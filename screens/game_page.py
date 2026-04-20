from __future__ import annotations

from dataclasses import dataclass

import pygame

from components.button import draw_outline_button
from components.modal_elements import (
    draw_backdrop,
    draw_decorated_panel,
    draw_language_box,
    draw_modal_button,
    draw_panel_header,
    draw_qr_placeholder,
    draw_sound_state_icon,
    draw_toggle_switch,
    wrap_text,
)
from components.setting_icon import draw_gear_icon
from config import BLACK, BORDER_PINK, WHITE
from core.AI import AI_DIFFICULTY_SETTINGS, get_ai_move
from core.board import (
    COLS,
    ROWS,
    board_full,
    create_board,
    drop_piece,
    get_next_open_row,
    is_valid_column,
)
from core.ui_fonts import get_ui_font


REFERENCE_SCREEN_WIDTH = 734
REFERENCE_SCREEN_HEIGHT = 680
REFERENCE_CELL_SIZE = 74
REFERENCE_BOARD_PADDING = 16
REFERENCE_SIDE_GUTTER = 92
REFERENCE_TOP_PANEL_HEIGHT = 92
REFERENCE_BOTTOM_PANEL_HEIGHT = 112

HUMAN_PLAYER = 1
AI_PLAYER = 2
EMPTY = 0

AI_THINK_DELAY_MS = 300
TURN_TIME_SECONDS = 120

BACKGROUND = (249, 249, 247)
PANEL = (255, 255, 255)
TEXT = (28, 30, 36)
SUBTEXT = (108, 114, 132)
BOARD_COLOR = (191, 53, 141)
BOARD_SHADOW = (227, 197, 216)
HOLE_COLOR = (250, 249, 246)
HUMAN_COLOR = (58, 102, 204)
AI_COLOR = (251, 238, 112)
ACCENT = (38, 42, 59)
TIMER_BG = (13, 13, 15)
TIMER_TEXT = (255, 255, 255)
FRAME_BORDER = (70, 95, 140)
DIALOG_OVERLAY = (16, 18, 24, 138)
DIALOG_BG = (255, 255, 255)
DIALOG_SHADOW = (214, 220, 231)
CANCEL_FILL = (244, 245, 248)
SUCCESS = (64, 148, 97)
WARNING = (200, 93, 93)


@dataclass(frozen=True)
class DifficultyConfig:
    label: str
    depth: int


DIFFICULTIES = {
    "easy": DifficultyConfig("Easy", AI_DIFFICULTY_SETTINGS["easy"]["depth"]),
    "medium": DifficultyConfig("Medium", AI_DIFFICULTY_SETTINGS["medium"]["depth"]),
    "hard": DifficultyConfig("Hard", AI_DIFFICULTY_SETTINGS["hard"]["depth"]),
}


