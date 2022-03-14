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


class ShadeAttack(Spell):
    turns = 2

    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        if target:
            if turn == 0:
                target = self.snap_to_range(target, upper=3, lower=1)
                if target:
                    self.add_effect(SpellEffect(menace=True), Area.Cross(origin=target))
            else:
                self.add_effect(SpellEffect(damage=self.caster.strength, damage_type=GridEntity.DAMAGE_FIRE),
                                Area.Cross(origin=target))  # Used for AI logic only
        return self.effects, self.areas, self.delays


class DragonBreath(Spell):
    turns = 2

    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        if target:
            if turn == 0:
                target *= 5
                target = self.snap_to_line(target, diagonals=False)
                target = self.snap_to_range(target, upper=5, lower=1)
        if target:
            target.scale_to(1.1)
            target.x = int(target.x)
            target.y = int(target.y)
            if abs(target.x) > 0:
                a = target + Pose((0, 1))
                b = target + Pose((0, -1))
            else:
                a = target + Pose((1, 0))
                b = target + Pose((-1, 0))
            c = target.copy()
            a2 = a + c * 4
            b2 = b + c * 4
            c2 = c * 5
            p = self.caster.position_on_grid
            a2, _ = self.caster.layer.map.raycast(a.copy() + p, a2 + p, (GridEntity.DENSITY_WALL,), offset=False)
            b2, _ = self.caster.layer.map.raycast(b.copy() + p, b2 + p, (GridEntity.DENSITY_WALL,), offset=False)
            c2, _ = self.caster.layer.map.raycast(c.copy() + p, c2 + p, (GridEntity.DENSITY_WALL,), offset=False)
            if turn == 1:
                if a2:
                    self.add_effect(SpellEffect(damage=3, damage_type=GridEntity.DAMAGE_FIRE),
                                    Area.Line(origin=a, endpoint=a2 - p, offset=False))
                if b2:
                    self.add_effect(SpellEffect(damage=3, damage_type=GridEntity.DAMAGE_FIRE),
                                    Area.Line(origin=b, endpoint=b2 - p, offset=False))
                if c2:
                    self.add_effect(SpellEffect(damage=3, damage_type=GridEntity.DAMAGE_FIRE),
                                    Area.Line(origin=c, endpoint=c2 - p, offset=False))
            if turn == 0:
                if a2:
                    self.add_effect(SpellEffect(menace=True),
                                    Area.Line(origin=a, endpoint=a2 - p, offset=False))
                if b2:
                    self.add_effect(SpellEffect(menace=True),
                                    Area.Line(origin=b, endpoint=b2 - p, offset=False))
                if c2:
                    self.add_effect(SpellEffect(menace=True),
                                    Area.Line(origin=c, endpoint=c2 - p, offset=False))
        return self.effects, self.areas, self.delays


class DragonAttack(Spell):
    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        self.add_effect(SpellEffect(damage=self.caster.strength, damage_type=GridEntity.DAMAGE_PHYSICAL, move_radial=3),
                        Area.Circle(radius=1.5, include_origin=False))
        return self.effects, self.areas, self.delays


class Clone(Spell):

    def get_effects(self, target, crit=False, turn=0):
        self.clear_effects()
        target = self.snap_to_range(target, upper=1, lower=1)
        target = self.snap_to_visible(target)
        if target:
            self.add_effect(SpellEffect(move_linear=target), Area.Point())
            self.add_effect(SpellEffect(summon=self.caster.__class__,
                                        summon_args={"hit_points": self.caster.health},
                                        density=GridEntity.DENSITY_EMPTY),
                            Area.Point(origin=target*-1))
        return self.effects, self.areas, self.delays
