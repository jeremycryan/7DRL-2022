from SpellEffect import SpellEffect, Damage
from SpellArea import *
import demo.Player as Player
from demo.Enemy import Enemy


class Spell:
    def __init__(self, caster):
        self.caster = caster
        self.effects = []
        self.areas = []
        self.delays = []

    def clear_effects(self):
        self.effects = []
        self.areas = []
        self.delays = []

    def get_effects(self, target, crit=False):
        """
        Determine the effects of casting this spell at the selected target
        :param target: The grid position of the target relative to the caster
        :param crit: True if spell should be extra powerful
        :return: Lists of effects, areas, and delays, or None if target is invalid
        """
        target = self.snap_to_line(target)
        if not target:
            return None, None, None
        self.clear_effects()
        self.add_effect(SpellEffect(damage=2 if crit else 1), Point(target))
        return self.effects, self.areas, self.delays

    def snap_to_line(self, target, diagonals=True):
        """
        Snaps target to nearest cardinal direction from caster
        :param target: the nominal target relative to the caster
        :param diagonals: if true, diagonal lines are allowed
        :return: the adjusted target, or False if target is invalid
        """
        if not target:
            return target
        m = max(abs(target.x), abs(target.y))
        target.scale_to(1 if diagonals else 0.5)
        target.x = round(target.x)
        target.y = round(target.y)
        return target * m

    def snap_to_range(self, target, upper=1, lower=0):
        """
        Snap target to within desired range
        :param target: the nominal target relative to the caster
        :param upper: the max distance of the spell target from the caster
        :param lower: the min distance of the spell target from the caster
        :return: the adjusted target, or False if target is invalid
        """
        if not target:
            return target
        if target.magnitude() > upper:
            target.scale_to(upper)
            target.x = round(target.x)
            target.y = round(target.y)
        if target.magnitude() < lower:
            return False
        return target

    def snap_to_visible(self, target, pierce=False, lower=0):
        """
        Snap target to a square with a direct line of sight from caster
        :param target: the nominal target relative to the caster
        :param lower: the min distance of the spell target from the caster
        :param pierce: if true, the targeting can pass through enemies
        :return: the adjusted target, or False if target is invalid
        """
        if not target:
            return target
        # TODO: raycast
        if target.magnitude() < lower:
            return False
        return target

    def snap_to_entity(self, target, affected=Enemy):
        """
        Target an entity that can be affected by the spell
        :param target: the nominal target relative to the caster
        :param affected: the min distance of the spell target from the caster
        :return: the adjusted target, or False if target is invalid
        """
        if not target:
            return target
        tile = target + self.caster.position_on_grid
        for item in self.caster.layer.map.get_all_at_position(tile.x, tile.y):
            if isinstance(item, affected):
                return target
        return False

    def cast(self, target):
        """
        Cast this spell at the selected target
        :param target: The grid position of the target relative to the caster
        :return: True if spell was cast successfully
        """
        print("Cast " + self.get_name())
        effects, areas, delays = self.get_effects(target)
        if not effects:
            return False
        for effect, area, delay in zip(effects, areas, delays):
            effect.apply(area, self.caster)
        # TODO: call iteratively from TurnManager to allow effects to animate
        return True

    def add_effect(self, effect, area, delay=0):
        """
        Add an effect to the spell
        :param effect: spell effect to add
        :param area: spell area to target
        :param delay: delay in animation after previous effect (ms)
        """
        self.effects.append(effect)
        self.areas.append(area)
        self.delays.append(delay)

    def get_name(self):
        return self.__class__.__name__.upper()

    def __repr__(self):
        return self.get_name()


class Zap(Spell):
    def get_effects(self, target, crit=False):
        self.clear_effects()
        target = self.snap_to_range(target, upper=1, lower=1)
        if target:
            self.add_effect(SpellEffect(damage=2 if crit else 1), Point(target))
        return self.effects, self.areas, self.delays


class Flare(Spell):
    def get_effects(self, target, crit=False):
        self.clear_effects()
        target = self.snap_to_range(target, upper=2, lower=0)
        if target:
            self.add_effect(SpellEffect(damage=1), Circle(target, radius=1.5 if crit else 1))
        return self.effects, self.areas, self.delays


class Push(Spell):
    def get_effects(self, target, crit=False):
        self.clear_effects()
        target = self.snap_to_range(target, upper=0, lower=0)
        if target:
            self.add_effect(SpellEffect(move_radial=2), Circle(target, radius=1.5 if crit else 1))
        return self.effects, self.areas, self.delays


class Bolt(Spell):
    def get_effects(self, target, crit=False):
        self.clear_effects()
        target = self.snap_to_line(target)
        target = self.snap_to_visible(target)
        target = self.snap_to_range(target, upper=5, lower=1)
        target = self.snap_to_entity(target)
        if target:
            self.add_effect(SpellEffect(damage=2 if crit else 1), Point(target))
        return self.effects, self.areas, self.delays


class Jump(Spell):
    def get_effects(self, target, crit=False):
        self.clear_effects()
        target = self.snap_to_range(target, upper=2, lower=1)
        if target:
            self.add_effect(SpellEffect(move_linear=target, affected=Player.Player, teleport=True), Point())
            self.add_effect(SpellEffect(), Point(target))
        return self.effects, self.areas, self.delays


class Recharge(Spell):
    def get_effects(self, target, crit=False):
        self.clear_effects()
        target = self.snap_to_range(target, upper=0, lower=0)
        if target:
            self.add_effect(SpellEffect(affected=Player.Player, action=recharge), Point())
        return self.effects, self.areas, self.delays


def recharge(effect, entity):
    entity.recharge(letters=1)
