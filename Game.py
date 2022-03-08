import pygame
from lib.ImageHandler import ImageHandler
from lib.Settings import Settings
from lib.demo.Demo1 import Demo1


class Game:
    def __init__(self):
        pygame.init()
        ImageHandler.init()
        Settings.load()
        self.main()

    def main(self):
        pass


if __name__=="__main__":
    Demo1()