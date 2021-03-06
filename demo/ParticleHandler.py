from lib.ImageHandler import ImageHandler
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
        self.glow = ImageHandler.load_copy("images/glow.png")
        if color != (255, 255, 255):
            self.glow = self.glow.copy()
            tint = pygame.Surface(self.glow.get_size())
            tint.fill((color))
            self.glow.blit(tint, (0, 0), special_flags=pygame.BLEND_MULT)
        super().__init__(duration=duration, position=position, velocity=velocity)
        self.radius = radius
        surface = pygame.Surface((2*radius, int(2*radius)))
        surface.fill((0, 0, 0))
        r = radius
        color = tuple([(item + 255) //  2 for item in color])
        pygame.draw.circle(surface, color, (r, r), r)
        surface.set_colorkey((255, 0, 255))
        self.surface = surface

    def draw(self, surface, offset=(0, 0)):
        radius = self.radius * (1 - self.through())
        if radius < 1:
            return
        x = self.position.x - radius + offset[0]
        y = self.position.y - radius + offset[1]
        # self.surface.set_alpha(255 * (1 - self.through()))
        glow = pygame.transform.scale(self.glow, (int(4*radius), int(4*radius)))
        surface.blit(glow, (self.position.x + offset[0] - glow.get_width()//2, self.position.y + offset[1] - glow.get_height()//2), special_flags=pygame.BLEND_ADD)
        surface.blit(pygame.transform.scale(self.surface, (int(2*radius), int(2*radius))), (x, y), special_flags=pygame.BLEND_ADD)

    def update(self, dt, events):
        super().update(dt, events)
        self.velocity *= 0.1**dt


class FwooshParticle(Particle):
    def __init__(self, duration=0.5, parent_position = (0, 0), color=(255, 255, 255)):
        offset = Pose((random.random() * 20 - 10, -Settings.Static.TILE_SIZE + random.random() * 20), 0)
        position = Pose(parent_position, 0) + offset
        super().__init__(duration=duration, position=position.get_position(), velocity=(0, Settings.Static.TILE_SIZE/duration))
        self.width = 3
        self.height = 6
        surface = pygame.Surface((self.width, self.height))
        self.color = color
        surface.fill((255, 0, 255))
        #self.color = color
        pygame.draw.ellipse(surface, (255, 255, 255), (surface.get_rect()))
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
        ParticleHandler.add_particle(CircleParticle(0.6 * random.random() + 0.25, self.position.get_position(), 5, self.color, (random.random() * 120 - 60, random.random() * 120 - 60)))


class SlashParticle(Particle):
    def __init__(self, duration = 0.5, parent_position = (0, 0), color = (255, 255, 255), thickness = 6, length=8):
        position = Pose((parent_position), 0) + Pose((12, -12), 0)
        super().__init__(duration, position.get_position())
        self.color = color
        surf = pygame.Surface((thickness, length))
        surf.fill((255, 0, 255))
        surf.set_colorkey((255, 0, 255))
        pygame.draw.ellipse(surf, (color), surf.get_rect())
        self.surf = surf
        self.velocity = Pose((-50, 20))
        self.scale = 0

    def update(self, dt, events):
        self.velocity = Pose((-100 + 50*self.through(), 30 + 100*self.through())) * 2
        self.scale = self.through() * (1 - self.through())**2 * 4
        self.velocity *= (1 - self.through())
        super().update(dt, events)

    def draw(self, surface, offset=(0, 0)):
        if self.scale <= 0:
            return
        my_surf = pygame.transform.scale(self.surf, (int(self.surf.get_height()*self.scale), int(self.surf.get_width()*self.scale)))
        my_surf = pygame.transform.rotate(my_surf, math.atan2(self.velocity.y, self.velocity.x) * 180/math.pi + 90)
        x = offset[0] + self.position.x - my_surf.get_width()//2
        y = offset[1] + self.position.y - my_surf.get_height()//2
        my_surf.set_alpha(255 * ((1 - self.through())**0.5))
        surface.blit(my_surf, (x, y))