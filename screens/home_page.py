import pygame

from components.board_view import draw_home_board
from components.button import draw_filled_button
from components.modal_elements import (
    draw_backdrop,
    draw_decorated_panel,
    draw_modal_button,
    draw_option_pill,
    wrap_text,
)
from components.setting_icon import draw_gear_icon
from config import BASE_HEIGHT, BASE_WIDTH, BG_COLOR, BLACK, TEAM_FONT_SIZE, TITLE_FONT_SIZE


class HomePage:
    def __init__(self, screen, preferences):
        self.screen = screen
        self.preferences = preferences
        self.btn_1player = None
        self.btn_2players = None
        self.btn_rules = None
        self.btn_quit = None
        self.btn_settings = None
        self.modal = None

    def sx(self, x):
        return int(x * self.screen.get_width() / BASE_WIDTH)

    def sy(self, y):
        return int(y * self.screen.get_height() / BASE_HEIGHT)

    def sf(self, size):
        scale_w = self.screen.get_width() / BASE_WIDTH
        scale_h = self.screen.get_height() / BASE_HEIGHT
        return max(16, int(size * min(scale_w, scale_h)))

    def draw_title(self):
        font = pygame.font.SysFont("timesnewroman", self.sf(TITLE_FONT_SIZE), bold=True)
        title = font.render(self.preferences.text("app_title"), True, BLACK)
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, self.sy(88)))
        self.screen.blit(title, title_rect)

    def draw_buttons(self):
        button_font = self.sf(42 if self.preferences.language == "en" else 34)
        self.btn_1player = draw_filled_button(
            self.screen,
            self.sx(123),
            self.sy(270),
            self.sx(343),
            self.sy(103),
            self.preferences.text("one_player"),
            button_font,
        )
        self.btn_2players = draw_filled_button(
            self.screen,
            self.sx(123),
            self.sy(408),
            self.sx(343),
            self.sy(103),
            self.preferences.text("two_players"),
            button_font,
        )
        self.btn_rules = draw_filled_button(
            self.screen,
            self.sx(123),
            self.sy(565),
            self.sx(343),
            self.sy(103),
            self.preferences.text("rules"),
            button_font,
        )
        self.btn_quit = draw_filled_button(
            self.screen,
            self.sx(123),
            self.sy(715),
            self.sx(343),
            self.sy(103),
            self.preferences.text("quit"),
            button_font,
        )

    def draw_team_name(self):
        font = pygame.font.SysFont("timesnewroman", self.sf(TEAM_FONT_SIZE), bold=True)
        team_text = font.render(self.preferences.text("team_name"), True, BLACK)
        text_rect = team_text.get_rect(bottomright=(self.sx(1330), self.sy(980)))
        self.screen.blit(team_text, text_rect)

    def draw_settings_button(self):
        size = max(66, self.sx(96))
        self.btn_settings = pygame.Rect(self.sx(44), self.sy(890), size, size)
        hovered = self.btn_settings.collidepoint(pygame.mouse.get_pos())

        fill = (255, 255, 255) if hovered else (248, 244, 247)
        border = (244, 180, 215)
        pygame.draw.ellipse(self.screen, fill, self.btn_settings)
        pygame.draw.ellipse(self.screen, border, self.btn_settings, 3)
        draw_gear_icon(
            self.screen,
            self.btn_settings.centerx,
            self.btn_settings.centery,
            outer_r=max(22, size // 2 - 14),
            inner_r=max(10, size // 6),
        )

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.draw_title()
        self.draw_buttons()
        draw_home_board(self.screen, self.sx, self.sy)
        self.draw_settings_button()
        self.draw_team_name()

        mouse_pos = pygame.mouse.get_pos()
        if self.modal == "settings":
            self.draw_settings_modal(mouse_pos)
        elif self.modal == "rules":
            self.draw_rules_modal(mouse_pos)

    def handle_click(self, mouse_pos):
        if self.modal == "settings":
            self.handle_settings_click(mouse_pos)
            return None

        if self.modal == "rules":
            self.handle_rules_click(mouse_pos)
            return None

        if self.btn_1player and self.btn_1player.collidepoint(mouse_pos):
            return "mode_select"
        if self.btn_2players and self.btn_2players.collidepoint(mouse_pos):
            return "2players"
        if self.btn_rules and self.btn_rules.collidepoint(mouse_pos):
            self.modal = "rules"
            return None
        if self.btn_quit and self.btn_quit.collidepoint(mouse_pos):
            return "quit"
        if self.btn_settings and self.btn_settings.collidepoint(mouse_pos):
            self.modal = "settings"
            return None
        return None

    def get_settings_rects(self):
        padding = max(18, self.sx(42))
        panel_width = min(self.sx(560), self.screen.get_width() - padding * 2)
        panel_height = min(self.sy(420), self.screen.get_height() - padding * 2)
        panel = pygame.Rect(
            (self.screen.get_width() - panel_width) // 2,
            (self.screen.get_height() - panel_height) // 2,
            panel_width,
            panel_height,
        )

        option_width = max(120, panel.width // 3)
        option_height = max(42, panel.height // 8)
        option_y = panel.top + max(120, panel.height // 3)
        gap = max(12, panel.width // 18)

        english_button = pygame.Rect(
            panel.centerx - gap - option_width,
            option_y,
            option_width,
            option_height,
        )
        vietnamese_button = pygame.Rect(
            panel.centerx + gap,
            option_y,
            option_width,
            option_height,
        )
        close_button = pygame.Rect(
            panel.centerx - panel.width // 5,
            panel.bottom - max(76, panel.height // 5),
            max(140, panel.width // 2),
            max(46, panel.height // 8),
        )

        return {
            "panel": panel,
            "english_button": english_button,
            "vietnamese_button": vietnamese_button,
            "close_button": close_button,
        }

    def draw_settings_modal(self, mouse_pos):
        rects = self.get_settings_rects()
        panel = rects["panel"]

        draw_backdrop(self.screen)
        draw_decorated_panel(self.screen, panel)

        title_font = pygame.font.SysFont("timesnewroman", self.sf(48), bold=True)
        label_font = pygame.font.SysFont("segoeui", self.sf(28), bold=True)
        hint_font = pygame.font.SysFont("segoeui", self.sf(20))

        title = title_font.render(self.preferences.text("settings_title"), True, BLACK)
        label = label_font.render(self.preferences.text("settings_language"), True, BLACK)
        hint = hint_font.render(self.preferences.text("settings_saved"), True, (95, 95, 104))

        self.screen.blit(title, title.get_rect(center=(panel.centerx, panel.top + max(42, panel.height // 7))))
        self.screen.blit(label, label.get_rect(center=(panel.centerx, panel.top + max(94, panel.height // 4))))
        self.screen.blit(hint, hint.get_rect(center=(panel.centerx, panel.bottom - max(118, panel.height // 4))))

        draw_option_pill(
            self.screen,
            rects["english_button"],
            self.preferences.text("language_en"),
            active=self.preferences.language == "en",
            hovered=rects["english_button"].collidepoint(mouse_pos),
            font_size=self.sf(20),
        )
        draw_option_pill(
            self.screen,
            rects["vietnamese_button"],
            self.preferences.text("language_vi"),
            active=self.preferences.language == "vi",
            hovered=rects["vietnamese_button"].collidepoint(mouse_pos),
            font_size=self.sf(20),
        )
        draw_modal_button(
            self.screen,
            rects["close_button"],
            self.preferences.text("settings_close"),
            hovered=rects["close_button"].collidepoint(mouse_pos),
            font_size=self.sf(24),
        )

    def handle_settings_click(self, mouse_pos):
        rects = self.get_settings_rects()
        if not rects["panel"].collidepoint(mouse_pos):
            self.modal = None
            return

        if rects["english_button"].collidepoint(mouse_pos):
            self.preferences.set_language("en")
            self.preferences.save()
            return

        if rects["vietnamese_button"].collidepoint(mouse_pos):
            self.preferences.set_language("vi")
            self.preferences.save()
            return

        if rects["close_button"].collidepoint(mouse_pos):
            self.modal = None

    def get_rules_rects(self):
        padding = max(18, self.sx(38))
        panel_width = min(self.sx(660), self.screen.get_width() - padding * 2)
        panel_height = min(self.sy(520), self.screen.get_height() - padding * 2)
        panel = pygame.Rect(
            (self.screen.get_width() - panel_width) // 2,
            (self.screen.get_height() - panel_height) // 2,
            panel_width,
            panel_height,
        )
        close_button = pygame.Rect(
            panel.centerx - panel.width // 5,
            panel.bottom - max(76, panel.height // 6),
            max(160, panel.width // 2),
            max(46, panel.height // 9),
        )
        return {
            "panel": panel,
            "close_button": close_button,
        }

    def draw_rules_modal(self, mouse_pos):
        rects = self.get_rules_rects()
        panel = rects["panel"]

        draw_backdrop(self.screen)
        draw_decorated_panel(self.screen, panel)

        title_font = pygame.font.SysFont("timesnewroman", self.sf(46), bold=True)
        body_font = pygame.font.SysFont("segoeui", self.sf(24))
        title = title_font.render(self.preferences.text("rules_title"), True, BLACK)
        self.screen.blit(title, title.get_rect(center=(panel.centerx, panel.top + max(42, panel.height // 10))))

        text_width = panel.width - max(70, panel.width // 8)
        current_y = panel.top + max(108, panel.height // 5)
        bullet_gap = max(8, self.sy(10))

        for line in self.preferences.rules_lines():
            wrapped = wrap_text(f"- {line}", body_font, text_width)
            for wrapped_line in wrapped:
                surface = body_font.render(wrapped_line, True, BLACK)
                self.screen.blit(surface, (panel.left + max(34, panel.width // 14), current_y))
                current_y += surface.get_height() + bullet_gap
            current_y += bullet_gap

        draw_modal_button(
            self.screen,
            rects["close_button"],
            self.preferences.text("rules_close"),
            hovered=rects["close_button"].collidepoint(mouse_pos),
            font_size=self.sf(24),
        )

    def handle_rules_click(self, mouse_pos):
        rects = self.get_rules_rects()
        if not rects["panel"].collidepoint(mouse_pos):
            self.modal = None
            return

        if rects["close_button"].collidepoint(mouse_pos):
            self.modal = None
