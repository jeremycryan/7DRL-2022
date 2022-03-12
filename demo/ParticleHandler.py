from lib.Primitives import GameObject, Pose
import pygame
from lib.Settings import Settings
import random
import math

class ParticleHandler:

    particles = {}

    @classmethod
    def init(cls):
        cls.clear_particles()

    @classmethod
    def update(cls, dt, events):
        keys = cls.particles.keys()
        for key in sorted(keys):
            new_particles = []
            for particle in cls.particles[key]:
                particle.update(dt, events)
                if not particle.destroyed:
                    new_particles.append(particle)
            cls.particles[key] = new_particles

    @classmethod
    def draw(cls, surface, offset=(0, 0)):
        for key in sorted(cls.particles.keys()):
            for particle in cls.particles[key]:
                particle.draw(surface, offset=offset)

    @classmethod
    def add_particle(cls, particle, layer=1):
        if not layer in cls.particles:
            cls.particles[layer] = []
        cls.particles[layer].append(particle)

    @classmethod
    def clear_particles(cls):
        cls.particles = {}


class Particle:
    def __init__(self, duration=0.5, position=(0, 0), velocity = (0, 0)):
        self.duration = duration
        self.position = Pose(position, 0)
        self.velocity = Pose(velocity, 0)
        self.age = 0
        self.destroyed = False

    def update(self, dt, events):
        self.age += dt
        self.position += self.velocity * dt
        if self.through() >= 1:
            self.destroy()

    def through(self):
        return min(self.age/self.duration, 1)

    def draw(self, surface, offset=(0, 0)):
        pass

    def destroy(self):
        self.on_destroy()
        self.destroyed = True

    def on_destroy(self):
        pass


class CircleParticle(Particle):

    def __init__(self, duration=0.5, position=(0, 0), radius=5, color=(255, 255, 255), velocity = (0, 0)):
        super().__init__(duration=duration, position=position, velocity=velocity)
        self.radius = radius
        surface = pygame.Surface((2*radius, int(1.5*radius)))
        surface.fill((255, 0, 255))
        r = radius
        pygame.draw.circle(surface, color, (r, r), r)
        surface.set_colorkey((255, 0, 255))
        angle = math.atan2(velocity[1], velocity[0])
        surface = pygame.transform.rotate(surface, angle*180/math.pi)
        self.surface = surface

    def draw(self, surface, offset=(0, 0)):
        radius = self.radius * (1 - self.through())
        if radius < 1:
            return
        x = self.position.x - radius//2 + offset[0]
        y = self.position.y - radius//2 + offset[1]
        # self.surface.set_alpha(255 * (1 - self.through()))
        surface.blit(pygame.transform.scale(self.surface, (int(2*radius), int(2*radius))), (x, y))


class FwooshParticle(Particle):
    def __init__(self, duration=0.5, parent_position = (0, 0), color=(255, 255, 255)):
        offset = Pose((random.random() * 20 - 10, -Settings.Static.TILE_SIZE + random.random() * 20), 0)
        position = Pose(parent_position, 0) + offset
        super().__init__(duration=duration, position=position.get_position(), velocity=(0, Settings.Static.TILE_SIZE/duration))
        self.width = 3
        self.height = 6
        surface = pygame.Surface((self.width, self.height))
        r = 255 - int(20 * abs(offset.x)) - 50
        g = r
        b = 255
        self.color = 255, 255, 255
        surface.fill((255, 0, 255))
        #self.color = color
        pygame.draw.ellipse(surface, self.color, (surface.get_rect()))
        surface.set_colorkey((255, 0, 255))
        self.surface = surface

    def draw(self, surface, offset=(0, 0)):
        width = int(self.through() * self.width)
        height = int(self.through() * self.height)
        if not width or not height:
            return
        x = self.position.x - self.width//2 + offset[0]
        y = self.position.y - self.height//2 + offset[1]
        surface.blit(pygame.transform.scale(self.surface, (width, height)), (x, y))

    def on_destroy(self):
        ParticleHandler.add_particle(CircleParticle(0.25, self.position.get_position(), 5, self.color, (random.random() * 200 - 100, random.random() * 200 - 100)))