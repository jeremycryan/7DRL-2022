import random

from lib.Primitives import GameObject, Pose
from lib.Animation import MoveAnimation
from lib.Settings import Settings
import pygame


class GridEntity(GameObject):

    SOLID_KEY = "S"
    ANY_KEY = "?"
    EMPTY_KEY = "."
    CURRENT_KEY = "@"

    def __init__(self, position=(0, 0)):
        """
        Creates a new game object.
        :param position: Position, in GRID coordinates
        """
        super().__init__()
        self.position = Pose(position, 0)
        self.position_on_grid = None
        self.layer = None
        self.solid = False
        self.sprites = []
        self.grid_rules = []
        self.animations = []

    def add_grid_rule(self, sprite, key=("@",), inverse=False, likelihood=1.0):
        """
        Create a grid rule. If conditions match the key, the provided sprite will be applied. Otherwise, it will
        move on to the next sprite rule.
        :param key: A key representing the conditions for the sprite to be applied. Must be a tuple of strings of
            equal length, with keys defined in GridEntity.SOLID_KEY, GridEntity.ANY_KEY, and so on.

            The following key:
                ("SSS",
                 "?@?",
                 "?.?")

            Means a tile will use the provided sprite only if the three tiles directly and diagonally above it ("@")
            are solid ("S"), and the tile directly below it is empty ("."). The remaining tiles can be anything ("?").

            The key must contain exactly one GridEntity.CURRENT_KEY ("@") symbol. The rule ("@",) will pass all
            conditions.
        :param sprite: The sprite to apply if the rule passes.
        :param inverse: If true, this sprite will NOT be applied if the key matches, but will for all other conditions.
        :param likelihood: If specified, the rule will only be applied if a random value between 0 and 1 is less than
            the specified likelihood.
        """
        self.grid_rules.append((key, sprite, inverse, likelihood))

    def check_grid_rule(self, key, inverse=False, likelihood=1.0):
        """
        Checks whether a grid rule should pass or fail
        :param key: The grid rule as a list of strings
        :param inverse: If true, inverts the result before returning.
        :param likelihood: If specified, the rule will only be applied if a random value between 0 and 1 is less than
            the specified likelihood.
        :return: True if the rule passes, false otherwise.
        """

        width = len(key[0])
        origin = None

        # Start out by finding the reference point
        for y, row in enumerate(key):
            if len(row) != width:
                raise ValueError("Key must have consistent lengths for all strings.")
            if self.CURRENT_KEY in row:
                if origin or row.count(self.CURRENT_KEY) > 1:
                    raise ValueError(f"Key must contain only one '{self.CURRENT_KEY}' symbol.")
                origin = row.index(self.CURRENT_KEY), y
        if not origin:
            raise ValueError(f"Key must contain only one '{self.CURRENT_KEY}' symbol.")

        # Now check whether we match the rule
        match = True
        for y, row in enumerate(key):
            if not match:
                break
            for x, item in enumerate(row):
                if not match:
                    break
                if item == self.CURRENT_KEY or item == self.ANY_KEY:
                    continue
                grid_x = self.position_on_grid.x + (x - origin[0])
                grid_y = self.position_on_grid.y + (y - origin[1])
                found_solid = False
                if not self.layer.cell_in_range(grid_x, grid_y):
                    found_solid = True  # Count out of range cells as solid
                else:
                    for grid_item in self.layer.peek_at_cell(grid_x, grid_y):
                        if grid_item.solid:
                            found_solid = True
                if found_solid:
                    if item == self.EMPTY_KEY:
                        match = False
                        continue
                else:
                    if item == self.SOLID_KEY:
                        match = False
                        continue

        match *= (random.random() <= likelihood)
        return match ^ inverse  # ^ is XOR

    def get_sprite_from_grid_rules(self):
        """
        Determines which sprite should be applied by evaluating the grid rules, then returns it.
        :return: The sprite, or None if no rules applied.
        """
        for key, sprite, inverse, likelihood in self.grid_rules:
            if self.check_grid_rule(key, inverse, likelihood):
                return sprite
        return None

    def draw(self, surface, offset=(0, 0)):
        for sprite in self.sprites:
            sprite.draw(surface, offset=offset)

    def align_sprites(self):
        for sprite in self.sprites:
            sprite.align_with_grid_object(self)

    def align_sprites_pixel(self):
        for sprite in self.sprites:
            sprite.align_with_grid_object_pixel(self)

    def update(self, dt, events):
        self.align_sprites_pixel()
        for animation in self.animations[:]:
            animation.update(dt, events)
            if animation.destroyed:
                self.animations.remove(animation)
        for sprite in self.sprites:
            sprite.update(dt, events)

    def add_sprite(self, sprite):
        self.sprites.append(sprite)
        sprite.align_with_grid_object(self)

    def add_to_layer(self, layer, x, y):
        """
        Call this when adding the GameObject to a map layer.
        :param layer: The layer we're being added to
        :param x: The x coordinate
        :param y: The y coordinate
        :return:
        """
        first_add = self.layer is None
        self.position_on_grid = Pose((x, y), 0)
        self.layer = layer
        if first_add:
            self.position = Pose(layer.grid_to_world_pixel(*self.position_on_grid.get_position()), 0)
            self.align_sprites_pixel()

    def on_move_to_grid_position(self, x, y):
        """
        Called when the object it has moved to a new x, y bucket in the grid.

        The object doesn't actually manipulate the grid in any way, it just is being told
        it should update itself visually.
        :param x: The new x position
        :param y: The new y position
        """
        self.animations.append(MoveAnimation(self,
                                             self.position.copy(),
                                             self.layer.grid_to_world_pixel(*self.position_on_grid.get_position())))

    def add_animation(self, animation):
        self.animations.append(animation)

    def can_move_to_grid_position(self, x, y):
        """
        Determines whether or not the entity can move to the specified position.

        By default, returns False if there's a solid object there.
        :param x: New X position
        :param y: New Y position
        :return:
        """
        self.require_grid()
        if not self.layer or not self.layer.cell_in_range(x, y):
            return False
        others = self.layer.map.get_all_at_position(x, y)
        for other in others:
            if other.solid:
                return False
        return True

    def move_to_grid_position(self, x, y):
        """
        Moves the object to the new grid position.
        :param x: The new X position
        :param y: The new Y position
        :return: True if successfully moved
        """
        self.require_grid()
        if not self.can_move_to_grid_position(x, y):
            return False
        if self.position_on_grid is not None:
            self.layer.remove_from_cell(*self.position_on_grid.get_position(), self)
        self.position_on_grid = Pose((x, y), 0)
        self.layer.add_to_cell(self, x, y)
        self.on_move_to_grid_position(x, y)
        return True

    def move(self, x=0, y=0):
        """
        Moves the object relative to its current position.
        :param x: The amount to move in the X direction, with positive numbers being right
        :param y: The amount to move in the Y direction, with positive numbers being down
        :return: True if successfully moved
        """
        self.require_grid()
        return self.move_to_grid_position(self.position_on_grid.x + x, self.position_on_grid.y + y)

    def require_grid(self):
        """Requires the layer property to be populated. """
        assert self.layer is not None

    def animating(self):
        for animation in self.animations:
            if animation.blocking:
                return True
        return False

    def draw_highlight(self, surface, x, y, color, offset=(0, 0)):
        """
        Highlights grid squares
        :param x: The x position to draw the highlight at, in number of tiles to the entity's right (0 is on the entity)
        :param y: The y position to draw the highlight, in number of tiles to the entity's south (0 is on the entity)
        :param color: The color of the highlight
        """
        tile_size = Settings.Static.TILE_SIZE
        center = (self.position_on_grid + Pose((x, y), 0))*tile_size + Pose(offset, 0)
        rect = (center.x - tile_size//2, center.y - tile_size//2, tile_size, tile_size)
        pygame.draw.rect(surface, color, rect, 2)