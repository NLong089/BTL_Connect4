import pygame
from config import BG_COLOR, BLACK, BASE_WIDTH, BASE_HEIGHT, BORDER_PINK
from components.button import draw_filled_button, draw_outline_button

class ModeSelectPage:
    def __init__(self, screen, preferences):
        self.screen = screen
        self.preferences = preferences
        self.btn_easy = None
        self.btn_medium = None
        self.btn_hard = None
        self.btn_exit = None
        self.btn_back_1player = None

    def sx(self, x):
        return int(x * self.screen.get_width() / BASE_WIDTH)

    def sy(self, y):
        return int(y * self.screen.get_height() / BASE_HEIGHT)

    def sf(self, size):
        scale_w = self.screen.get_width() / BASE_WIDTH
        scale_h = self.screen.get_height() / BASE_HEIGHT
        return max(16, int(size * min(scale_w, scale_h)))

    def draw_top_button(self):
        label = self.preferences.text("one_player")
        font_size = self.sf(42 if self.preferences.language == "en" else 34)
        self.btn_back_1player = draw_filled_button(
            self.screen, self.sx(24), self.sy(58), self.sx(343), self.sy(112), label, font_size
        )

    def draw_corner(self, x, y, pos):
        size = self.sx(34)
        line = max(2, self.sx(3))
        box = self.sx(16)

        if pos == "tl":
            pygame.draw.arc(self.screen, BORDER_PINK, (x, y, size, size), 0, 1.57, line)
            pygame.draw.rect(self.screen, BORDER_PINK, (x, y, box, box), width=line)
        elif pos == "tr":
            pygame.draw.arc(self.screen, BORDER_PINK, (x - size, y, size, size), 1.57, 3.14, line)
            pygame.draw.rect(self.screen, BORDER_PINK, (x - box, y, box, box), width=line)
        elif pos == "bl":
            pygame.draw.arc(self.screen, BORDER_PINK, (x, y - size, size, size), -1.57, 0, line)
            pygame.draw.rect(self.screen, BORDER_PINK, (x, y - box, box, box), width=line)
        elif pos == "br":
            pygame.draw.arc(self.screen, BORDER_PINK, (x - size, y - size, size, size), 3.14, 4.71, line)
            pygame.draw.rect(self.screen, BORDER_PINK, (x - box, y - box, box, box), width=line)

    def draw_panel(self):
        x = self.sx(390)
        y = self.sy(172)
        w = self.sx(730)
        h = self.sy(746)

        pygame.draw.rect(self.screen, BORDER_PINK, (x, y, w, h), width=max(3, self.sx(5)))
        pygame.draw.rect(self.screen, BORDER_PINK, (x + self.sx(22), y + self.sy(22), w - self.sx(44), h - self.sy(44)), width=max(2, self.sx(3)))

        self.draw_corner(x + self.sx(22), y + self.sy(22), "tl")
        self.draw_corner(x + w - self.sx(22), y + self.sy(22), "tr")
        self.draw_corner(x + self.sx(22), y + h - self.sy(22), "bl")
        self.draw_corner(x + w - self.sx(22), y + h - self.sy(22), "br")

        title_font = pygame.font.SysFont("timesnewroman", self.sf(72), bold=True)
        title = title_font.render(self.preferences.text("levels"), True, BLACK)
        self.screen.blit(title, (self.sx(640), self.sy(215)))

        line_w = max(2, self.sx(4))
        pygame.draw.line(self.screen, BLACK, (self.sx(430), self.sy(236)), (self.sx(590), self.sy(236)), line_w)
        pygame.draw.line(self.screen, BLACK, (self.sx(923), self.sy(236)), (self.sx(1083), self.sy(236)), line_w)

        s = self.sx(14)
        b = max(2, self.sx(4))
        pygame.draw.rect(self.screen, BLACK, (self.sx(425), self.sy(229), s, s), width=b)
        pygame.draw.rect(self.screen, BLACK, (self.sx(584), self.sy(229), s, s), width=b)
        pygame.draw.rect(self.screen, BLACK, (self.sx(917), self.sy(229), s, s), width=b)
        pygame.draw.rect(self.screen, BLACK, (self.sx(1077), self.sy(229), s, s), width=b)

    def draw_buttons(self):
        font_size = self.sf(42 if self.preferences.language == "en" else 34)
        self.btn_easy = draw_outline_button(
            self.screen,
            self.sx(560),
            self.sy(324),
            self.sx(385),
            self.sy(104),
            self.preferences.text("easy"),
            font_size,
        )
        self.btn_medium = draw_outline_button(
            self.screen,
            self.sx(560),
            self.sy(477),
            self.sx(385),
            self.sy(104),
            self.preferences.text("medium"),
            font_size,
        )
        self.btn_hard = draw_outline_button(
            self.screen,
            self.sx(560),
            self.sy(631),
            self.sx(385),
            self.sy(104),
            self.preferences.text("hard"),
            font_size,
        )
        self.btn_exit = draw_outline_button(
            self.screen,
            self.sx(666),
            self.sy(785),
            self.sx(173),
            self.sy(95),
            self.preferences.text("exit"),
            self.sf(38),
        )

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.draw_top_button()
        self.draw_panel()
        self.draw_buttons()

    def handle_click(self, mouse_pos):
        if self.btn_back_1player and self.btn_back_1player.collidepoint(mouse_pos):
            return "home"
        if self.btn_easy and self.btn_easy.collidepoint(mouse_pos):
            return "easy"
        if self.btn_medium and self.btn_medium.collidepoint(mouse_pos):
            return "medium"
        if self.btn_hard and self.btn_hard.collidepoint(mouse_pos):
            return "hard"
        if self.btn_exit and self.btn_exit.collidepoint(mouse_pos):
            return "home"
        return None
