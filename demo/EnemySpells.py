from demo.Spell import Spell
import demo.SpellArea as Area
from demo.SpellEffect import SpellEffect
from lib.GridEntity import GridEntity
from lib.Primitives import Pose


class BatAttack(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        target = self.snap_to_range(target, upper=1, lower=1)
        if target:
            self.add_effect(SpellEffect(damage=self.caster.strength, damage_type=GridEntity.DAMAGE_PHYSICAL),
                            Area.Point(target))
        return self.effects, self.areas, self.delays


class SpiderAttack(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        target = self.snap_to_line(target, diagonals=False)
        target = self.snap_to_range(target, upper=3, lower=2)
        target = self.snap_to_visible(target, pierce=False)
        if target:
            self.add_effect(SpellEffect(damage=self.caster.strength, damage_type=GridEntity.DAMAGE_WEB),
                            Area.Line(endpoint=target))
        return self.effects, self.areas, self.delays


class WolfAttack(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        target = self.snap_to_range(target, upper=1, lower=1)
        if target:
            if abs(target.x) > 0:
                start = target + Pose((0, 1))
                end = target + Pose((0, -1))
            else:
                start = target + Pose((1, 0))
                end = target + Pose((-1, 0))
            self.add_effect(SpellEffect(damage=self.caster.strength, damage_type=GridEntity.DAMAGE_PHYSICAL),
                            Area.Line(start, end, offset=False))
        return self.effects, self.areas, self.delays


class OrcAttack(Spell):
    turns = 5

    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        if turn == 0:
            target = self.snap_to_line(target, diagonals=False)
            target = self.snap_to_range(target, upper=3, lower=1)
            target = self.snap_to_visible(target, pierce=False)
            if target:
                self.add_effect(SpellEffect(damage_type=None), Area.Point(target))  # Used for AI logic only
        if target:
            target = self.snap_to_range(target, upper=1)  # One square in forward direction
            if turn == 0 or turn == 2 or turn == 4:  # Attack (sweep)
                if abs(target.x) > 0:
                    start = target + Pose((0, 1))
                    end = target + Pose((0, -1))
                else:
                    start = target + Pose((1, 0))
                    end = target + Pose((-1, 0))
                self.add_effect(SpellEffect(damage=self.caster.strength, damage_type=GridEntity.DAMAGE_PHYSICAL),
                                Area.Line(start, end, offset=False))
                self.add_effect(SpellEffect(move_linear=target), Area.Point(target))
                self.combo = True
            if turn == 1 or turn == 3:  # Charge forward
                self.add_effect(SpellEffect(move_linear=target), Area.Point())
                self.combo = True
        return self.effects, self.areas, self.delays
