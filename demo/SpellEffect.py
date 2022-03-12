from demo.TurnManager import TurnManager
from lib.GridEntity import GridEntity


class SpellEffect:
    def __init__(self, damage=0, damage_type=GridEntity.DAMAGE_NORMAL, move_linear=None, move_radial=None, teleport=False,
                 stun=0, affected=(GridEntity.FACTION_ALLY, GridEntity.FACTION_HOSTILE, GridEntity.FACTION_NEUTRAL),
                 action=None, delayed_action=None, duration=0, summon=None, summon_args=None,
                 density=GridEntity.DENSITY_CREATURE):
        """
        Define a spell effect to be applied to all valid targets in some area
        :param damage: Deal damage to target; negative value indicates healing
        :param damage_type: Type of damage for determining resistance and vulnerability
        :param move_linear: Push target in a specified direction
        :param move_radial: Push target radially away from the origin of the effect
        :param teleport: If false, massive enemies are pushed less distance and entities can't move through walls
        :param affected: Class or classes of targets that can be affected
        :param action: Custom function to be called on the target (e.g. reduce spell cooldowns)
        :param delayed_action: Custom function to be called on the target every turn after the first
        :param duration: Number of turns to continue calling the delayed_action function (-1 for infinite turns)
        :param summon: Class of entity to summon
        :param summon_args: Dictionary of keyword arguments for constructing summoned entity
        :param density: Density of valid targets
        """
        self.damage = damage
        self.damage_type = damage_type
        self.move_linear = move_linear
        self.move_radial = move_radial
        self.teleport = teleport
        self.stun = stun
        if not hasattr(affected, "__iter__"):
            affected = (affected,)
        self.affected = affected
        self.action = action
        self.delayed_action = delayed_action
        self.duration = duration
        self.summon = summon
        if not summon_args:
            summon_args = {}
        self.summon_args = summon_args
        if not hasattr(density, "__iter__"):
            density = (density,)
        self.density = density
        # TODO: implement delayed action spells

    def apply(self, target, caster):
        # TODO (low priority): sort squares by distance from origin to avoid collisions when pushing
        for square in target.squares:
            tile = square + caster.position_on_grid
            items = caster.layer.map.get_all_at_position(tile.x, tile.y)
            if not items:
                continue
            summoned = False
            for item in items:
                if item.faction in self.affected and item.density in self.density:
                    if self.damage or self.stun:
                        item.damage(hp=self.damage, damage_type=self.damage_type, stun=self.stun)
                    if self.move_linear:
                        item.push(self.move_linear.x, self.move_linear.y, teleport=self.teleport)
                    if self.move_radial:
                        move = (item.position_on_grid - caster.position_on_grid - target.origin)
                        if move.magnitude():
                            move.scale_to(self.move_radial)
                            item.push(round(move.x), round(move.y), teleport=self.teleport)
                    if self.summon and not summoned:
                        entity = self.summon(**self.summon_args)
                        caster.layer.add_to_cell(entity, item.position_on_grid.x, item.position_on_grid.y)
                        TurnManager.add_entities(entity)
                        summoned = True
                    if self.action:
                        self.action(self, item)
