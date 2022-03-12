from lib.Primitives import GameObject, Pose
import pygame

class ParticleHandler:

    particles = []

    @classmethod
    def init(cls):
        cls.clear_particles()

    @classmethod
    def update(cls, dt, events):
        new_particles = []
        for particle in cls.particles:
            particle.update(dt, events)
            if not particle.destroyed:
                new_particles.append(particle)
        cls.particles = new_particles

    @classmethod
    def draw(cls, surface, offset=(0, 0)):
        for particle in cls.particles:
            particle.draw(surface, offset=offset)

    @classmethod
    def add_particle(cls, particle):
        cls.particles.append(particle)

    @classmethod
    def clear_particles(cls):
        cls.particles = []


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
        self.destroyed = True


class CircleParticle(Particle):

    def __init__(self, duration=0.5, position=(0, 0), radius=5, color=(255, 255, 255), velocity = (0, 0)):
        super().__init__(duration=duration, position=position)
        self.radius = radius
        surface = pygame.Surface((2*radius, 2*radius))
        surface.fill((255, 0, 255))
        r = radius
        pygame.draw.circle(surface, color, (r, r), r)
        surface.set_colorkey((255, 0, 255))
        self.surface = surface

    def draw(self, surface, offset=(0, 0)):
        radius = self.radius * (1 - self.through())
        if radius < 1:
            return
        x = self.position.x - radius//2 + offset[0]
        y = self.position.y - radius//2 + offset[1]
        surface.blit(self.surface, (x, y))