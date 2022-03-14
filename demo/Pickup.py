import pygame
import math
import time

from lib.GridEntity import GridEntity
from lib.ImageHandler import ImageHandler
from lib.Primitives import Pose
from lib.Sprite import StaticSprite
from lib.Animation import ShrinkToNothing


class Pickup(GridEntity):

    is_pickup = True
    density = GridEntity.DENSITY_PICKUP

    def __init__(self):
        super().__init__()
        self.solid = False

    def on_pickup(self, pickupper):
        self.add_animation(ShrinkToNothing(self, 0.25))


class LetterTile(Pickup):

    def __init__(self, letter):
        super().__init__()
        self.letter = letter
        self.add_sprite(StaticSprite(ImageHandler.load(f"images/letters/UI_LETTER_{letter}.png"), colorkey=(255, 0, 255)))

    def on_pickup(self, pickupper):
        super().on_pickup(pickupper)
        if hasattr(pickupper, "letter_tiles"):
            pickupper.letter_tiles.append(self)


class LostPage(Pickup):

    def __init__(self):
        super().__init__()
        self.add_sprite(StaticSprite(ImageHandler.load("images/shadow.png"), blend_mode=pygame.BLEND_MULT))
        self.page_sprite = StaticSprite(ImageHandler.load("images/lost_page.png"), colorkey=(255, 0, 255))
        self.add_sprite(self.page_sprite)


    def on_pickup(self, pickupper):
        super().on_pickup(pickupper)
        pickupper.learn_spell()

    def update(self, dt, events):
        super().update(dt, events)
        self.page_sprite.position = self.position + Pose((0, -10 - math.sin(time.time()*10) * 2))


class HealthPickup(Pickup):
    def __init__(self):
        super().__init__()
        self.add_sprite(StaticSprite(ImageHandler.load("images/small_shadow.png"), blend_mode=pygame.BLEND_MULT))
        self.pip_sprite = (StaticSprite(ImageHandler.load("images/ui/UI_Health_3Pip.png"), colorkey=(255, 0, 255)))
        self.add_sprite(self.pip_sprite)

    def update(self, dt, events):
        super().update(dt, events)
        self.pip_sprite.position = self.position + Pose((0, -5 - math.sin(time.time()*10) * 1))

    def on_pickup(self, pickupper):
        if hasattr(pickupper, "heal"):
            if pickupper.heal(3):
                super().on_pickup(pickupper)


class HealthPickupSmall(Pickup):
    def __init__(self):
        super().__init__()
        self.add_sprite(StaticSprite(ImageHandler.load("images/small_shadow.png"), blend_mode=pygame.BLEND_MULT))
        self.pip_sprite = (StaticSprite(ImageHandler.load("images/ui/heart_pip_pickup.png"), colorkey=(255, 0, 255)))
        self.add_sprite(self.pip_sprite)

    def update(self, dt, events):
        super().update(dt, events)
        self.pip_sprite.position = self.position + Pose((0, -5 - math.sin(time.time()*10) * 1))

    def on_pickup(self, pickupper):
        if hasattr(pickupper, "heal"):
            if pickupper.heal(1):
                super().on_pickup(pickupper)