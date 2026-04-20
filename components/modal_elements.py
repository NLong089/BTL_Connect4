import math

import pygame

from config import BLACK, BORDER_PINK, LIGHT_PINK, WHITE

SOFT_FILL = (250, 245, 249)
ACTIVE_FILL = (255, 221, 238)
MUTED = (98, 98, 108)


def draw_backdrop(screen, alpha=110):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((255, 255, 255, alpha))
    screen.blit(overlay, (0, 0))


def draw_corner_ornament(screen, x, y, size, box, line_width, position, color=BORDER_PINK):
    if position == "tl":
        pygame.draw.arc(screen, color, (x, y, size, size), 0, math.pi / 2, line_width)
        pygame.draw.rect(screen, color, (x, y, box, box), width=line_width)
    elif position == "tr":
        pygame.draw.arc(screen, color, (x - size, y, size, size), math.pi / 2, math.pi, line_width)
        pygame.draw.rect(screen, color, (x - box, y, box, box), width=line_width)
    elif position == "bl":
        pygame.draw.arc(screen, color, (x, y - size, size, size), -math.pi / 2, 0, line_width)
        pygame.draw.rect(screen, color, (x, y - box, box, box), width=line_width)
    elif position == "br":
        pygame.draw.arc(screen, color, (x - size, y - size, size, size), math.pi, math.pi * 1.5, line_width)
        pygame.draw.rect(screen, color, (x - box, y - box, box, box), width=line_width)


def draw_decorated_panel(
    screen,
    rect,
    fill_color=WHITE,
    border_color=BORDER_PINK,
    outer_width=3,
    inner_margin=18,
    inner_width=2,
):
    pygame.draw.rect(screen, fill_color, rect)
    pygame.draw.rect(screen, border_color, rect, width=outer_width)

    inner_rect = rect.inflate(-inner_margin * 2, -inner_margin * 2)
    if inner_rect.width <= 0 or inner_rect.height <= 0:
        return rect

    pygame.draw.rect(screen, border_color, inner_rect, width=inner_width)

    corner_size = max(18, inner_margin + 6)
    corner_box = max(10, inner_margin - 2)

    draw_corner_ornament(screen, inner_rect.left, inner_rect.top, corner_size, corner_box, inner_width, "tl", border_color)
    draw_corner_ornament(screen, inner_rect.right, inner_rect.top, corner_size, corner_box, inner_width, "tr", border_color)
    draw_corner_ornament(screen, inner_rect.left, inner_rect.bottom, corner_size, corner_box, inner_width, "bl", border_color)
    draw_corner_ornament(screen, inner_rect.right, inner_rect.bottom, corner_size, corner_box, inner_width, "br", border_color)
    return inner_rect


