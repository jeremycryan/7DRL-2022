from lib.GridEntity import GridEntity
from lib.ImageHandler import ImageHandler
from lib.Sprite import StaticSprite, InvisibleSprite

import random

class Enemy(GridEntity):
    name = "ENEMY"
    hit_points = 1

    faction = GridEntity.FACTION_HOSTILE

    def __init__(self):
        super().__init__()
        self.add_sprite(self.load_sprite())
        self.solid = True

    def load_sprite(self):
        """
        By default, return an invisible sprite.
        :return:
        """
        return InvisibleSprite()

    def take_turn(self):
        """
        Code to run when the enemy takes its turn. Remember to set self.taking_turn to true if it needs to wait on
        an animation, etc. to finish before other entities take their turns. This should probably be the case for
        anything other than regular movement.
        """
        pass


class Goomba(Enemy):
    name = "GOOMBA"
    hit_points = 1

    def __init__(self):
        super().__init__()

    def load_sprite(self):
        """
        By default, return an invisible sprite.
        :return:
        """
        sprite = StaticSprite.from_path("images/goomba.png")
        sprite.set_colorkey((255, 0, 255))
        return sprite

    def take_turn(self):
        """
        Code to run when the enemy takes its turn. Remember to set self.taking_turn to true if it needs to wait on
        an animation, etc. to finish before other entities take their turns. This should probably be the case for
        anything other than regular movement.
        """
        directions = [(1, 0), (0, 1), (0, -1), (-1, 0)]
        random.shuffle(directions)
        for direction in directions:
            if self.can_move(*direction):
                self.move(*direction)
                self.align_sprites()
                break
