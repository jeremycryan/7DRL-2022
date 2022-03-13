import random

from demo.ParticleHandler import ParticleHandler, CircleParticle
from lib.Animation import Fwoosh, Feint
from demo.Pickup import LetterTile
from lib.Camera import Camera
from lib.GridEntity import GridEntity
from lib.Primitives import Pose
from lib.Settings import Settings
from lib.Sprite import StaticSprite
import demo.Spell as Spell
from lib.ImageHandler import ImageHandler

import pygame
import math

spellKeys = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7,
             pygame.K_8, pygame.K_9]


class Player(GridEntity):

    faction = GridEntity.FACTION_ALLY

    def __init__(self, position=(0, 0)):
        super().__init__(position)

        self.staff = ImageHandler.load_copy("images/staff.png")
        self.staff.set_colorkey((255, 0, 255))
        sprite = StaticSprite.from_path("images/pigeon.png", flippable=True)
        sprite.set_colorkey((255, 0, 255))
        self.load_shadow()
        self.sprites.append(sprite)
        self.health = 1
        self.stun = 0
        self.weight = 1
        self.vulnerabilities = []
        self.invulnerabilities = []
        self.resistances = []
        self.prepared_spell = None
        self.spells = [None for i in range(10)]
        self.cooldown = [0 for i in range(10)]
        self.new_turn = True
        self.solid = True

        self.lockout_count = 0

        self.letter_tiles = [LetterTile(letter) for letter in Settings.Static.STARTING_LETTERS]
        self.letters_in_use = self.letter_tiles.copy()

        starting_spells = []#[0, "flare", "push", "bolt", "jump", "recharge", "beam", "freeze", "golem", "barrier"]
        for i, spell in enumerate(starting_spells):
            self.spells[i] = Spell.get_spell(self, starting_spells[i])

    def add_to_layer(self, layer, x, y):
        super().add_to_layer(layer, x, y)

    def on_move_to_grid_position(self, x, y):
        super().on_move_to_grid_position(x, y)
        #self.animations.append(Fwoosh(self, 0.8))

    def update(self, dt, events):
        super().update(dt, events)

        # Start of turn setup
        if self.new_turn:
            self.new_turn = False
            self.recharge()

        if self.locked_out():
            return

        # Player input handling
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_w] and self.can_make_turn_movement():
            if not self.move(y=-1):
                self.add_animation(Feint(self, self.position, (0, -16), duration=0.2))
            self.end_turn()
        if pressed[pygame.K_s] and self.can_make_turn_movement():
            if not self.move(y=1):
                self.add_animation(Feint(self, self.position, (0, 16), duration=0.2))
            self.end_turn()
        if pressed[pygame.K_a] and self.can_make_turn_movement():
            if not self.move(x=-1):
                self.add_animation(Feint(self, self.position, (-16, 0), duration=0.2))
            self.end_turn()
        if pressed[pygame.K_d] and self.can_make_turn_movement():
            if not self.move(x=1):
                self.add_animation(Feint(self, self.position, (16, 0), duration=0.2))
            self.end_turn()
        if self.can_make_turn_movement():
            for i, key in enumerate(spellKeys):
                if pressed[key] and self.cooldown[i] == 0 and self.spells[i] and i != self.prepared_spell:
                    self.prepared_spell = i
        if pressed[pygame.K_ESCAPE]:
            self.prepared_spell = None

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_presses = pygame.mouse.get_pressed()
                if mouse_presses[0] and not self.prepared_spell is None:
                    hover = self.layer.map.get_hovered_tile()
                    if hover and self.get_spell().cast(hover - self.position_on_grid):
                        self.cooldown[self.prepared_spell] = len(self.get_spell().get_name()) + 1
                        self.prepared_spell = None
                        self.end_turn()
                        break

    def can_make_turn_movement(self):
        return not self.animating() and self.taking_turn

    def locked_out(self):
        """
        Indicates the player shouldn't be able to do anything because something else is in control (e.g. a menu)
        :return: True if the player is locked out
        """
        return self.lockout_count > 0

    def lock(self):
        """
        Locks the player. Make sure to call unlock after.
        """
        self.lockout_count += 1

    def unlock(self):
        """
        Unlocks the player. Only call after locking and only once per lock.
        """
        self.lockout_count -= 1

    def draw(self, surface, offset=(0, 0)):
        pose_to_mouse = Camera.mouse_pos_game_coordinates() - self.position
        should_flip = pose_to_mouse.x < 0
        for sprite in self.sprites:
            sprite.flipped_x = should_flip
        angle = -math.atan2(pose_to_mouse.y, pose_to_mouse.x) * 180/math.pi
        staff_rotated = pygame.transform.rotate(self.staff, angle - 90)
        sx = self.position.x + offset[0] + (14 * (1 - 2*should_flip)) - staff_rotated.get_width()//2
        sy = self.position.y + offset[1] - (5) - staff_rotated.get_height()//2
        surface.blit(staff_rotated, (sx, sy))
        super().draw(surface, offset=offset)
        hovered = self.layer.map.get_hovered_tile()
        if hovered and self.get_spell() and not self.locked_out():
            effects, areas, delays = self.get_spell().get_effects(hovered - self.position_on_grid)
            for effect, area, delay in zip(effects, areas, delays):
                if effect.damage > 0:
                    color = (255, 0, 0)
                else:
                    color = (255, 255, 0)
                for square in area.squares:
                    self.draw_highlight(surface, *square.get_position(), color, offset=offset)

            # if any([item.solid for item in self.layer.map.get_all_at_position(hovered.x, hovered.y)]):
            #     color = (255, 0, 0)
            # off = hovered - self.position_on_grid
            # self.draw_highlight(surface, *off.get_position(), color, offset=offset)

    def take_turn(self):
        self.taking_turn = True

    def end_turn(self):
        GridEntity.end_turn(self)
        # self.prepared_spell = None
        self.new_turn = True

    def get_spell(self):
        if self.prepared_spell is None:
            return None
        return self.spells[self.prepared_spell]

    def damage(self, hp=0, damage_type=GridEntity.DAMAGE_NORMAL, stun=0):
        """
        Apply damage or healing to this entity
        :param hp: Amount of damage to deal; a negative number represents healing
        :param damage_type: Type of damage dealt (SpellEffect.Damage), used to calculate resistance and vulnerability
        :param stun: number of turns to skip due to stun effect
        """
        if hp > 0 and damage_type in self.resistances:
            hp = hp // 2
        elif hp > 0 and damage_type in self.vulnerabilities:
            hp *= 2
        elif hp > 0 and damage_type in self.invulnerabilities:
            hp = 0
        if stun > 0 and damage_type in self.invulnerabilities:
            stun = 0
        self.stun = max(self.stun, stun)
        self.health -= hp
        if self.health <= 0:
            self.health = 1
            # self.destroy()
            print("Game Over")  # TODO: Game Over

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

    def recharge(self, letters=1):
        for i, charge in enumerate(self.cooldown):
            self.cooldown[i] = max(0, self.cooldown[i] - 1)

    def check_for_pickups(self):
        if not self.position_on_grid:
            return
        for entity in self.layer.map.get_all_at_position(*self.position_on_grid.get_position()):
            if entity is self:
                pass
            if entity.is_pickup:
                entity.on_pickup(self)
