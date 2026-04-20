import pygame
from config import PINK, WHITE, BLUE, YELLOW

def draw_home_board(screen, sx, sy):
    board_x = sx(586)
    board_y = sy(208)
    board_w = sx(775)
    board_h = sy(646)
    rows = 6
    cols = 7
    radius = max(12, min(board_w // 20, board_h // 16))

    pygame.draw.rect(screen, PINK, (board_x, board_y, board_w, board_h), border_radius=max(20, board_w // 16))

    cell_w = board_w / cols
    cell_h = board_h / rows

    for r in range(rows):
        for c in range(cols):
            cx = int(board_x + c * cell_w + cell_w / 2)
            cy = int(board_y + r * cell_h + cell_h / 2)
            pygame.draw.circle(screen, WHITE, (cx, cy), radius)

    pieces = [
        (3, 3, YELLOW),
        (4, 2, YELLOW),
        (4, 3, BLUE),
        (5, 2, BLUE),
        (5, 3, YELLOW),
        (5, 4, BLUE),
    ]

    for r, c, color in pieces:
        cx = int(board_x + c * cell_w + cell_w / 2)
        cy = int(board_y + r * cell_h + cell_h / 2)
        pygame.draw.circle(screen, color, (cx, cy), radius)