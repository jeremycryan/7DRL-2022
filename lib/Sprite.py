from lib.Primitives import GameObject, Pose
import pygame
from lib.ImageHandler import ImageHandler
import time
from lib.Settings import Settings


class Sprite(GameObject):
    """
    Class that holds one or more pygame surfaces for an object.
    """

    def __init__(self):
        super().__init__()

        # Position in pixels
        self.position = Pose((0, 0), 0)
        self.distortion = Pose((1, 1), 0)
        self.alpha = 255
        self.tint = (255, 255, 255)  # Color to tint the surface multiplicitively
        self.colorkey = None  # Color key for transparent pixel
        self.flipped_x = False
        self.blend_mode = pygame.BLENDMODE_NONE

    def set_colorkey(self, color):
        self.colorkey = color

    def set_alpha(self, alpha):
        self.alpha = alpha

    def update(self, dt, events):
        pass

    def get_sprite_rect(self):
        return None

    def apply_tint(self, surface):
        # This has to happen after we set the colorkey but before we adjust it for the pygame blend mode workaround
        mask = pygame.mask.from_surface(surface)

        # Workaround for https://github.com/pygame/pygame/issues/3071
        # Adjust colorkey dynamically based on how much a white blit changes the color
        colorkey_test = pygame.Surface((1, 1))
        colorkey_test.fill(self.colorkey)
        tint_test = pygame.Surface((1, 1))
        tint_test.fill((255, 255, 255))
        colorkey_test.blit(tint_test, (0, 0), special_flags=pygame.BLEND_MULT)
        surface.set_colorkey(colorkey_test.get_at((0, 0)))

        # Now actually apply the tint
        tint_surf = mask.to_surface(setcolor=self.tint, unsetcolor=(255, 255, 255))
        my_surface = surface.copy()  # Since we're using a shared surface, but this is destructive
        my_surface.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_MULT)
        return my_surface

    def draw(self, surf, offset=(0, 0)):
        my_surface = self.get_current_surface()
        my_surface.set_colorkey(self.colorkey)
        my_surface.set_alpha(self.alpha)
        if self.tint != (255, 255, 255):
            my_surface = self.apply_tint(my_surface)
        if self.distortion.x != 1 or self.distortion.y != 1:
            width = int(self.distortion.x * my_surface.get_width())
            height = int(self.distortion.y * my_surface.get_height())
            my_surface = pygame.transform.scale(my_surface, (width, height))
        rect = self.get_sprite_rect()
        if type(rect) == tuple:
            rect = pygame.rect.Rect(*rect)
        if not rect:
            rect = pygame.rect.Rect(0, 0, my_surface.get_width(), my_surface.get_height())
        x = self.position.x + offset[0] - rect.width//2
        y = self.position.y + offset[1] - rect.height//2
        surf.blit(my_surface, (x, y), rect, special_flags=self.blend_mode)

    def align_with_grid_object(self, grid_object):
        if not grid_object.layer:
            return  # Can't determine position in real world from grid coordinates
        parent_grid_position = grid_object.position_on_grid.get_position()
        parent_pixel_position = grid_object.layer.grid_to_world_pixel(*parent_grid_position)
        self.position.set_position(parent_pixel_position)

    def align_with_grid_object_pixel(self, grid_object):
        self.position = grid_object.position.copy()

    def get_current_surface(self):
        raise NotImplementedError("Has not been implemented yet.")


class StaticSprite(Sprite):
    def __init__(self, surface, alpha=255, colorkey=None, rect=None, flippable = False, blend_mode = pygame.BLENDMODE_NONE):
        super().__init__()
        self.blend_mode = blend_mode
        self._static_surface = surface
        self.flippable = flippable
        if flippable:
            self._flipped_static_surface = pygame.transform.flip(self._static_surface, True, False)
        if not rect:
            self._static_rect = self._static_surface.get_rect()
        else:
            self._static_rect = rect
            if type(self._static_rect) == tuple:
                self._static_rect = pygame.rect.Rect(*self._static_rect)
        if flippable:
            self._flipped_static_rect = pygame.rect.Rect(
                self._static_surface.get_width() - self._static_rect.width - self._static_rect.left,
                self._static_surface.get_height() - self._static_rect.height - self._static_rect.top,
                self._static_rect.width,
                self._static_rect.height,
            )
        self.set_colorkey(colorkey)
        self.set_alpha(alpha)

    @staticmethod
    def from_path(path, flippable=False):
        sprite = StaticSprite(ImageHandler.load(path), flippable=flippable)
        return sprite

    def get_sprite_rect(self):
        if self.flippable and self.flipped_x:
            return self._flipped_static_rect
        return self._static_rect

    def get_current_surface(self):
        if self.flippable and self.flipped_x:
            return self._flipped_static_surface
        return self._static_surface


class InvisibleSprite(Sprite):
    def __init__(self):
        pass

    def draw(self, surface, offset=(0, 0)):
        pass

    def update(self, dt, events):
        pass