def draw_panel_header(screen, rect, text, font, title_color=BLACK, line_color=BLACK):
    title = font.render(text, True, title_color)
    title_rect = title.get_rect(center=(rect.centerx, rect.y + max(44, rect.h // 10)))
    screen.blit(title, title_rect)

    line_y = title_rect.centery
    gap = max(24, rect.w // 22)
    margin = max(34, rect.w // 10)
    line_width = max(2, rect.w // 220)
    square_size = max(8, rect.w // 52)

    left_start = rect.left + margin
    left_end = title_rect.left - gap
    right_start = title_rect.right + gap
    right_end = rect.right - margin

    if left_end > left_start:
        pygame.draw.line(screen, line_color, (left_start, line_y), (left_end, line_y), line_width)
        pygame.draw.rect(
            screen,
            line_color,
            (left_start - square_size // 2, line_y - square_size // 2, square_size, square_size),
            width=line_width,
        )
        pygame.draw.rect(
            screen,
            line_color,
            (left_end - square_size // 2, line_y - square_size // 2, square_size, square_size),
            width=line_width,
        )

    if right_end > right_start:
        pygame.draw.line(screen, line_color, (right_start, line_y), (right_end, line_y), line_width)
        pygame.draw.rect(
            screen,
            line_color,
            (right_start - square_size // 2, line_y - square_size // 2, square_size, square_size),
            width=line_width,
        )
        pygame.draw.rect(
            screen,
            line_color,
            (right_end - square_size // 2, line_y - square_size // 2, square_size, square_size),
            width=line_width,
        )

    return title_rect


def draw_modal_button(
    screen,
    rect,
    label,
    hovered=False,
    fill_color=LIGHT_PINK,
    border_color=BORDER_PINK,
    text_color=BLACK,
    font_size=28,
    font_name="segoeui",
):
    draw_fill = _shift_color(fill_color, 10) if hovered else fill_color
    radius = max(16, min(rect.width, rect.height) // 4)
    pygame.draw.rect(screen, draw_fill, rect, border_radius=radius)
    pygame.draw.rect(screen, border_color, rect, width=max(2, rect.width // 70), border_radius=radius)

    inset_x = max(8, rect.width // 12)
    inset_y = max(6, rect.height // 6)
    inner_rect = rect.inflate(-inset_x * 2, -inset_y * 2)
    if inner_rect.width > 0 and inner_rect.height > 0:
        pygame.draw.rect(screen, border_color, inner_rect, width=1, border_radius=max(12, radius - 6))

    font = pygame.font.SysFont(font_name, font_size, bold=True)
    surface = font.render(label, True, text_color)
    screen.blit(surface, surface.get_rect(center=rect.center))
    return rect


def draw_option_pill(screen, rect, label, active=False, hovered=False, font_size=22):
    fill_color = ACTIVE_FILL if active else SOFT_FILL
    border_color = BORDER_PINK if active else MUTED
    text_color = BLACK if active else MUTED
    if hovered:
        fill_color = _shift_color(fill_color, 8)

    pygame.draw.rect(screen, fill_color, rect, border_radius=max(16, rect.height // 2))
    pygame.draw.rect(
        screen,
        border_color,
        rect,
        width=max(2, rect.width // 90),
        border_radius=max(16, rect.height // 2),
    )

    font = pygame.font.SysFont("segoeui", font_size, bold=True)
    surface = font.render(label, True, text_color)
    screen.blit(surface, surface.get_rect(center=rect.center))
    return rect


def draw_volume_icon(screen, center, size, color=BLACK):
    cx, cy = center
    half = size // 2
    line_width = max(3, size // 18)

    speaker_back = pygame.Rect(cx - half, cy - size // 7, size // 5, size * 2 // 7)
    pygame.draw.rect(screen, color, speaker_back)

    speaker_front = [
        (speaker_back.right, cy - size // 4),
        (speaker_back.right + size // 4, cy - size // 2),
        (speaker_back.right + size // 4, cy + size // 2),
        (speaker_back.right, cy + size // 4),
    ]
    pygame.draw.polygon(screen, color, speaker_front)


def draw_sound_state_icon(screen, center, size, enabled, color=BLACK):
    draw_volume_icon(screen, center, size, color)

    if enabled:
        for scale in (0.50, 0.76):
            wave_rect = pygame.Rect(
                int(center[0] - size * scale * 0.05),
                int(center[1] - size * scale),
                int(size * scale * 1.05),
                int(size * scale * 2),
            )
            pygame.draw.arc(screen, color, wave_rect, -0.75, 0.75, max(2, size // 20))
    else:
        slash_offset = size // 3
        slash_width = max(4, size // 16)
        pygame.draw.line(
            screen,
            (221, 92, 115),
            (center[0] - slash_offset // 2, center[1] - slash_offset),
            (center[0] + slash_offset, center[1] + slash_offset),
            slash_width,
        )


def draw_toggle_switch(screen, rect, enabled):
    track_color = (255, 214, 224) if enabled else (236, 236, 236)
    knob_color = (255, 255, 255)
    border_width = max(2, rect.w // 28)

    pygame.draw.rect(screen, track_color, rect, border_radius=rect.h // 2)
    pygame.draw.rect(screen, BORDER_PINK, rect, width=border_width, border_radius=rect.h // 2)

    padding = max(4, rect.h // 10)
    knob_radius = rect.h // 2 - padding
    knob_x = rect.right - rect.h // 2 if enabled else rect.left + rect.h // 2
    pygame.draw.circle(screen, knob_color, (knob_x, rect.centery), knob_radius)
    pygame.draw.circle(screen, BORDER_PINK, (knob_x, rect.centery), knob_radius, width=border_width)


def draw_language_box(screen, rect, text, font):
    pygame.draw.rect(screen, WHITE, rect, border_radius=max(10, rect.h // 5))
    pygame.draw.rect(screen, BORDER_PINK, rect, width=max(2, rect.w // 60), border_radius=max(10, rect.h // 5))

    label = font.render(text, True, BLACK)
    label_rect = label.get_rect(midleft=(rect.left + max(16, rect.w // 12), rect.centery))
    screen.blit(label, label_rect)

    arrow_color = (199, 57, 138)
    arrow_size = max(10, rect.h // 5)
    arrow_center_x = rect.right - max(22, rect.w // 6)
    arrow_center_y = rect.centery + 2
    pygame.draw.polygon(
        screen,
        arrow_color,
        [
            (arrow_center_x - arrow_size, arrow_center_y - arrow_size // 2),
            (arrow_center_x + arrow_size, arrow_center_y - arrow_size // 2),
            (arrow_center_x, arrow_center_y + arrow_size),
        ],
    )
    return rect


def draw_qr_placeholder(screen, rect, color=(87, 87, 92)):
    qr_rect = rect.copy()
    size = min(qr_rect.w, qr_rect.h)
    qr_rect.size = (size, size)
    qr_rect.center = rect.center

    module_count = 21
    cell = max(4, size // module_count)
    qr_size = cell * module_count
    start_x = qr_rect.centerx - qr_size // 2
    start_y = qr_rect.centery - qr_size // 2

    matrix = [[0 for _ in range(module_count)] for _ in range(module_count)]

    def fill_finder(row, col):
        for r in range(7):
            for c in range(7):
                rr = row + r
                cc = col + c
                outer = r in (0, 6) or c in (0, 6)
                inner = 2 <= r <= 4 and 2 <= c <= 4
                matrix[rr][cc] = 1 if outer or inner else 0

    fill_finder(0, 0)
    fill_finder(0, module_count - 7)
    fill_finder(module_count - 7, 0)

    for i in range(8, module_count - 8):
        matrix[6][i] = i % 2
        matrix[i][6] = (i + 1) % 2

    data_modules = [
        (9, 9), (9, 10), (9, 11), (10, 8), (10, 12), (11, 9), (11, 10), (11, 11),
        (13, 8), (13, 9), (13, 11), (13, 12), (14, 10), (15, 8), (15, 11), (16, 9),
        (8, 14), (9, 15), (10, 14), (11, 15), (12, 14), (13, 15), (14, 14), (15, 15),
        (8, 17), (9, 18), (10, 17), (12, 17), (13, 18), (15, 17), (16, 18), (17, 17),
        (17, 9), (17, 10), (17, 11), (18, 8), (18, 12), (19, 9), (19, 10), (19, 11),
    ]
    for row, col in data_modules:
        if 0 <= row < module_count and 0 <= col < module_count:
            matrix[row][col] = 1

    for row in range(module_count):
        for col in range(module_count):
            if matrix[row][col]:
                pygame.draw.rect(
                    screen,
                    color,
                    (start_x + col * cell, start_y + row * cell, cell, cell),
                    border_radius=max(1, cell // 4),
                )


def wrap_text(*args):
    if len(args) != 3:
        raise TypeError("wrap_text expects 3 arguments")

    first, second, max_width = args
    if hasattr(first, "size"):
        font = first
        text = second
    else:
        text = first
        font = second

    words = str(text).split()
    if not words:
        return [""]

    lines = []
    current_line = words[0]

    for word in words[1:]:
        test_line = f"{current_line} {word}"
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)
    return lines


def _shift_color(color, amount):
    return tuple(min(255, channel + amount) for channel in color)
