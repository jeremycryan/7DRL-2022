from demo.Button import Button
from lib.ImageHandler import ImageHandler
from lib.Primitives import GameObject

import pygame
import sys

from lib.Settings import Settings


class Scene(GameObject):
    pass

    def __init__(self):
        super().__init__()
        self.has_finished = False
        self.age = 0

    def update(self, dt, events):
        self.age += dt

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def draw(self, surf, offset=(0, 0)):
        pass

    def is_over(self):
        return self.has_finished

    def finish(self):
        self.has_finished = True


class TitleScreen(Scene):

    def __init__(self):
        super().__init__()
        self.black = pygame.Surface((Settings.Static.GAME_WIDTH, Settings.Static.GAME_HEIGHT))
        self.black.fill((0, 0, 0))
        self.shown = 0
        self.splash = ImageHandler.load("images/ui/splash.png")
        start_button_surf = pygame.Surface((50, 50))
        start_button_surf.fill((0, 255, 0))
        pygame.draw.polygon(start_button_surf, (255, 255, 255), ((10, 10), (40, 25), (15, 45)))
        self.start_button = Button(start_button_surf,(30, 30), "PlaY", on_click=self.close)
        self.closing = False

    def draw(self, surf, offset=(0, 0)):
        super().draw(surf, offset=offset)
        surf.blit(self.splash, (0, 0))
        self.start_button.draw(surf, *offset)
        surf.blit(self.black, (0, 0))

    def close(self):
        self.closing = True

    def update(self, dt, events):
        super().update(dt, events)
        if self.shown >= 1:
            self.start_button.update(dt, events)
        if not self.closing:
            self.shown = min(1, self.shown + 3*dt)
        else:
            self.shown = max(0, self.shown - 3*dt)
        self.black.set_alpha(255 * (1 - self.shown))
        if self.shown <= 0 and self.closing:
            self.finish()


class GameOverScreen(Scene):


    def __init__(self, level):
        super().__init__()
        self.black = pygame.Surface((Settings.Static.GAME_WIDTH, Settings.Static.GAME_HEIGHT))
        self.black.fill((0, 0, 0))
        self.shown = 0
        self.level = level
        self.splash = ImageHandler.load("images/ui/you_died.png")
        start_button_surf = pygame.Surface((50, 50))
        start_button_surf.fill((0, 255, 0))
        pygame.draw.polygon(start_button_surf, (255, 255, 255), ((10, 10), (40, 25), (15, 45)))
        self.start_button = Button(start_button_surf,(30, 30), "PlaY", on_click=self.close)
        self.closing = False
        self.font = pygame.font.Font("fonts/smallest_pixel.ttf", 10)


    def draw(self, surf, offset=(0, 0)):
        super().draw(surf, offset=offset)
        surf.blit(self.splash, (0, 0))
        font_surf = self.font.render(f"You reached level {self.level - 1} before meeting your end.", 0, (133, 133, 133))
        surf.blit(font_surf, (Settings.Static.GAME_WIDTH//2 - font_surf.get_width()//2, Settings.Static.GAME_HEIGHT//2))

        font_surf = self.font.render(f"Press Enter to continue", 0, (88, 88, 88))
        if self.age > 3 and self.age % 1 < 0.5:
            surf.blit(font_surf, (Settings.Static.GAME_WIDTH//2 - font_surf.get_width()//2, Settings.Static.GAME_HEIGHT - 14))
        surf.blit(self.black, (0, 0))

    def close(self):
        self.closing = True

    def update(self, dt, events):
        super().update(dt, events)
        if not self.closing:
            self.shown = min(1, self.shown + 3*dt)
        else:
            self.shown = max(0, self.shown - 3*dt)
        self.black.set_alpha(255 * (1 - self.shown))
        if self.shown <= 0 and self.closing:
            self.finish()

        if self.age > 2:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.close()