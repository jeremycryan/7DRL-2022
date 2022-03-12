from lib.Primitives import Pose
from lib.Math import lerp, PowerCurve
import pygame
import random
from demo.ParticleHandler import ParticleHandler, FwooshParticle, SlashParticle
from lib.Primitives import GameObject


class Animation:

    blocking = False
    keep_turn = False

    def __init__(self, parent, duration=None):
        self.parent = parent
        self.age = 0
        self.duration = duration
        self.destroyed = False

    def update(self, dt, events):
        self.age += dt
        if self.age > self.duration:
            self.destroy()

    def through(self):
        if self.duration == 0:
            return 1
        if self.duration is None:
            return 0
        return self.age/self.duration

    def destroy(self):
        self.on_destroy()
        self.destroyed = True

    def on_destroy(self):
        # Let child classes do something here
        pass


class DelayAnimation(Animation):
    blocking = True


class Feint(Animation):
    keep_turn = True

    def __init__(self, parent, start_position, vector = (16, 0), duration=0.2, squish_factor = 0.8):
        super().__init__(parent, duration=duration)
        self.start_position = start_position
        if type(self.start_position) is tuple:
            self.start_position = Pose(self.start_position, 0)
        self.end_position = self.start_position + Pose(vector, 0)
        self.current_position = start_position.copy()
        self.squish_factor = squish_factor

    def update(self, dt, events):
        super().update(dt, events)
        if self.destroyed:
            return
        curve = PowerCurve(power=1)
        squish_curve = PowerCurve(power=2, acceleration_time=0.5, deceleration_time=0.01)
        diff = self.end_position - self.start_position
        is_x = abs(diff.x) > abs(diff.y)
        sx, sy = 1, 1
        if self.through() < 0.5:
            x = lerp(self.start_position.x, self.end_position.x, self.through() * 2, curve)
            y = lerp(self.start_position.y, self.end_position.y, self.through() * 2, curve)
            if is_x:
                sx = lerp(1, self.squish_factor, self.through() * 2, squish_curve)
                sy = 1/sx
            else:
                sy = lerp(1, self.squish_factor, self.through() * 2, squish_curve)
                sx = 1/sy
        else:
            x = lerp(self.start_position.x, self.end_position.x, (2 - 2*self.through()), curve)
            y = lerp(self.start_position.y, self.end_position.y, (2 - 2*self.through()), curve)
            if is_x:
                sx = lerp(1, self.squish_factor, (2 - 2*self.through()), squish_curve)
                sy = 1/sx
            else:
                sy = lerp(1, self.squish_factor, (2 - 2*self.through()), squish_curve)
                sx = 1/sy
        self.current_position = Pose((x, y), 0)
        self.parent.position = self.current_position.copy()
        for sprite in self.parent.sprites:
            sprite.distortion = Pose((sx, sy))

    def on_destroy(self):
        self.parent.position = self.start_position.copy()


class MoveAnimation(Animation):

    blocking = True

    def __init__(self, parent, start_position, end_position, duration=0.2, squish_factor = 1):
        super().__init__(parent, duration=duration)
        self.start_position = start_position
        if type(self.start_position) is tuple:
            self.start_position = Pose(self.start_position, 0)
        self.end_position = end_position
        if type(self.end_position) is tuple:
            self.end_position = Pose(self.end_position, 0)
        self.current_position = start_position.copy()
        self.squish_factor = squish_factor

    def update(self, dt, events):
        super().update(dt, events)
        if self.destroyed:
            return
        total_bounce_height = 8
        bounce_height = Pose((0, ((self.through() - 0.5)*2)**2 - 1), 0) * total_bounce_height
        curve = PowerCurve(power=1)
        x = lerp(self.start_position.x, self.end_position.x, self.through(), curve)
        y = lerp(self.start_position.y, self.end_position.y, self.through(), curve)
        self.current_position = Pose((x, y), 0) + bounce_height
        self.parent.position = self.current_position.copy()
        sx = 1 - (bounce_height.magnitude()/total_bounce_height) * (1 - self.squish_factor)
        sy = 1/sx
        for sprite in self.parent.sprites:
            if sprite.blend_mode is not pygame.BLENDMODE_NONE:
                sprite.position.y -= bounce_height.y
            else:
                sprite.distortion = Pose((sx, sy), 0)

    def on_destroy(self):
        self.parent.position = self.end_position.copy()
        for sprite in self.parent.sprites:
            sprite.distortion = Pose((1, 1), 0)


class Fwoosh(Animation):
    blocking = True
    keep_turn = True

    def __init__(self, parent, duration=0.5, position=(0, 0), color = (255, 255, 255)):
        """
        If position is specified, ignore position of parent.
        """
        super().__init__(parent, duration)
        self.since_spawn = 0
        self.color = color
        self.position = Pose(position) if position else None

    def update(self, dt, events):
        super().update(dt, events)
        if self.through() < 0.3:
            self.since_spawn += dt
        while self.since_spawn > 0.008:
            self.since_spawn -= 0.008
            if not self.position:
                ParticleHandler.add_particle(FwooshParticle(0.2, (self.parent.position.x, self.parent.position.y - 16), self.color))
            else:
                ParticleHandler.add_particle(FwooshParticle(0.2, (self.position.x, self.position.y - 16), self.color))

    @staticmethod
    def no_parent(duration=0.5, position=(0, 0)):
        parent = GameObject()
        parent.position = Pose(position, 0)
        return Fwoosh(parent, duration)


class Scratch(Animation):

    blocking = True
    keep_turn = True

    def __init__(self, parent, duration=0.5, position=(0, 0), color = (255, 255, 255)):
        """
        If position is specified, ignore position of parent.
        """
        super().__init__(parent, duration)
        self.since_spawn = 0
        self.color = color
        self.position = Pose(position) if position else None
        diff = (self.position - parent.position)
        diff *= (20 / (diff.magnitude() + 1))
        parent.add_animation(Feint(parent, parent.position.copy(), diff.get_position(), 0.25, 1))

    def update(self, dt, events):
        super().update(dt, events)
        if self.through() < 0.3:
            self.since_spawn += dt
        while self.since_spawn > 0.003:
            self.since_spawn -= 0.003
            root_position = self.parent.position if not self.position else self.position

            for offset in (8, -15), (10, -8), (15, -3):
                ParticleHandler.add_particle(SlashParticle(0.4, (root_position + Pose(offset)).get_position(), self.color))