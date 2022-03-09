from lib.GridEntity import GridEntity
from lib.Sprite import StaticSprite
from demo.Spell import *

import pygame

spellKeys = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7,
             pygame.K_8, pygame.K_9]


class Player(GridEntity):

    faction = GridEntity.FACTION_ALLY


    def __init__(self, position=(0, 0)):
        super().__init__(position)
        sprite = StaticSprite.from_path("images/pigeon.png")
        sprite.set_colorkey((255, 0, 255))
        self.sprites.append(sprite)
        self.health = 1
        self.weight = 1
        self.vulnerabilities = []
        self.invulnerabilities = []
        self.resistances = []
        self.prepared_spell = None
        self.spells = [None for i in range(10)]
        self.cooldown = [0 for i in range(10)]
        self.new_turn = True

        self.spells[1] = Zap(self)
        self.spells[2] = Flare(self)
        self.spells[3] = Push(self)
        self.spells[4] = Bolt(self)
        self.spells[5] = Jump(self)
        self.spells[6] = Recharge(self)

    def add_to_layer(self, layer, x, y):
        super().add_to_layer(layer, x, y)

    def update(self, dt, events):
        super().update(dt, events)

        # Start of turn setup
        if self.new_turn:
            self.new_turn = False
            self.recharge()

        # Player input handling
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_w] and self.can_make_turn_movement():
            self.move(y=-1)
            self.end_turn()
        if pressed[pygame.K_s] and self.can_make_turn_movement():
            self.move(y=1)
            self.end_turn()
        if pressed[pygame.K_a] and self.can_make_turn_movement():
            self.move(x=-1)
            self.end_turn()
        if pressed[pygame.K_d] and self.can_make_turn_movement():
            self.move(x=1)
            self.end_turn()
        if self.can_make_turn_movement():
            for i, key in enumerate(spellKeys):
                if pressed[key] and self.cooldown[i] == 0 and self.spells[i] and i != self.prepared_spell:
                    self.prepared_spell = i
                    print("Prepared " + str(self.spells[i]))
        if pressed[pygame.K_ESCAPE]:
            self.prepared_spell = None

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_presses = pygame.mouse.get_pressed()
                if mouse_presses[0] and self.prepared_spell:
                    hover = self.layer.map.get_hovered_tile()
                    if hover and self.get_spell().cast(hover - self.position_on_grid):
                        self.cooldown[self.prepared_spell] = len(self.get_spell().get_name()) + 1
                        self.end_turn()
                        break

    def can_make_turn_movement(self):
        return not self.animating() and self.taking_turn

    def draw(self, surface, offset=(0, 0)):
        super().draw(surface, offset=offset)
        hovered = self.layer.map.get_hovered_tile()
        if hovered and self.get_spell():
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
        self.prepared_spell = None
        self.new_turn = True

    def get_spell(self):
        if self.prepared_spell is None:
            return None
        return self.spells[self.prepared_spell]

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
        if self.health < 0:
            self.health = 0

    def push(self, x=0, y=0, teleport=False):
        if not teleport:
            x = x//self.weight
            y = y//self.weight
        # TODO: raycast to avoid moving through walls
        self.move(x, y)

    def recharge(self, letters=1):
        for i, charge in enumerate(self.cooldown):
            if self.spells[i]:
                n = len(self.spells[i].get_name())
                if n >= charge > 1:
                    print(self.spells[i].get_name()[:n - charge + 1])
                if charge == 1:
                    print(self.spells[i].get_name() + " is ready")
            self.cooldown[i] = max(0, self.cooldown[i] - 1)
