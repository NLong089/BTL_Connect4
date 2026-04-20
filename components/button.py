import pygame

from config import BLACK, BORDER_PINK, LIGHT_PINK, WHITE


def draw_filled_button(
    screen,
    x,
    y,
    w,
    h,
    text,
    font_size=42,
    fill_color=LIGHT_PINK,
    text_color=BLACK,
    font_name="segoeui",
):
    rect = pygame.Rect(x, y, w, h)
    radius = max(18, min(w, h) // 4)
    pygame.draw.rect(screen, fill_color, rect, border_radius=radius)

    font = pygame.font.SysFont(font_name, font_size, bold=True)
    label = font.render(text, True, text_color)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)
    return rect


def draw_outline_button(
    screen,
    x,
    y,
    w,
    h,
    text,
    font_size=42,
    border_color=BORDER_PINK,
    text_color=BLACK,
    fill_color=WHITE,
    font_name="segoeui",
):
    rect = pygame.Rect(x, y, w, h)
    radius = max(18, min(w, h) // 4)
    pygame.draw.rect(screen, fill_color, rect, border_radius=radius)
    pygame.draw.rect(screen, border_color, rect, width=max(3, w // 60), border_radius=radius)

    font = pygame.font.SysFont(font_name, font_size, bold=True)
    label = font.render(text, True, text_color)
    label_rect = label.get_rect(center=rect.center)
    screen.blit(label, label_rect)
    return rect
