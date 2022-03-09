from lib.Primitives import Pose
import enum
from demo.Enemy import Enemy


class Damage(enum.Enum):
    normal = 0
    fire = 1
    ice = 2
    electric = 3


class SpellEffect:
    def __init__(self, damage=0, damage_type=Damage.normal, move_linear=None, move_radial=None, teleport=False,
                 stun=0, affected=Enemy, action=None, delayed_action=None, duration=0):
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
        """
        self.damage = damage
        self.damage_type = damage_type
        self.move_linear = move_linear
        self.move_radial = move_radial
        self.teleport = teleport
        self.stun = stun
        self.affected = affected
        self.action = action
        self.delayed_action = delayed_action
        self.duration = duration
        # TODO: add a "spawn new entity" effect
        # TODO: implement delayed action spells
        # TODO: implement stun

    def apply(self, target, caster):
        # TODO (low priority): sort squares by distance from origin to avoid collisions when pushing
        for square in target.squares:
            tile = square + caster.position_on_grid
            for item in caster.layer.map.get_all_at_position(tile.x, tile.y):
                if isinstance(item, self.affected):
                    if self.damage != 0:
                        item.damage(self.damage, self.damage_type)
                    if self.move_linear:
                        item.push(self.move_linear.x, self.move_linear.y, teleport=self.teleport)
                    if self.move_radial:
                        move = (item.position_on_grid - caster.position_on_grid - target.origin)
                        if move.magnitude():
                            move.scale_to(self.move_radial)
                            item.push(round(move.x), round(move.y), teleport=self.teleport)
                    if self.action:
                        self.action(self, item)
