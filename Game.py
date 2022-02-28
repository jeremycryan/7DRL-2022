import pygame
from lib.ImageHandler import ImageHandler
from lib.Settings import Settings


class Game:
    def __init__(self):
        pygame.init()
        ImageHandler.init()
        Settings.load()
        self.main()

    def main(self):
        pass


if __name__=="__main__":
    Game()