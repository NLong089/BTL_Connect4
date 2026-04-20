import pygame

from config import BLACK, BORDER_PINK, LIGHT_PINK, WHITE

OVERLAY = (16, 18, 24, 150)
SHADOW = (223, 214, 229)
MUTED = (90, 90, 102)
SOFT_FILL = (250, 245, 249)
ACTIVE_FILL = (255, 221, 238)


def draw_backdrop(screen, alpha=150):
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((OVERLAY[0], OVERLAY[1], OVERLAY[2], alpha))
    screen.blit(overlay, (0, 0))


def draw_decorated_panel(screen, rect, bg_color=WHITE, border_color=BORDER_PINK, radius=28):
    shadow_rect = rect.move(0, 10)
    pygame.draw.rect(screen, SHADOW, shadow_rect, border_radius=radius)
    pygame.draw.rect(screen, bg_color, rect, border_radius=radius)
    pygame.draw.rect(screen, border_color, rect, width=4, border_radius=radius)

    inner_rect = rect.inflate(-28, -28)
    if inner_rect.width > 0 and inner_rect.height > 0:
        pygame.draw.rect(screen, border_color, inner_rect, width=2, border_radius=max(14, radius - 8))
        _draw_corner(screen, inner_rect.left, inner_rect.top, "tl", border_color)
        _draw_corner(screen, inner_rect.right, inner_rect.top, "tr", border_color)
        _draw_corner(screen, inner_rect.left, inner_rect.bottom, "bl", border_color)
        _draw_corner(screen, inner_rect.right, inner_rect.bottom, "br", border_color)


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

    font = pygame.font.SysFont(font_name, font_size, bold=True)
    surface = font.render(label, True, text_color)
    screen.blit(surface, surface.get_rect(center=rect.center))


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


def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
            continue

        if current_line:
            lines.append(" ".join(current_line))
        current_line = [word]

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def _draw_corner(screen, x, y, position, color):
    size = 18
    thickness = 2
    box = 10

    if position == "tl":
        pygame.draw.arc(screen, color, (x, y, size, size), 0, 1.57, thickness)
        pygame.draw.rect(screen, color, (x, y, box, box), width=thickness)
    elif position == "tr":
        pygame.draw.arc(screen, color, (x - size, y, size, size), 1.57, 3.14, thickness)
        pygame.draw.rect(screen, color, (x - box, y, box, box), width=thickness)
    elif position == "bl":
        pygame.draw.arc(screen, color, (x, y - size, size, size), -1.57, 0, thickness)
        pygame.draw.rect(screen, color, (x, y - box, box, box), width=thickness)
    elif position == "br":
        pygame.draw.arc(screen, color, (x - size, y - size, size, size), 3.14, 4.71, thickness)
        pygame.draw.rect(screen, color, (x - box, y - box, box, box), width=thickness)


def _shift_color(color, amount):
    return tuple(min(255, channel + amount) for channel in color)
