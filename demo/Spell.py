from demo.SpellEffect import SpellEffect
import demo.SpellArea as Area
from lib.GridEntity import GridEntity
from lib.Settings import Settings


class Spell:
    turns = 1
    description = "All knowledge of this spell has been lost."

    def __init__(self, caster):
        self.caster = caster
        self.effects = []
        self.areas = []
        self.delays = []
        self.combo = False

    def caster_pos(self):
        return self.caster.position_on_grid

    def clear_effects(self):
        self.effects = []
        self.areas = []
        self.delays = []

    def get_effects(self, target, crit=False, turn=0):
        """
        Determine the effects of casting this spell at the selected target
        :param target: The grid position of the target relative to the caster
        :param crit: True if spell should be extra powerful
        :param turn: Turn number for multi-turn spells
        :return: Lists of effects, areas, and delays, or None if target is invalid
        """
        target = self.snap_to_line(target)
        if not target:
            return None, None, None
        self.clear_effects()
        self.add_effect(SpellEffect(damage=2 if crit else 1), Area.Point(target))
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
        target = target.copy()
        m = max(abs(target.x), abs(target.y))
        target.scale_to(1 if diagonals else 0.7)
        target.x = round(target.x)
        target.y = round(target.y)
        return target * m

    def snap_to_range(self, target, upper=1.0, lower=0.0):
        """
        Snap target to within desired range
        :param target: the nominal target relative to the caster
        :param upper: the max distance of the spell target from the caster
        :param lower: the min distance of the spell target from the caster
        :return: the adjusted target, or False if target is invalid
        """
        if not target:
            return target
        target = target.copy()
        if target.magnitude() > upper:
            target.scale_to(upper)
            target.x = round(target.x)
            target.y = round(target.y)
        if target.magnitude() > upper or target.magnitude() < lower:
            return False
        return target

    def snap_to_visible(self, target, pierce=False, lower=0):
        """
        Snap target to a square with a direct line of sight from caster
        :param target: the nominal target relative to the caster
        :param lower: the min distance of the spell target from the caster
        :param pierce: if true, the targeting can pass through creatures
        :return: the adjusted target, or False if target is invalid
        """
        if not target or target.magnitude() == 0:
            return target
        if pierce:
            types = (GridEntity.DENSITY_WALL,)
        else:
            types = (GridEntity.DENSITY_WALL, GridEntity.DENSITY_CREATURE)
        target, entity = self.caster.layer.map.raycast(self.caster_pos(), self.caster_pos()+target, types,
                                                       offset=True)
        if not pierce and entity and entity.density == GridEntity.DENSITY_CREATURE:
            target = entity.position_on_grid
        if not target:
            return False
        target -= self.caster_pos()
        if target.magnitude() < lower:
            return False
        return target

    def snap_to_entity(self, target, affected=(), avoid=(), density=()):
        """
        Target an entity that can be affected by the spell
        :param target: the nominal target relative to the caster
        :param affected: only select targets containing these factions of entities
        :param avoid: do not select squares containing these factions of entities
        :param density: only select targets containing this densities of entities
        :return: the target, or False if target is invalid
        """
        if not hasattr(affected, "__iter__"):
            affected = (affected,)
        if not hasattr(avoid, "__iter__"):
            avoid = (avoid,)
        if not hasattr(density, "__iter__"):
            density = (density,)
        if not target:
            return target
        tile = target + self.caster_pos()
        valid = False
        valid_density = False
        for item in self.caster.layer.map.get_all_at_position(tile.x, tile.y):
            if not len(affected) or item.faction in affected:
                valid = True
            if item.faction in avoid:
                return False
            if not len(density) or item.density in density:
                valid_density = True
            if item.density != GridEntity.DENSITY_EMPTY and GridEntity.DENSITY_EMPTY in density:
                return False
        if valid and valid_density:
            return target
        else:
            return False

    def cast(self, target, crit=False, turn=0):
        """
        Cast this spell at the selected target
        :param target: The grid position of the target relative to the caster
        :param crit: True if spell should be extra powerful
        :param turn: Turn number for multi-turn spells
        :return: True if spell was cast successfully
        """
        effects, areas, delays = self.get_effects(target, crit=crit, turn=turn)
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


def get_spell(caster, name):
    """
    Get a spell object from its name (case-insensitive)
    """
    if not name:
        return None
    name = name[0].upper() + name[1:].lower()
    if name in globals():
        spell = globals()[name](caster)
        return spell
    return None

def list_known_spells():
    spells = [spell for spell in list_spells() if spell in Settings.Dynamic.KNOWN_SPELLS]
    return spells

def list_unknown_spells():
    spells = [spell for spell in list_spells() if spell not in Settings.Dynamic.KNOWN_SPELLS]
    return spells

def list_spells():
    """
    Get a list of all existing spell names
    """
    spells = []
    for key in globals().values():
        if isinstance(key, type) and issubclass(key, Spell) and key is not Spell:
            spells.append(key.__name__.upper())
    spells.sort()
    return spells


def recharge(_, entity):
    entity.recharge(letters=1)


