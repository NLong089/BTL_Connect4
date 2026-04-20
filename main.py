import os
import pygame
import sys

from config import WINDOW_WIDTH, WINDOW_HEIGHT
from core.preferences import GamePreferences
from screens.home_page import HomePage
from screens.mode_select_page import ModeSelectPage
from screens.game_page import GamePage

os.environ["SDL_VIDEO_CENTERED"] = "1"

def main():
    pygame.init()

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Connect 4")
    clock = pygame.time.Clock()
    preferences = GamePreferences()

    home_page = HomePage(screen, preferences)
    mode_select_page = ModeSelectPage(screen, preferences)
    game_page = GamePage(screen, preferences)

    current_screen = "home"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.VIDEORESIZE:
                new_width = max(event.w, 800)
                new_height = max(event.h, 600)

                screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)

                home_page.screen = screen
                mode_select_page.screen = screen
                game_page.screen = screen

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if current_screen == "home":
                    result = home_page.handle_click(event.pos)

                    if result == "mode_select":
                        current_screen = "mode_select"
                    elif result == "2players":
                        game_page.reset(game_mode="pvp")
                        current_screen = "game"
                    elif result == "quit":
                        pygame.quit()
                        sys.exit()


                elif current_screen == "mode_select":

                    result = mode_select_page.handle_click(event.pos)

                    if result == "home":

                        current_screen = "home"

                    elif result == "easy":

                        game_page.reset(difficulty="easy", game_mode="ai")

                        current_screen = "game"

                    elif result == "medium":

                        game_page.reset(difficulty="medium", game_mode="ai")

                        current_screen = "game"

                    elif result == "hard":

                        game_page.reset(difficulty="hard", game_mode="ai")

                        current_screen = "game"
                elif current_screen == "game":
                    result = game_page.handle_click(event.pos)

                    if result == "home":
                        current_screen = "home"

        if current_screen == "home":
            home_page.draw()
        elif current_screen == "mode_select":
            mode_select_page.draw()
        elif current_screen == "game":
            game_page.draw()

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