class GamePage:
    def __init__(self, screen, preferences, difficulty="easy"):
        self.screen = screen
        self.preferences = preferences
        self.difficulty = difficulty
        self.game_mode = "ai"
        self.btn_home = None
        self.btn_restart = None
        self.btn_settings = None
        self.active_modal = None
        self.modal_parent = None
        self.settings_draft_language = self.preferences.language
        self.settings_draft_volume = self.preferences.volume_on
        self.settings_dropdown_open = False
        self.settings_buttons = {}
        self.about_exit_button = None
        self.donate_exit_button = None
        self.win_buttons = {}
        self.reset(difficulty)

    def reset(self, difficulty=None, game_mode=None):
        if difficulty is not None:
            self.difficulty = difficulty
        if game_mode is not None:
            self.game_mode = game_mode

        self.board = create_board()
        self.current_player = HUMAN_PLAYER
        self.game_over = False
        self.winner = EMPTY
        self.winning_line = None
        self.end_reason = "active"
        self.ai_turn_started_at = None
        self.human_time_left = float(TURN_TIME_SECONDS)
        self.ai_time_left = float(TURN_TIME_SECONDS)
        self.last_tick_ms = pygame.time.get_ticks()
        self.show_reset_confirmation = False
        self.active_modal = None
        self.modal_parent = None
        self.settings_dropdown_open = False
        self.reset_overlay_rects()

    def reset_overlay_rects(self):
        self.settings_buttons = {}
        self.about_exit_button = None
        self.donate_exit_button = None
        self.win_buttons = {}

    def sx(self, x):
        return int(x * self.screen.get_width() / 1440)

    def sy(self, y):
        return int(y * self.screen.get_height() / 1024)

    def sf(self, size):
        scale_w = self.screen.get_width() / 1440
        scale_h = self.screen.get_height() / 1024
        return max(16, int(size * min(scale_w, scale_h)))

    def make_centered_rect(self, width_ratio, height_ratio, top_ratio=None):
        width = int(self.screen.get_width() * width_ratio)
        height = int(self.screen.get_height() * height_ratio)
        x = (self.screen.get_width() - width) // 2
        y = (self.screen.get_height() - height) // 2 if top_ratio is None else int(self.screen.get_height() * top_ratio)
        return pygame.Rect(x, y, width, height)

    def draw(self):
        self._update_runtime_state()
        self.reset_overlay_rects()

        layout = self._compute_layout()
        mouse_pos = pygame.mouse.get_pos()
        hovered_column = self._get_hovered_column(mouse_pos, layout)

        self.screen.fill(BACKGROUND)
        self._draw_background(layout)
        self._draw_top_buttons(layout, mouse_pos)
        self._draw_side_panels(layout)
        self._draw_preview_disc(layout, hovered_column)
        self._draw_board(layout)
        self._draw_turn_panel(layout)

        if self.active_modal:
            draw_backdrop(self.screen, 128)
            if self.active_modal == "settings":
                self._draw_settings_modal(layout, mouse_pos)
            elif self.active_modal == "about":
                self._draw_about_modal()
            elif self.active_modal == "donate":
                self._draw_donate_modal()

        if self.game_over:
            draw_backdrop(self.screen, 146)
            self._draw_winner_popup(layout, mouse_pos)
        if self.show_reset_confirmation:
            self._draw_reset_confirmation(layout, mouse_pos)

    def handle_click(self, mouse_pos):
        layout = self._compute_layout()

        if self.show_reset_confirmation:
            rects = self._get_reset_dialog_rects(layout)
            if rects["confirm_button"].collidepoint(mouse_pos):
                self.reset()
            elif rects["cancel_button"].collidepoint(mouse_pos):
                self._close_reset_confirmation()
            return None

        if self.active_modal == "settings":
            self._handle_settings_click(layout, mouse_pos)
            return None
        if self.active_modal in {"about", "donate"}:
            self._handle_info_modal_click(mouse_pos)
            return None

        if self.game_over:
            rects = self._get_winner_popup_rects(layout)
            if rects["play_again_button"].collidepoint(mouse_pos):
                self.reset()
                return None
            if rects["exit_button"].collidepoint(mouse_pos):
                self.ai_turn_started_at = None
                return "home"
            return None

        if layout["restart_button"].collidepoint(mouse_pos):
            self._open_reset_confirmation()
            return None

        if layout["home_button"].collidepoint(mouse_pos):
            self.ai_turn_started_at = None
            return "home"

        if layout["settings_button"].collidepoint(mouse_pos):
            self._open_settings_modal()
            return None

        if self._is_ai_turn():
            return None

        column = self._get_hovered_column(mouse_pos, layout)
        if column is not None:
            self._apply_move(column, self.current_player)

        return None

    def _update_runtime_state(self):
        now = pygame.time.get_ticks()
        elapsed = (now - self.last_tick_ms) / 1000 if self.last_tick_ms is not None else 0
        self.last_tick_ms = now

        if self.show_reset_confirmation or self.active_modal:
            return

        if self.game_over:
            return

        if self.current_player == HUMAN_PLAYER:
            self.human_time_left = max(0.0, self.human_time_left - elapsed)
            if self.human_time_left == 0:
                self.game_over = True
                self.winner = self._other_player(HUMAN_PLAYER)
                self.end_reason = "timeout"
                return
        else:
            self.ai_time_left = max(0.0, self.ai_time_left - elapsed)
            if self.ai_time_left == 0:
                self.game_over = True
                self.winner = self._other_player(AI_PLAYER)
                self.end_reason = "timeout"
                return

        if not self._is_ai_turn():
            return

        if self.ai_turn_started_at is None:
            self.ai_turn_started_at = now
            return

        if now - self.ai_turn_started_at < AI_THINK_DELAY_MS:
            return

        column = get_ai_move(self.board, self.difficulty)
        if column is not None:
            self._apply_move(column, AI_PLAYER)
        self.ai_turn_started_at = None

    def _open_reset_confirmation(self):
        self.show_reset_confirmation = True
        if self._is_ai_turn():
            self.ai_turn_started_at = pygame.time.get_ticks()

    def _close_reset_confirmation(self):
        self.show_reset_confirmation = False
        self.last_tick_ms = pygame.time.get_ticks()
        if self._is_ai_turn():
            self.ai_turn_started_at = self.last_tick_ms

    def _open_settings_modal(self):
        self.active_modal = "settings"
        self.modal_parent = None
        self.settings_draft_language = self.preferences.language
        self.settings_draft_volume = self.preferences.volume_on
        self.settings_dropdown_open = False
        if self._is_ai_turn():
            self.ai_turn_started_at = pygame.time.get_ticks()

    def _close_settings_modal(self):
        self._close_active_modal()

    def _open_info_modal(self, modal_name):
        self.modal_parent = self.active_modal
        self.active_modal = modal_name
        self.settings_dropdown_open = False

    def _close_active_modal(self):
        self.active_modal = self.modal_parent
        self.modal_parent = None
        self.settings_dropdown_open = False
        self.last_tick_ms = pygame.time.get_ticks()
        if self._is_ai_turn():
            self.ai_turn_started_at = self.last_tick_ms

    def _apply_move(self, column, piece):
        if not is_valid_column(self.board, column):
            return

        row = get_next_open_row(self.board, column)
        if row is None:
            return

        drop_piece(self.board, row, column, piece)

        winning_line = self._find_winning_line(piece)
        if winning_line:
            self.game_over = True
            self.winning_line = winning_line
            self.winner = piece
            self.end_reason = "connect4"
            return

        if board_full(self.board):
            self.game_over = True
            self.winner = EMPTY
            self.winning_line = None
            self.end_reason = "draw"
            return

        self.current_player = self._other_player(piece)
        if self._is_ai_turn():
            self.ai_turn_started_at = pygame.time.get_ticks()
        else:
            self.ai_turn_started_at = None

    def _find_winning_line(self, player):
        for row in range(ROWS):
            for col in range(COLS - 3):
                coords = [(row, col + offset) for offset in range(4)]
                if all(self.board[r][c] == player for r, c in coords):
                    return coords

        for row in range(ROWS - 3):
            for col in range(COLS):
                coords = [(row + offset, col) for offset in range(4)]
                if all(self.board[r][c] == player for r, c in coords):
                    return coords

        for row in range(ROWS - 3):
            for col in range(COLS - 3):
                coords = [(row + offset, col + offset) for offset in range(4)]
                if all(self.board[r][c] == player for r, c in coords):
                    return coords

        for row in range(3, ROWS):
            for col in range(COLS - 3):
                coords = [(row - offset, col + offset) for offset in range(4)]
                if all(self.board[r][c] == player for r, c in coords):
                    return coords

        return None

    def _compute_layout(self):
        screen_width, screen_height = self.screen.get_size()
        scale = min(
            (screen_width - 24) / REFERENCE_SCREEN_WIDTH,
            (screen_height - 24) / REFERENCE_SCREEN_HEIGHT,
        )
        scale = max(0.68, min(scale, 1.55))

        cell_size = max(52, int(REFERENCE_CELL_SIZE * scale))
        board_padding = max(10, int(REFERENCE_BOARD_PADDING * scale))
        side_gutter = max(70, int(REFERENCE_SIDE_GUTTER * scale))
        top_panel_height = max(72, int(REFERENCE_TOP_PANEL_HEIGHT * scale))
        bottom_panel_height = max(86, int(REFERENCE_BOTTOM_PANEL_HEIGHT * scale))
        icon_size = max(36, int(40 * scale))
        icon_gap = max(8, int(8 * scale))

        board_width = COLS * cell_size
        board_height = ROWS * cell_size
        board_frame_width = board_width + (board_padding * 2)
        board_frame_height = board_height + (board_padding * 2)

        total_content_height = top_panel_height + board_frame_height + bottom_panel_height
        content_top = max(0, (screen_height - total_content_height) // 2)
        board_x = max(20, (screen_width - board_frame_width) // 2)
        board_y = content_top + top_panel_height
        board_frame = pygame.Rect(board_x, board_y, board_frame_width, board_frame_height)

        icon_y = content_top + max(6, int(18 * scale))
        icon_group_width = icon_size * 3 + icon_gap * 2
        icon_start_x = (screen_width - icon_group_width) // 2
        restart_button = pygame.Rect(icon_start_x, icon_y, icon_size, icon_size)
        home_button = pygame.Rect(icon_start_x + icon_size + icon_gap, icon_y, icon_size, icon_size)
        settings_button = pygame.Rect(icon_start_x + (icon_size + icon_gap) * 2, icon_y, icon_size, icon_size)

        marker_y = board_frame.centery - max(18, int(40 * scale))
        marker_offset = max(28, side_gutter // 2)
        human_marker_center = (board_frame.left - marker_offset, marker_y)
        ai_marker_center = (board_frame.right + marker_offset, marker_y)

        timer_width = max(84, int(88 * scale))
        timer_height = max(40, int(48 * scale))
        timer_y = min(
            screen_height - timer_height - max(10, int(12 * scale)),
            board_frame.bottom - timer_height + max(14, int(18 * scale)),
        )
        human_timer = pygame.Rect(
            human_marker_center[0] - (timer_width // 2),
            timer_y,
            timer_width,
            timer_height,
        )
        ai_timer = pygame.Rect(
            ai_marker_center[0] - (timer_width // 2),
            timer_y,
            timer_width,
            timer_height,
        )

        turn_panel_width = max(180, int(188 * scale))
        turn_panel_height = max(46, int(52 * scale))
        turn_panel = pygame.Rect(
            (screen_width - turn_panel_width) // 2,
            board_frame.bottom + max(18, int(18 * scale)),
            turn_panel_width,
            turn_panel_height,
        )

        preview_y = board_frame.top - max(18, int(22 * scale))
        margin = max(6, int(10 * scale))
        outer_frame = pygame.Rect(
            margin,
            margin,
            screen_width - (margin * 2),
            screen_height - (margin * 2),
        )

        return {
            "scale": scale,
            "screen_width": screen_width,
            "screen_height": screen_height,
            "cell_size": cell_size,
            "board_padding": board_padding,
            "board_frame": board_frame,
            "cell_origin": (board_frame.left + board_padding, board_frame.top + board_padding),
            "restart_button": restart_button,
            "home_button": home_button,
            "settings_button": settings_button,
            "human_marker_center": human_marker_center,
            "ai_marker_center": ai_marker_center,
            "human_timer": human_timer,
            "ai_timer": ai_timer,
            "turn_panel": turn_panel,
            "preview_y": preview_y,
            "outer_frame": outer_frame,
        }

    def _get_hovered_column(self, mouse_pos, layout):
        origin_x, origin_y = layout["cell_origin"]
        x, y = mouse_pos
        board_width = COLS * layout["cell_size"]
        board_height = ROWS * layout["cell_size"]

        if not (origin_x <= x <= origin_x + board_width):
            return None
        if not (layout["preview_y"] - layout["cell_size"] <= y <= origin_y + board_height):
            return None

        column = int((x - origin_x) // layout["cell_size"])
        if not is_valid_column(self.board, column):
            return None
        return column

    def _draw_background(self, layout):
        pygame.draw.rect(self.screen, PANEL, layout["outer_frame"], border_radius=max(16, int(12 * layout["scale"])))
        pygame.draw.rect(
            self.screen,
            FRAME_BORDER,
            layout["outer_frame"],
            width=max(2, int(2 * layout["scale"])),
            border_radius=max(16, int(12 * layout["scale"])),
        )

    def _draw_top_buttons(self, layout, mouse_pos):
        self.btn_restart = layout["restart_button"]
        self.btn_home = layout["home_button"]
        self.btn_settings = layout["settings_button"]

        self._draw_icon_button(layout["restart_button"], mouse_pos, "restart")
        self._draw_icon_button(layout["home_button"], mouse_pos, "home")
        self._draw_icon_button(layout["settings_button"], mouse_pos, "settings")

    def _draw_icon_button(self, rect, mouse_pos, icon_name):
        hovered = rect.collidepoint(mouse_pos)
        fill = (244, 244, 240) if hovered else PANEL
        outline = BORDER_PINK if icon_name == "settings" else ACCENT
        pygame.draw.ellipse(self.screen, fill, rect.inflate(10, 10))
        pygame.draw.ellipse(self.screen, outline, rect.inflate(10, 10), 2)

        if icon_name == "home":
            self._draw_home_icon(rect.center, rect.width)
        elif icon_name == "restart":
            self._draw_restart_icon(rect.center, rect.width)
        else:
            draw_gear_icon(
                self.screen,
                rect.centerx,
                rect.centery,
                outer_r=max(12, rect.width // 2 - 6),
                inner_r=max(5, rect.width // 7),
            )

    def _draw_home_icon(self, center, icon_size):
        cx, cy = center
        roof_offset = max(8, icon_size // 3)
        body_width = max(14, icon_size // 2)
        body_height = max(12, icon_size // 2)
        door_width = max(4, icon_size // 8)
        door_height = max(7, icon_size // 5)

        roof = [(cx - roof_offset, cy + 2), (cx, cy - roof_offset), (cx + roof_offset, cy + 2)]
        base = pygame.Rect(cx - (body_width // 2), cy + 2, body_width, body_height)
        door = pygame.Rect(cx - (door_width // 2), cy + body_height // 4, door_width, door_height)

        pygame.draw.lines(self.screen, TEXT, False, roof, 3)
        pygame.draw.rect(self.screen, TEXT, base, 3)
        pygame.draw.rect(self.screen, TEXT, door, 2)

    def _draw_restart_icon(self, center, icon_size):
        cx, cy = center
        radius = max(9, icon_size // 3)
        width = max(2, icon_size // 11)
        pygame.draw.arc(
            self.screen,
            TEXT,
            (cx - radius, cy - radius, radius * 2, radius * 2),
            0.8,
            5.5,
            width,
        )
        arrow = [
            (cx + radius - 2, cy - radius + 2),
            (cx + radius + max(4, icon_size // 8), cy - radius + 4),
            (cx + radius - 1, cy - radius + max(8, icon_size // 5)),
        ]
        pygame.draw.polygon(self.screen, TEXT, arrow)

    def _draw_side_panels(self, layout):
        active_human = self.current_player == HUMAN_PLAYER and not self.game_over
        active_ai = self.current_player == AI_PLAYER and not self.game_over

        self._draw_player_marker(layout["human_marker_center"], HUMAN_COLOR, active_human, layout["scale"])
        self._draw_player_marker(layout["ai_marker_center"], AI_COLOR, active_ai, layout["scale"])
        self._draw_side_label(layout["human_marker_center"], self._left_player_label(), layout["scale"])
        self._draw_side_label(layout["ai_marker_center"], self._right_player_label(), layout["scale"])
        self._draw_timer_box(layout["human_timer"], self.human_time_left)
        self._draw_timer_box(layout["ai_timer"], self.ai_time_left)

    def _draw_player_marker(self, center, fill, active, scale):
        radius = max(28, int(34 * scale))
        outline = ACCENT if active else PANEL
        width = 4 if active else 2
        pygame.draw.circle(self.screen, fill, center, radius)
        pygame.draw.circle(self.screen, outline, center, radius, width)

    def _draw_side_label(self, center, label, scale):
        font = pygame.font.SysFont("consolas", max(13, int(16 * scale)), bold=True)
        text_surface = font.render(label, True, SUBTEXT)
        text_rect = text_surface.get_rect(center=(center[0], center[1] + max(48, int(50 * scale))))
        self.screen.blit(text_surface, text_rect)

    def _draw_timer_box(self, rect, seconds_left):
        pygame.draw.rect(self.screen, TIMER_BG, rect, border_radius=10)
        font = pygame.font.SysFont("consolas", max(18, int(rect.height * 0.45)), bold=True)
        time_surface = font.render(self._format_time(seconds_left), True, TIMER_TEXT)
        self.screen.blit(time_surface, time_surface.get_rect(center=rect.center))

    def _draw_preview_disc(self, layout, hovered_column):
        if self.game_over or hovered_column is None or self._is_ai_turn():
            return

        origin_x, _ = layout["cell_origin"]
        center_x = origin_x + (hovered_column * layout["cell_size"]) + (layout["cell_size"] // 2)
        radius = max(16, (layout["cell_size"] // 2) - max(8, int(10 * layout["scale"])))
        center = (center_x, layout["preview_y"])
        pygame.draw.circle(self.screen, self._color_for_player(self.current_player), center, radius)
        pygame.draw.circle(self.screen, ACCENT, center, radius, 2)

    def _draw_board(self, layout):
        shadow_rect = layout["board_frame"].move(0, max(4, int(6 * layout["scale"])))
        pygame.draw.rect(self.screen, BOARD_SHADOW, shadow_rect, border_radius=max(18, int(26 * layout["scale"])))
        pygame.draw.rect(self.screen, BOARD_COLOR, layout["board_frame"], border_radius=max(18, int(26 * layout["scale"])))

        highlighted = set(self.winning_line or [])
        radius = max(16, (layout["cell_size"] // 2) - max(8, int(10 * layout["scale"])))

        for row in range(ROWS):
            for col in range(COLS):
                center = self._get_cell_center(row, col, layout)
                piece = self.board[row][col]

                color = HOLE_COLOR
                if piece == HUMAN_PLAYER:
                    color = HUMAN_COLOR
                elif piece == AI_PLAYER:
                    color = AI_COLOR

                pygame.draw.circle(self.screen, color, center, radius)

                if (row, col) in highlighted:
                    pygame.draw.circle(self.screen, WHITE, center, radius, 5)
                elif piece != EMPTY:
                    pygame.draw.circle(self.screen, ACCENT, center, radius, 2)

    def _draw_turn_panel(self, layout):
        difficulty = DIFFICULTIES.get(self.difficulty, DIFFICULTIES["medium"])
        turn_font = pygame.font.SysFont("segoeui", max(16, int(18 * layout["scale"])), bold=True)
        small_font = pygame.font.SysFont("consolas", max(12, int(15 * layout["scale"])), bold=True)

        glow_color = self._get_turn_glow_color()
        panel_fill = self._get_turn_panel_fill_color()
        self._draw_panel_glow(layout["turn_panel"], glow_color, layout["scale"])

        pygame.draw.rect(self.screen, panel_fill, layout["turn_panel"], border_radius=10)
        pygame.draw.rect(
            self.screen,
            glow_color,
            layout["turn_panel"],
            width=max(2, int(2 * layout["scale"])),
            border_radius=10,
        )

        if self.game_over:
            if self.winner == HUMAN_PLAYER:
                label = self.preferences.text("turn_blue_wins")
            elif self.winner == AI_PLAYER:
                label = self.preferences.text("turn_yellow_wins")
            else:
                label = self.preferences.text("turn_draw")
        elif self.current_player == HUMAN_PLAYER:
            label = self.preferences.text("turn_blue")
        else:
            label = self.preferences.text("turn_yellow")

        label_surface = turn_font.render(label, True, TEXT)
        self.screen.blit(label_surface, label_surface.get_rect(center=layout["turn_panel"].center))

        if self.end_reason == "timeout":
            footer_label = self.preferences.text("footer_timeout")
            footer_color = WARNING
        elif self.end_reason == "connect4":
            footer_label = self.preferences.text("footer_connect4")
            footer_color = SUCCESS if self.winner == HUMAN_PLAYER else WARNING
        elif self.end_reason == "draw":
            footer_label = self.preferences.text("footer_draw")
            footer_color = SUBTEXT
        elif self.game_mode == "pvp":
            footer_label = self.preferences.text("footer_two_players")
            footer_color = SUBTEXT
        else:
            footer_label = self.preferences.format("footer_depth", depth=difficulty.depth)
            footer_color = SUBTEXT

        footer_surface = small_font.render(footer_label, True, footer_color)
        footer_y = min(
            layout["screen_height"] - max(18, int(24 * layout["scale"])),
            layout["turn_panel"].bottom + max(18, int(24 * layout["scale"])),
        )
        self.screen.blit(
            footer_surface,
            footer_surface.get_rect(center=(layout["screen_width"] // 2, footer_y)),
        )

    def _get_reset_dialog_rects(self, layout):
        dialog_width = max(300, int(340 * layout["scale"]))
        dialog_height = max(190, int(210 * layout["scale"]))
        dialog = pygame.Rect(
            (layout["screen_width"] - dialog_width) // 2,
            (layout["screen_height"] - dialog_height) // 2,
            dialog_width,
            dialog_height,
        )

        button_width = max(108, int(122 * layout["scale"]))
        button_height = max(42, int(46 * layout["scale"]))
        gap = max(10, int(14 * layout["scale"]))
        button_y = dialog.bottom - button_height - max(18, int(22 * layout["scale"]))
        cancel_button = pygame.Rect(
            dialog.centerx - gap - button_width,
            button_y,
            button_width,
            button_height,
        )
        confirm_button = pygame.Rect(
            dialog.centerx + gap,
            button_y,
            button_width,
            button_height,
        )

        return {
            "dialog": dialog,
            "cancel_button": cancel_button,
            "confirm_button": confirm_button,
        }

    def _draw_reset_confirmation(self, layout, mouse_pos):
        overlay = pygame.Surface((layout["screen_width"], layout["screen_height"]), pygame.SRCALPHA)
        overlay.fill(DIALOG_OVERLAY)
        self.screen.blit(overlay, (0, 0))

        rects = self._get_reset_dialog_rects(layout)
        dialog = rects["dialog"]
        shadow = dialog.move(0, max(6, int(8 * layout["scale"])))

        pygame.draw.rect(self.screen, DIALOG_SHADOW, shadow, border_radius=18)
        pygame.draw.rect(self.screen, DIALOG_BG, dialog, border_radius=18)
        pygame.draw.rect(self.screen, FRAME_BORDER, dialog, width=2, border_radius=18)

        title_font = pygame.font.SysFont("georgia", max(20, int(24 * layout["scale"])), bold=True)
        body_font = pygame.font.SysFont("segoeui", max(15, int(17 * layout["scale"])))

        title_surface = title_font.render(self.preferences.text("reset_title"), True, TEXT)
        self.screen.blit(title_surface, title_surface.get_rect(center=(dialog.centerx, dialog.top + max(34, int(40 * layout["scale"])))))

        body_width = dialog.width - max(42, int(48 * layout["scale"]))
        lines = wrap_text(self.preferences.text("reset_body"), body_font, body_width)
        body_y = dialog.top + max(68, int(78 * layout["scale"]))
        for line in lines:
            surface = body_font.render(line, True, SUBTEXT)
            self.screen.blit(surface, surface.get_rect(center=(dialog.centerx, body_y)))
            body_y += surface.get_height() + max(2, int(3 * layout["scale"]))

        draw_modal_button(
            self.screen,
            rects["cancel_button"],
            self.preferences.text("reset_keep"),
            hovered=rects["cancel_button"].collidepoint(mouse_pos),
            fill_color=CANCEL_FILL,
            border_color=FRAME_BORDER,
            font_size=max(15, int(17 * layout["scale"])),
        )
        draw_modal_button(
            self.screen,
            rects["confirm_button"],
            self.preferences.text("reset_confirm"),
            hovered=rects["confirm_button"].collidepoint(mouse_pos),
            fill_color=WARNING,
            border_color=WARNING,
            text_color=PANEL,
            font_size=max(15, int(17 * layout["scale"])),
        )

    def _draw_settings_modal(self, layout, mouse_pos):
        panel_rect = self.make_centered_rect(0.58, 0.74, 0.10)
        draw_decorated_panel(
            self.screen,
            panel_rect,
            outer_width=max(3, self.sx(4)),
            inner_margin=max(16, self.sx(20)),
            inner_width=max(2, self.sx(2)),
        )
        header_font = get_ui_font(self.sf(42), bold=True)
        draw_panel_header(self.screen, panel_rect, self.preferences.text("settings_title"), header_font)

        label_font = get_ui_font(self.sf(18), bold=True)
        icon_center = (panel_rect.left + int(panel_rect.w * 0.20), panel_rect.top + int(panel_rect.h * 0.30))
        draw_sound_state_icon(self.screen, icon_center, max(40, panel_rect.w // 11), self.settings_draft_volume)

        volume_label = label_font.render(self.preferences.text("settings_volume"), True, BLACK)
        volume_label_rect = volume_label.get_rect(midleft=(panel_rect.left + int(panel_rect.w * 0.30), panel_rect.top + int(panel_rect.h * 0.24)))
        self.screen.blit(volume_label, volume_label_rect)

        volume_rect = pygame.Rect(
            panel_rect.left + int(panel_rect.w * 0.30),
            panel_rect.top + int(panel_rect.h * 0.28),
            int(panel_rect.w * 0.20),
            int(panel_rect.h * 0.08),
        )
        draw_toggle_switch(self.screen, volume_rect, self.settings_draft_volume)
        self.settings_buttons["volume"] = volume_rect

        language_label = label_font.render(self.preferences.text("settings_language"), True, BLACK)
        language_label_rect = language_label.get_rect(midleft=(panel_rect.left + int(panel_rect.w * 0.55), panel_rect.top + int(panel_rect.h * 0.24)))
        self.screen.blit(language_label, language_label_rect)

        language_rect = pygame.Rect(
            panel_rect.left + int(panel_rect.w * 0.55),
            panel_rect.top + int(panel_rect.h * 0.26),
            int(panel_rect.w * 0.28),
            int(panel_rect.h * 0.10),
        )
        language_font = get_ui_font(self.sf(20), bold=False)
        draw_language_box(
            self.screen,
            language_rect,
            self.preferences.language_label(self.settings_draft_language).upper(),
            language_font,
        )
        self.settings_buttons["language_box"] = language_rect

        button_width = int(panel_rect.w * 0.32)
        button_height = int(panel_rect.h * 0.12)
        left_x = panel_rect.left + int(panel_rect.w * 0.12)
        right_x = panel_rect.right - button_width - int(panel_rect.w * 0.12)
        top_row_y = panel_rect.top + int(panel_rect.h * 0.56)
        bottom_row_y = panel_rect.top + int(panel_rect.h * 0.74)
        button_font_size = self.sf(28)

        self.settings_buttons["about"] = draw_outline_button(
            self.screen,
            left_x,
            top_row_y,
            button_width,
            button_height,
            self.preferences.text("about_title"),
            button_font_size,
        )
        self.settings_buttons["donate"] = draw_outline_button(
            self.screen,
            right_x,
            top_row_y,
            button_width,
            button_height,
            self.preferences.text("donate_title"),
            button_font_size,
        )
        self.settings_buttons["save"] = draw_outline_button(
            self.screen,
            left_x,
            bottom_row_y,
            button_width,
            button_height,
            self.preferences.text("save"),
            button_font_size,
        )
        self.settings_buttons["exit"] = draw_outline_button(
            self.screen,
            right_x,
            bottom_row_y,
            button_width,
            button_height,
            self.preferences.text("exit"),
            button_font_size,
        )

        if self.settings_dropdown_open:
            option_height = int(language_rect.h * 0.86)
            dropdown_rect = pygame.Rect(
                language_rect.left,
                language_rect.bottom + self.sy(6),
                language_rect.w,
                option_height * 2,
            )
            pygame.draw.rect(self.screen, WHITE, dropdown_rect, border_radius=max(10, dropdown_rect.h // 6))
            pygame.draw.rect(
                self.screen,
                BORDER_PINK,
                dropdown_rect,
                width=max(2, self.sx(2)),
                border_radius=max(10, dropdown_rect.h // 6),
            )

            option_font = get_ui_font(self.sf(20), bold=True)
            for index, code in enumerate(("en", "vi")):
                rect = pygame.Rect(
                    dropdown_rect.left,
                    dropdown_rect.top + option_height * index,
                    dropdown_rect.w,
                    option_height,
                )
                if code == self.settings_draft_language:
                    pygame.draw.rect(self.screen, (255, 245, 250), rect)
                if index > 0:
                    pygame.draw.line(
                        self.screen,
                        BORDER_PINK,
                        (rect.left, rect.top),
                        (rect.right, rect.top),
                        max(1, self.sx(1)),
                    )
                option_text = option_font.render(self.preferences.language_label(code), True, BLACK)
                option_text_rect = option_text.get_rect(center=rect.center)
                self.screen.blit(option_text, option_text_rect)
                self.settings_buttons[f"language_{code}"] = rect

    def _draw_about_modal(self):
        panel_rect = self.make_centered_rect(0.68, 0.68, 0.08)
        draw_decorated_panel(
            self.screen,
            panel_rect,
            outer_width=max(3, self.sx(4)),
            inner_margin=max(16, self.sx(20)),
            inner_width=max(2, self.sx(2)),
        )
        header_font = get_ui_font(self.sf(42), bold=True)
        draw_panel_header(self.screen, panel_rect, self.preferences.text("about_title"), header_font)

        title_font = get_ui_font(self.sf(28), bold=True)
        body_font = get_ui_font(self.sf(24), bold=True)
        highlight_font = get_ui_font(self.sf(26), bold=True)

        y = panel_rect.top + int(panel_rect.h * 0.24)

        intro_lines = wrap_text(title_font, self.preferences.text("about_intro"), int(panel_rect.w * 0.80))
        for line in intro_lines:
            label = title_font.render(line, True, BLACK)
            rect = label.get_rect(center=(panel_rect.centerx, y))
            self.screen.blit(label, rect)
            y += label.get_height() + self.sy(10)

        y += self.sy(12)
        for name in self.preferences.lines("about_names"):
            label = body_font.render(name, True, BLACK)
            rect = label.get_rect(center=(panel_rect.centerx, y))
            self.screen.blit(label, rect)
            y += label.get_height() + self.sy(14)

        y += self.sy(20)
        for line in wrap_text(highlight_font, self.preferences.text("about_highlight"), int(panel_rect.w * 0.86)):
            label = highlight_font.render(line, True, (255, 42, 42))
            rect = label.get_rect(center=(panel_rect.centerx, y))
            self.screen.blit(label, rect)
            y += label.get_height() + self.sy(10)

        creator = highlight_font.render(self.preferences.text("about_creator"), True, (255, 42, 42))
        creator_rect = creator.get_rect(center=(panel_rect.centerx, y + self.sy(6)))
        self.screen.blit(creator, creator_rect)

        button_width = max(130, panel_rect.w // 5)
        button_height = max(58, panel_rect.h // 10)
        button_x = panel_rect.centerx - button_width // 2
        button_y = panel_rect.bottom - button_height - self.sy(42)
        self.about_exit_button = draw_outline_button(
            self.screen,
            button_x,
            button_y,
            button_width,
            button_height,
            self.preferences.text("exit"),
            self.sf(28),
        )

    def _draw_donate_modal(self):
        panel_rect = self.make_centered_rect(0.64, 0.66, 0.08)
        draw_decorated_panel(
            self.screen,
            panel_rect,
            outer_width=max(3, self.sx(4)),
            inner_margin=max(16, self.sx(20)),
            inner_width=max(2, self.sx(2)),
        )
        header_font = get_ui_font(self.sf(42), bold=True)
        draw_panel_header(self.screen, panel_rect, self.preferences.text("donate_title"), header_font)

        qr_size = int(min(panel_rect.w * 0.50, panel_rect.h * 0.48))
        qr_rect = pygame.Rect(0, 0, qr_size, qr_size)
        qr_rect.center = (panel_rect.centerx, panel_rect.top + int(panel_rect.h * 0.44))
        draw_qr_placeholder(self.screen, qr_rect)

        button_width = max(130, panel_rect.w // 5)
        button_height = max(58, panel_rect.h // 10)
        button_x = panel_rect.centerx - button_width // 2
        button_y = panel_rect.bottom - button_height - self.sy(42)
        self.donate_exit_button = draw_outline_button(
            self.screen,
            button_x,
            button_y,
            button_width,
            button_height,
            self.preferences.text("exit"),
            self.sf(28),
        )

    def _handle_settings_click(self, layout, mouse_pos):
        if self.settings_dropdown_open:
            for code in ("en", "vi"):
                rect = self.settings_buttons.get(f"language_{code}")
                if rect and rect.collidepoint(mouse_pos):
                    self.settings_draft_language = code
                    self.settings_dropdown_open = False
                    return None

        language_box = self.settings_buttons.get("language_box")
        if language_box and language_box.collidepoint(mouse_pos):
            self.settings_dropdown_open = not self.settings_dropdown_open
            return None

        if self.settings_dropdown_open:
            self.settings_dropdown_open = False

        if self.settings_buttons.get("volume") and self.settings_buttons["volume"].collidepoint(mouse_pos):
            self.settings_draft_volume = not self.settings_draft_volume
            return None

        if self.settings_buttons.get("about") and self.settings_buttons["about"].collidepoint(mouse_pos):
            self._open_info_modal("about")
            return None

        if self.settings_buttons.get("donate") and self.settings_buttons["donate"].collidepoint(mouse_pos):
            self._open_info_modal("donate")
            return None

        if self.settings_buttons.get("save") and self.settings_buttons["save"].collidepoint(mouse_pos):
            self.preferences.set_language(self.settings_draft_language)
            self.preferences.set_volume(self.settings_draft_volume)
            self.preferences.save()
            self._close_settings_modal()
            return None

        if self.settings_buttons.get("exit") and self.settings_buttons["exit"].collidepoint(mouse_pos):
            self._close_settings_modal()
            return None

        return None

    def _handle_info_modal_click(self, mouse_pos):
        if self.active_modal == "about":
            if self.about_exit_button and self.about_exit_button.collidepoint(mouse_pos):
                self._close_active_modal()
            return None

        if self.active_modal == "donate":
            if self.donate_exit_button and self.donate_exit_button.collidepoint(mouse_pos):
                self._close_active_modal()
            return None

        return None

    def _get_winner_popup_rects(self, layout):
        dialog = self.make_centered_rect(0.31, 0.52, 0.18)

        button_width = int(dialog.w * 0.34)
        button_height = int(dialog.h * 0.14)
        gap = int(dialog.w * 0.12)
        button_y = dialog.bottom - int(dialog.h * 0.22)
        play_again_button = pygame.Rect(
            dialog.centerx - gap - button_width,
            button_y,
            button_width,
            button_height,
        )
        exit_button = pygame.Rect(
            dialog.centerx + gap,
            button_y,
            button_width,
            button_height,
        )

        return {
            "dialog": dialog,
            "play_again_button": play_again_button,
            "exit_button": exit_button,
        }

    def _draw_winner_popup(self, layout, mouse_pos):
        rects = self._get_winner_popup_rects(layout)
        dialog = rects["dialog"]

        draw_backdrop(self.screen, alpha=146)
        draw_decorated_panel(
            self.screen,
            dialog,
            outer_width=max(2, self.sx(3)),
            inner_margin=max(14, self.sx(18)),
            inner_width=max(1, self.sx(2)),
        )

        title_font = get_ui_font(self.sf(28), bold=True)
        big_font = pygame.font.SysFont("arialblack", self.sf(92), bold=True)
        button_font_size = self.sf(22 if self.preferences.language == "vi" else 24)

        title_surface = title_font.render(self._popup_title(), True, TEXT)
        title_y = dialog.top + int(dialog.h * 0.15)
        word_y = dialog.top + int(dialog.h * 0.48)

        self.screen.blit(title_surface, title_surface.get_rect(center=(dialog.centerx, title_y)))
        self._draw_outlined_text(
            self._popup_word(),
            big_font,
            self._popup_word_color(),
            (98, 73, 155),
            (dialog.centerx, word_y),
            max(2, self.sx(4)),
        )

        draw_modal_button(
            self.screen,
            rects["play_again_button"],
            self.preferences.text("play_again"),
            hovered=rects["play_again_button"].collidepoint(mouse_pos),
            fill_color=WHITE,
            border_color=BORDER_PINK,
            text_color=BLACK,
            font_size=button_font_size,
        )
        draw_modal_button(
            self.screen,
            rects["exit_button"],
            self.preferences.text("exit"),
            hovered=rects["exit_button"].collidepoint(mouse_pos),
            fill_color=WHITE,
            border_color=BORDER_PINK,
            text_color=BLACK,
            font_size=button_font_size,
        )

    def _draw_outlined_text(self, text, font, fill_color, outline_color, center, outline_width=3):
        outline_surface = font.render(text, True, outline_color)
        fill_surface = font.render(text, True, fill_color)

        offsets = [
            (-outline_width, 0),
            (outline_width, 0),
            (0, -outline_width),
            (0, outline_width),
            (-outline_width, -outline_width),
            (outline_width, outline_width),
            (-outline_width, outline_width),
            (outline_width, -outline_width),
        ]
        for dx, dy in offsets:
            outline_rect = outline_surface.get_rect(center=(center[0] + dx, center[1] + dy))
            self.screen.blit(outline_surface, outline_rect)

        fill_rect = fill_surface.get_rect(center=center)
        self.screen.blit(fill_surface, fill_rect)

    def _get_cell_center(self, row, col, layout):
        origin_x, origin_y = layout["cell_origin"]
        center_x = origin_x + (col * layout["cell_size"]) + (layout["cell_size"] // 2)
        center_y = origin_y + (row * layout["cell_size"]) + (layout["cell_size"] // 2)
        return center_x, center_y

    def _format_time(self, seconds_left):
        total_seconds = max(0, int(seconds_left))
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def _get_turn_glow_color(self):
        if self.game_over:
            if self.winner == HUMAN_PLAYER:
                return HUMAN_COLOR
            if self.winner == AI_PLAYER:
                return AI_COLOR
            return SUBTEXT

        return self._color_for_player(self.current_player)

    def _get_turn_panel_fill_color(self):
        return self._get_turn_glow_color()

    def _draw_panel_glow(self, rect, color, scale):
        glow_size = max(12, int(18 * scale))
        glow_surface = pygame.Surface(
            (rect.width + glow_size * 2, rect.height + glow_size * 2),
            pygame.SRCALPHA,
        )

        layers = [
            (glow_size, 34),
            (max(8, int(glow_size * 0.72)), 54),
            (max(4, int(glow_size * 0.42)), 84),
        ]

        for inflate, alpha in layers:
            glow_rect = pygame.Rect(
                glow_size - inflate,
                glow_size - inflate,
                rect.width + inflate * 2,
                rect.height + inflate * 2,
            )
            pygame.draw.rect(
                glow_surface,
                (*color, alpha),
                glow_rect,
                border_radius=max(12, rect.height // 2),
            )

        self.screen.blit(glow_surface, (rect.x - glow_size, rect.y - glow_size))

    def _other_player(self, player):
        return AI_PLAYER if player == HUMAN_PLAYER else HUMAN_PLAYER

    def _is_ai_turn(self):
        return self.game_mode == "ai" and self.current_player == AI_PLAYER and not self.game_over

    def _color_for_player(self, player):
        return HUMAN_COLOR if player == HUMAN_PLAYER else AI_COLOR

    def _left_player_label(self):
        return self.preferences.text("player_you") if self.game_mode == "ai" else self.preferences.text("player_one")

    def _right_player_label(self):
        return self.preferences.text("player_ai") if self.game_mode == "ai" else self.preferences.text("player_two")

    def _popup_title(self):
        if self.winner == HUMAN_PLAYER:
            return self.preferences.text("winner_blue")
        if self.winner == AI_PLAYER:
            return self.preferences.text("winner_yellow")
        return self.preferences.text("winner_draw")

    def _popup_word(self):
        if self.winner == EMPTY:
            return self.preferences.text("winner_popup_draw")
        return self.preferences.text("winner_popup_win")

    def _popup_word_color(self):
        if self.winner == HUMAN_PLAYER:
            return HUMAN_COLOR
        if self.winner == AI_PLAYER:
            return (242, 197, 72)
        return (164, 164, 176)

    def _popup_reason(self):
        if self.end_reason == "timeout":
            return self.preferences.text("winner_reason_timeout")
        if self.end_reason == "draw":
            return self.preferences.text("winner_reason_draw")
        return self.preferences.text("winner_reason_connect4")
