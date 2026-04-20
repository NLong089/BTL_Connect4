import math

import pygame

from config import BLACK


def draw_gear_icon(screen, center_x, center_y, outer_r=58, inner_r=24, teeth=8):
    line_width = max(3, outer_r // 8)
    tooth_depth = max(outer_r // 4, 10)
    body_r = max(inner_r + line_width * 2, outer_r - tooth_depth)
    points = []

    for tooth_index in range(teeth):
        angle = tooth_index * (2 * math.pi / teeth)
        tangent = 2 * math.pi / (teeth * 6)
        tooth_outer = outer_r
        tooth_inner = body_r

        points.extend(
            [
                _polar_point(center_x, center_y, tooth_outer, angle - tangent),
                _polar_point(center_x, center_y, tooth_outer, angle + tangent),
                _polar_point(center_x, center_y, tooth_inner, angle + tangent * 1.8),
            ]
        )

        next_angle = angle + (2 * math.pi / teeth)
        valley_angle = next_angle - tangent * 1.8
        points.append(_polar_point(center_x, center_y, tooth_inner, valley_angle))

    pygame.draw.polygon(screen, BLACK, points, width=line_width)
    pygame.draw.circle(screen, BLACK, (center_x, center_y), body_r, width=line_width)
    pygame.draw.circle(screen, BLACK, (center_x, center_y), inner_r, width=line_width)


def _polar_point(cx, cy, radius, angle):
    return (cx + math.cos(angle) * radius, cy + math.sin(angle) * radius)