class Zap(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        target = self.snap_to_range(target, upper=1.5, lower=1)
        if target:
            self.add_effect(SpellEffect(damage=2 if crit else 1), Area.Point(target))
        return self.effects, self.areas, self.delays

class Stab(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        target = self.snap_to_range(target, upper=1.5, lower=1)
        if target:
            self.add_effect(SpellEffect(damage=3), Area.Point(target))
        return self.effects, self.areas, self.delays

class Flare(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        target = self.snap_to_range(target, upper=2.5, lower=0)
        target = self.snap_to_visible(target)
        if target:
            self.add_effect(SpellEffect(damage=1), Area.Circle(target, radius=1.5))
        return self.effects, self.areas, self.delays

class Firestorm(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        target = self.snap_to_range(target, upper=4.5, lower=1)
        target = self.snap_to_visible(target, pierce=True)
        if target:
            self.add_effect(SpellEffect(damage=2), Area.Circle(target, radius=2.5))
        return self.effects, self.areas, self.delays

class Condemn(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        target = self.snap_to_range(target, upper=0, lower=0)
        target = self.snap_to_visible(target, pierce=True)
        if target:
            self.add_effect(SpellEffect(damage=7), Area.Circle(target, radius=5.5, include_origin = False))
            self.add_effect(SpellEffect(damage=3), Area.Circle(target, radius=.5, include_origin = False))
        return self.effects, self.areas, self.delays

class Push(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        target = self.snap_to_range(target, upper=0, lower=0)
        if target:
            self.add_effect(SpellEffect(move_radial=3, stun=1),
                            Area.Circle(target, radius=1.5 if crit else 1, include_origin=False))
        return self.effects, self.areas, self.delays


class Bolt(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        # target = self.snap_to_line(target)
        target = self.snap_to_visible(target)
        target = self.snap_to_range(target, upper=5, lower=1)
        target = self.snap_to_entity(target, density=GridEntity.DENSITY_CREATURE)
        if target:
            self.add_effect(SpellEffect(damage=2), Area.Point(target))
        return self.effects, self.areas, self.delays


class Beam(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        target *= 5
        target = self.snap_to_line(target)
        target = self.snap_to_visible(target, pierce=True)
        target = self.snap_to_range(target, upper=7, lower=1)
        if target:
            self.add_effect(SpellEffect(damage=2), Area.Line(endpoint=target, offset=True))
        return self.effects, self.areas, self.delays

class Lightning(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        target *= 5
        target = self.snap_to_line(target)
        target = self.snap_to_visible(target, pierce=True)
        target = self.snap_to_range(target, upper=6, lower=1)
        if target:
            self.add_effect(SpellEffect(damage=2), Area.Cross(radius = 3, no_origin = True))
            self.add_effect(SpellEffect(damage=2), Area.Cross(radius = 2, no_origin = True))
            self.add_effect(SpellEffect(damage=2), Area.Cross(radius = 1, no_origin = True))
            self.add_effect(SpellEffect(damage=3), Area.Line(endpoint=target, offset=True))
        return self.effects, self.areas, self.delays


class Hop(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        target = self.snap_to_range(target, upper=2, lower=1)
        target = self.snap_to_entity(target, density=GridEntity.DENSITY_EMPTY)
        if target:
            self.add_effect(SpellEffect(move_linear=target, teleport=True), Area.Point())
            self.add_effect(SpellEffect(), Area.Point(target))
        return self.effects, self.areas, self.delays

class Teleport(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        target = self.snap_to_range(target, upper=4.5, lower=1)
        target = self.snap_to_entity(target, density=GridEntity.DENSITY_EMPTY)
        if target:
            self.add_effect(SpellEffect(move_linear=target, teleport=True), Area.Point())
            self.add_effect(SpellEffect(), Area.Point(target))
        return self.effects, self.areas, self.delays

class Recharge(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        target = self.snap_to_range(target, upper=0, lower=0)
        if target:
            self.add_effect(SpellEffect(action=recharge), Area.Point())
            self.add_effect(SpellEffect(action=recharge), Area.Point())
            self.add_effect(SpellEffect(action=recharge), Area.Point())
            self.add_effect(SpellEffect(action=recharge), Area.Point())
        return self.effects, self.areas, self.delays


class Freeze(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        target = self.snap_to_visible(target)
        target = self.snap_to_range(target, upper=2.5, lower=1)
        if target:
            self.add_effect(SpellEffect(damage_type=GridEntity.DAMAGE_ICE, stun=3),
                            Area.Circle(target, radius=2))
        return self.effects, self.areas, self.delays

class Frostbite(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        target = self.snap_to_visible(target)
        target = self.snap_to_range(target, upper=2.5, lower=1)
        if target:
            self.add_effect(SpellEffect(damage_type=GridEntity.DAMAGE_ICE, stun=4),
                            Area.Circle(target, radius=1))
        return self.effects, self.areas, self.delays


class Golem(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        target = self.snap_to_visible(target)
        target = self.snap_to_entity(target, density=GridEntity.DENSITY_EMPTY)
        target = self.snap_to_range(target, upper=3, lower=1)
        if target:
            import demo.Enemy as Enemy
            self.add_effect(SpellEffect(summon=Enemy.GolemSummon, density=GridEntity.DENSITY_EMPTY), Area.Point(target))
        return self.effects, self.areas, self.delays


class Barrier(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        target = self.snap_to_visible(target)
        target = self.snap_to_entity(target, density=GridEntity.DENSITY_EMPTY)
        target = self.snap_to_range(target, upper=4, lower=1)
        if target:
            import demo.Enemy as Enemy
            self.add_effect(SpellEffect(summon=Enemy.BarrierSummon, density=GridEntity.DENSITY_EMPTY), Area.Point(target))
        return self.effects, self.areas, self.delays
