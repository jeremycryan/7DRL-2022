from lib.Primitives import Pose
from lib.Math import lerp, PowerCurve
import pygame
import random
from demo.ParticleHandler import ParticleHandler, FwooshParticle
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


class MoveAnimation(Animation):

    blocking = True

    def __init__(self, parent, start_position, end_position, duration=0.2):
        super().__init__(parent, duration=duration)
        self.start_position = start_position
        if type(self.start_position) is tuple:
            self.start_position = Pose(self.start_position, 0)
        self.end_position = end_position
        if type(self.end_position) is tuple:
            self.end_position = Pose(self.end_position, 0)
        self.current_position = start_position.copy()

    def update(self, dt, events):
        super().update(dt, events)
        if self.destroyed:
            return
        bounce_height = Pose((0, ((self.through() - 0.5)*2)**2 - 1), 0) * 8
        curve = PowerCurve(power=1)
        x = lerp(self.start_position.x, self.end_position.x, self.through(), curve)
        y = lerp(self.start_position.y, self.end_position.y, self.through(), curve)
        self.current_position = Pose((x, y), 0) + bounce_height
        self.parent.position = self.current_position.copy()
        for sprite in self.parent.sprites:
            if sprite.blend_mode is not pygame.BLENDMODE_NONE:
                sprite.position.y -= bounce_height.y

    def on_destroy(self):
        self.parent.position = self.end_position.copy()


class Fwoosh(Animation):
    blocking = True
    keep_turn = True

    def __init__(self, parent, duration=0.5, position=(0, 0)):
        """
        If position is specified, ignore position of parent.
        """
        super().__init__(parent, duration)
        self.since_spawn = 0
        self.position = Pose(position) if position else None

    def update(self, dt, events):
        super().update(dt, events)
        if self.through() < 0.3:
            self.since_spawn += dt
        while self.since_spawn > 0.008:
            self.since_spawn -= 0.008
            if not self.position:
                ParticleHandler.add_particle(FwooshParticle(0.2, (self.parent.position.x, self.parent.position.y - 16), (255, 255, 0)))
            else:
                ParticleHandler.add_particle(FwooshParticle(0.2, (self.position.x, self.position.y - 16), (255, 255, 0)))

    @staticmethod
    def no_parent(duration=0.5, position=(0, 0)):
        parent = GameObject()
        parent.position = Pose(position, 0)
        return Fwoosh(parent, duration)