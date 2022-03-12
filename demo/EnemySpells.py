from demo.Spell import Spell
import demo.SpellArea as Area
from demo.SpellEffect import SpellEffect
from lib.GridEntity import GridEntity


class SpiderAttack(Spell):
    def get_effects(self, target, crit=False):
        self.clear_effects()
        target = self.snap_to_range(target, upper=1, lower=1)
        if target:
            self.add_effect(SpellEffect(damage=2 if crit else 1, damage_type=GridEntity.DAMAGE_PHYSICAL), Area.Point(target))
        return self.effects, self.areas, self.delays
