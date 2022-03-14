import demo.Player as Player
import demo.EnemyAI as Ai
import demo.EnemySpells as Spell
from demo.EnemyDropHandler import EnemyDropHandler
from demo.Pickup import Pickup, LetterTile
from demo.Wall import Wall
from lib import Math
from lib.Animation import MoveAnimation, Spawn, InstantMoveAnimation
from lib.GridEntity import GridEntity
from lib.ImageHandler import ImageHandler
from lib.Primitives import Pose
from lib.Settings import Settings
from lib.Sprite import StaticSprite, InvisibleSprite
import math

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
    period = 1

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
        self.menacing = []
        if not Enemy.name_font:
            Enemy.name_font = pygame.font.Font("fonts/smallest_pixel.ttf", 10)
            Enemy.name_letters = {letter:Enemy.name_font.render(letter, True, (255, 255, 255)) for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ "}
        self.hearts = {
            0: ImageHandler.load("images/ui/small_health_0pip.png"),
            1: ImageHandler.load("images/ui/small_health_1pip.png"),
            2: ImageHandler.load("images/ui/small_health_2pip.png"),
            3: ImageHandler.load("images/ui/small_health_3pip.png")
        }
        for item in self.hearts.values():
            item.set_colorkey((255, 0, 255))

    def load_sprite(self):
        """
        By default, return an invisible sprite.
        :return:
        """
        return InvisibleSprite()

    def draw(self, surface, offset=(0, 0)):
        super().draw(surface, offset=offset)
        self.draw_name(surface, offset=offset)
        if self.name not in Settings.Dynamic.KNOWN_ENEMIES:
            Settings.Dynamic.KNOWN_ENEMIES.append(self.name)
            Settings.Dynamic.KNOWN_ENEMIES.sort()
        color = (255, 0, 0)
        for square in self.menacing:
            self.draw_highlight(surface, *square.get_position(), color, offset=offset)

    def draw_name(self, surface, offset=(0, 0)):
        letters = [Enemy.name_letters[letter] for letter in self.name]
        width = sum([letter.get_width() for letter in letters])
        x = offset[0] - width//2 + self.position.x
        y = offset[1] - letters[0].get_height()//2 + self.position.y + self.name_y_offset()
        for letter in letters:
            surface.blit(letter, (x, y))
            x += letter.get_width()
        self.draw_health(surface, offset=offset)

    def draw_health(self, surface, offset=(0, 0)):
        number_of_containers = math.ceil(self.hit_points / 3)
        spacing = 8
        x = offset[0] + self.position.x - (spacing * (number_of_containers - 1))//2
        y = offset[1] - 5 + self.position.y + self.name_y_offset()
        health_remaining = self.health

        for i in range(number_of_containers):
            pips = min(health_remaining, 3)
            health_remaining -= pips
            surf = self.hearts[pips]
            surface.blit(surf, (x - surf.get_width()//2, y - surf.get_width()//2))
            x += spacing

    def name_y_offset(self):
        """
        This might be bigger for larger enemies
        """
        return -20

    def take_turn(self):
        """
        Code to run when the enemy takes its turn. Remember to set self.taking_turn to true if it needs to wait on
        an animation, etc. to finish before other entities take their turns. This should probably be the case for
        anything other than regular movement.
        """
        pass

    def damage(self, hp=0, damage_type=GridEntity.DAMAGE_SPELL, stun=0):
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

    def on_destroy(self):
        super().on_destroy()
        if self.position_on_grid and self.drop_letters:
            x, y = self.position_on_grid.get_position()
            drop = EnemyDropHandler.get_drop(self)
            if drop:
                self.layer.map.add_to_cell(drop, x, y, Settings.Static.PICKUP_LAYER)
        # TODO: death animation

    def push(self, x=0, y=0, teleport=False, instant=False):
        if not teleport:
            x = x//self.weight
            y = y//self.weight
        if teleport:
            self.move(x, y, instant)
        else:
            target = Pose((x, y))
            target, entity = self.layer.map.raycast(self.position_on_grid, self.position_on_grid + target,
                                                    (GridEntity.DENSITY_WALL, GridEntity.DENSITY_CREATURE), offset=True)
            if target:
                target -= self.position_on_grid
                self.move(target.x, target.y, instant)

    def move(self, x=0, y=0, keep_turn=False):
        super().move(x, y, keep_turn)
        if x < 0:
            for sprite in self.sprites:
                sprite.flipped_x = True
        if x > 0:
            for sprite in self.sprites:
                sprite.flipped_x = False


class Bat(Enemy):
    name = "BAT"
    hit_points = 1
    strength = 1
    can_melee = True
    can_ranged = True
    spells = [Spell.BatAttack]
    move_squares = Math.get_squares(linear=1)

    def __init__(self):
        super().__init__()
        self.attacks = [spell(self) for spell in self.spells]
        self.stun += int(random.random()*self.period)
        self.current_spell = None
        self.current_target = None
        self.spell_progress = 0

    def load_sprite(self):
        sprite = StaticSprite.from_path("images/rat.png", flippable=True)
        sprite.set_colorkey((255, 0, 255))
        return sprite

    def take_turn(self):
        self.menacing = []
        if self.spell_progress > 0:
            self.current_spell.cast(self.current_target, turn=self.spell_progress)
            self.spell_progress += 1
            if self.spell_progress + 1 > self.current_spell.turns:
                self.current_spell = None
                self.current_target = None
                self.spell_progress = 0
                self.stun += self.period - 1
            else:
                self.combo = self.current_spell.combo
            return
        targets = [e.position_on_grid - self.position_on_grid for e in GridEntity.allies]
        for attack in self.attacks:
            attack_target = Ai.check_spell(self, attack, targets, can_melee=self.can_melee, can_ranged=self.can_ranged)
            if attack_target:
                attack.cast(attack_target)
                if attack.turns > 1:
                    self.current_spell = attack
                    self.current_target = attack_target.copy()
                    self.spell_progress = 1
                    self.combo = attack.combo
                else:
                    self.stun += self.period - 1
                return
        hunt_target = Ai.select_target(self, targets=targets, radius=4, visible=True)
        if hunt_target:
            destination = Ai.hunt(self, hunt_target, squares=self.move_squares)
        else:
            destination = Ai.wander(self, self.move_squares)
        if destination:
            self.move(*destination.get_position())
            self.align_sprites()
        self.stun += self.period - 1


class Spider(Bat):
    name = "SPIDER"
    hit_points = 1
    spells = [Spell.BatAttack, Spell.SpiderAttack]

    def load_sprite(self):
        sprite = StaticSprite.from_path("images/goomba.png", flippable=True)
        sprite.set_colorkey((255, 0, 255))
        return sprite

    def name_y_offset(self):
        return -16

    def load_shadow(self):
        self.add_sprite(StaticSprite(ImageHandler.load("images/small_shadow.png"), blend_mode=pygame.BLEND_MULT))


class Wolf(Bat):
    name = "WOLF"
    hit_points = 3
    period = 2
    spells = [Spell.WolfAttack]

    def load_sprite(self):
        sprite = StaticSprite.from_path("images/dorg.png", flippable=True)
        sprite.set_colorkey((255, 0, 255))
        return sprite

    def name_y_offset(self):
        return -18


class Orc(Bat):
    name = "ORC"
    hit_points = 6
    period = 3
    spells = [Spell.OrcAttack]

    def load_sprite(self):
        sprite = StaticSprite.from_path("images/orca.png", flippable=True)
        sprite.set_colorkey((255, 0, 255))
        return sprite

    def name_y_offset(self):
        return -36


class Shade(Bat):
    name = "SHADE"
    hit_points = 6
    spells = [Spell.ShadeAttack]
    can_melee = False
    move_squares = Math.get_squares(linear=1, custom=1)

    def load_sprite(self):
        sprite = StaticSprite.from_path("images/shade.png", flippable=True)
        sprite.set_colorkey((255, 0, 255))
        return sprite

    def name_y_offset(self):
        return -26


class Slime(Bat):
    name = "SLIME"
    hit_points = 4
    period = 2
    spells = [Spell.BatAttack]

    def load_sprite(self):
        sprite = StaticSprite.from_path("images/slime.png", flippable=True)
        sprite.set_colorkey((255, 0, 255))
        return sprite

    def name_y_offset(self):
        return -26

    def on_move_to_grid_position(self, x, y, keep_turn=False):
        animation = InstantMoveAnimation if keep_turn else MoveAnimation
        self.animations.append(animation(self,
                                         self.position.copy(),
                                         self.layer.grid_to_world_pixel(*self.position_on_grid.get_position()),
                                         squish_factor=0.7, bounce_height=15))
        self.check_for_pickups()

    def take_turn(self):
        if self.health < self.hit_points:
            random.shuffle(self.move_squares)
            for square in self.move_squares:
                if self.clone.cast(square):
                    self.stun += self.period - 1
                    self.hit_points = self.health
                    return
        super().take_turn()

    def __init__(self, hit_points=None):
        super().__init__()
        if hit_points:
            if hit_points < self.hit_points:
                self.health = hit_points
                self.hit_points = hit_points
                self.drop_letters = False
        self.clone = Spell.Clone(self)


class GolemSummon(Enemy):
    name = "GOLEM"
    hit_points = 3
    faction = GridEntity.FACTION_ALLY
    drop_letters = False

    def __init__(self):
        super().__init__()
        self.attacks = [Spell.SpiderAttack(self)]
        self.add_animation(Spawn(self))

    def load_sprite(self):
        sprite = StaticSprite.from_path("images/golem.png", flippable=True)
        sprite.set_colorkey((255, 0, 255))
        return sprite

    def take_turn(self):
        move_squares = Math.get_squares(linear=1)
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

    def name_y_offset(self):
        return -26


class BarrierSummon(Enemy):
    name = "BARRIER"
    hit_points = 5
    faction = GridEntity.FACTION_NEUTRAL
    drop_letters = False
    invulnerabilities = (Enemy.DAMAGE_SPELL,)

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
