import demo.Player as Player
import demo.EnemyAI as Ai
import demo.EnemySpells as Spell
from demo.Pickup import Pickup, LetterTile
from demo.Wall import Wall
from lib.GridEntity import GridEntity
from lib.ImageHandler import ImageHandler
from lib.Primitives import Pose
from lib.Settings import Settings
from lib.Sprite import StaticSprite, InvisibleSprite

import random
import pygame


class Enemy(GridEntity):
    name = "ENEMY"
    hit_points = 1
    weight = 1
    drop_letters = True
    vulnerabilities = ()
    invulnerabilities = ()
    resistances = ()

    name_font = None
    name_letters = {}

    faction = GridEntity.FACTION_HOSTILE

    def __init__(self):
        super().__init__()
        self.load_shadow()
        self.add_sprite(self.load_sprite())
        self.solid = True
        self.health = self.hit_points
        self.stun = 0
        if not Enemy.name_font:
            Enemy.name_font = pygame.font.Font("fonts/smallest_pixel.ttf", 10)
            Enemy.name_letters = {letter:Enemy.name_font.render(letter, True, (255, 255, 255)) for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ "}

    def load_sprite(self):
        """
        By default, return an invisible sprite.
        :return:
        """
        return InvisibleSprite()

    def draw(self, surface, offset=(0, 0)):
        super().draw(surface, offset=offset)
        self.draw_name(surface, offset=offset)

    def draw_name(self, surface, offset=(0, 0)):
        letters = [Enemy.name_letters[letter] for letter in self.name]
        width = sum([letter.get_width() for letter in letters])
        x = offset[0] - width//2 + self.position.x
        y = offset[1] - letters[0].get_height()//2 + self.position.y + self.name_y_offset()
        for letter in letters:
            surface.blit(letter, (x, y))
            x += letter.get_width()

    def name_y_offset(self):
        """
        This might be bigger for larger enemies
        """
        return -16

    def take_turn(self):
        """
        Code to run when the enemy takes its turn. Remember to set self.taking_turn to true if it needs to wait on
        an animation, etc. to finish before other entities take their turns. This should probably be the case for
        anything other than regular movement.
        """
        pass

    def damage(self, hp=0, damage_type=GridEntity.DAMAGE_NORMAL, stun=0):
        """
        Apply damage or healing to this entity
        :param hp: Amount of damage to deal; a negative number represents healing
        :param damage_type: Type of damage dealt (SpellEffect.Damage), used to calculate resistance and vulnerability
        :param stun: number of turns to skip due to stun effect
        """
        if hp > 0 and damage_type in self.resistances:
            hp = hp//2
        elif hp > 0 and damage_type in self.vulnerabilities:
            hp *= 2
        elif hp > 0 and damage_type in self.invulnerabilities:
            hp = 0
        if stun > 0 and damage_type in self.invulnerabilities:
            stun = 0
        self.stun = max(self.stun, stun)
        self.health -= hp
        if self.health <= 0:
            self.health = 0
            self.destroy()

    def on_destroy(self):
        super().on_destroy()
        if self.position_on_grid and self.drop_letters:
            x, y = self.position_on_grid.get_position()
            # TODO be smart about what letter I drop
            self.layer.map.add_to_cell(LetterTile(random.choice(self.name)), x, y, Settings.Static.PICKUP_LAYER)
        # TODO: death animation

    def push(self, x=0, y=0, teleport=False):
        if not teleport:
            x = x//self.weight
            y = y//self.weight
        if teleport:
            self.move(x, y)
        else:
            target = Pose((x, y))
            target, entity = self.layer.map.raycast(self.position_on_grid, self.position_on_grid + target,
                                                    (GridEntity.DENSITY_WALL, GridEntity.DENSITY_CREATURE), offset=True)
            if target:
                target -= self.position_on_grid
                self.move(target.x, target.y)

    def move(self, x=0, y=0):
        super().move(x, y)
        if x < 0:
            for sprite in self.sprites:
                sprite.flipped_x = True
        if x > 0:
            for sprite in self.sprites:
                sprite.flipped_x = False


class Goomba(Enemy):
    name = "SPIDER"
    hit_points = 1

    def __init__(self):
        super().__init__()
        self.attacks = [Spell.SpiderAttack(self)]

    def load_sprite(self):
        sprite = StaticSprite.from_path("images/goomba.png", flippable=True)
        sprite.set_colorkey((255, 0, 255))
        return sprite

    def take_turn(self):
        move_squares = Ai.get_squares(self, linear=1)
        attack_squares = move_squares
        targets = [e.position_on_grid - self.position_on_grid for e in GridEntity.allies]
        attack_target = Ai.select_target(self, targets=targets, squares=attack_squares)
        if attack_target:
            self.attacks[0].cast(attack_target)
            return
        hunt_target = Ai.select_target(self, targets=targets, radius=4, visible=True)
        if hunt_target:
            destination = Ai.hunt(self, hunt_target, squares=move_squares)
        else:
            destination = Ai.wander(self, move_squares)
        if destination:
            self.move(*destination.get_position())
            self.align_sprites()


class GolemSummon(Enemy):
    name = "GOLEM"
    hit_points = 3
    faction = GridEntity.FACTION_ALLY
    drop_letters = False

    def __init__(self):
        super().__init__()
        self.attacks = [Spell.SpiderAttack(self)]

    def load_sprite(self):
        sprite = StaticSprite.from_path("images/goomba.png", flippable=True)
        sprite.set_colorkey((255, 0, 255))
        return sprite

    def take_turn(self):
        move_squares = Ai.get_squares(self, linear=1)
        attack_squares = move_squares
        attack_target, _ = Ai.find(self, squares=attack_squares)
        if attack_target:
            self.attacks[0].cast(attack_target)
            return
        hunt_target = GridEntity.allies[0].position_on_grid - self.position_on_grid
        if hunt_target and hunt_target.magnitude() > 3:
            destination = Ai.hunt(self, hunt_target)
        else:
            destination = Ai.wander(self, move_squares)
        if destination:
            self.move(*destination.get_position())
            self.align_sprites()


class BarrierSummon(Enemy):
    name = "BARRIER"
    hit_points = 5
    faction = GridEntity.FACTION_NEUTRAL
    drop_letters = False
    invulnerabilities = (Enemy.DAMAGE_NORMAL,)

    def __init__(self):
        super().__init__()

    def load_sprite(self):
        surf = ImageHandler.load("images/tileset_engine.png")
        tw = Settings.Static.TILE_SIZE  # tile width
        sprite = StaticSprite(surf, rect=(0, 6*tw, tw, tw))
        sprite.set_colorkey((255, 0, 255))
        return sprite

    def take_turn(self):
        self.damage(1, damage_type=self.DAMAGE_OVERRIDE)
