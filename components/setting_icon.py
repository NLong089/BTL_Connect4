import pygame
import math
from config import BLACK

def draw_gear_icon(screen, center_x, center_y, outer_r=58, inner_r=24, teeth=8):
    points = []
    for i in range(teeth * 2):
        angle = i * math.pi / teeth
        r = outer_r if i % 2 == 0 else outer_r - 14
        x = center_x + math.cos(angle) * r
        y = center_y + math.sin(angle) * r
        points.append((x, y))

    pygame.draw.polygon(screen, BLACK, points, width=6)
    pygame.draw.circle(screen, BLACK, (center_x, center_y), inner_r, width=6)