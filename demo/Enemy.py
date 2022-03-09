from lib.GridEntity import GridEntity
from lib.ImageHandler import ImageHandler
from lib.Sprite import StaticSprite, InvisibleSprite

import random


class Enemy(GridEntity):
    name = "ENEMY"
    hit_points = 1
    weight = 1
    vulnerabilities = []
    invulnerabilities = []
    resistances = []

    def __init__(self):
        super().__init__()
        self.add_sprite(self.load_sprite())
        self.solid = True
        self.health = self.hit_points

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

    def damage(self, hp, damage_type):
        """
        Apply damage or healing to this entity
        :param hp: Amount of damage to deal; a negative number represents healing
        :param damage_type: Type of damage dealt (SpellEffect.Damage), used to calculate resistance and vulnerability
        """
        if hp > 0 and damage_type in self.resistances:
            hp = hp//2
        elif hp > 0 and damage_type in self.vulnerabilities:
            hp *= 2
        elif hp > 0 and damage_type in self.invulnerabilities:
            hp = 0
        self.health -= hp
        if self.health <= 0:
            self.health = 0
            # TODO: death animation
            if self.position_on_grid is not None:
                self.layer.remove_from_cell(*self.position_on_grid.get_position(), self)

    def push(self, x=0, y=0, teleport=False):
        if not teleport:
            x = x//self.weight
            y = y//self.weight
        # TODO: raycast to avoid moving through walls
        self.move(x, y)
        print(x,y)


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
