from demo.Enemy import Enemy
from demo.TurnManager import TurnManager
from demo.Wall import Floor
from lib.GridEntity import GridEntity
from lib.Settings import Settings
from lib.Primitives import Pose
from lib.Camera import Camera
import pygame


class Map:
    TILE_WIDTH = Settings.Static.TILE_SIZE
    TILE_HEIGHT = Settings.Static.TILE_SIZE
    OUT_OF_FRAME_DISTANCE = TILE_WIDTH*2  # The distance outside the window frame we stop drawing objects

    def __init__(self, width, height):
        """
        Creates an empty map.
        :param width: Width, in tiles
        :param height: Height, in tiles
        """
        self.width = width
        self.height = height

        self.layers = []

    def get_hovered_tile(self):
        mpos = Pose(pygame.mouse.get_pos(), 0)
        mpos -= Pose((Settings.Static.WINDOW_WIDTH//2, Settings.Static.WINDOW_HEIGHT//2), 0)
        mpos.x *= Settings.Static.GAME_WIDTH/Settings.Static.WINDOW_WIDTH
        mpos.y *= Settings.Static.GAME_HEIGHT/Settings.Static.WINDOW_HEIGHT
        mpos += Camera.get_game_position() * -1
        #mpos += Pose((Settings.Static.GAME_WIDTH//2, Settings.Static.GAME_HEIGHT//2), 0)
        mpos += Pose((Settings.Static.TILE_SIZE//2, Settings.Static.TILE_SIZE//2), 0)  # Because tile centers are the position

        x = mpos.x//Settings.Static.TILE_SIZE
        y = mpos.y//Settings.Static.TILE_SIZE

        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None

        else:
            return Pose((int(x), int(y)), 0)

    def add_empty_layer(self, height=0):
        """
        Adds a new layer to the Map.
        :param height: The height of the layer. Lower numbers will be drawn first. The behavior of equal heights
            is not specified.
        :return: The new layer
        """
        new_layer = Map.MapLayer(self, height)
        self.layers.append(new_layer)
        self.layers = sorted(self.layers, key=lambda x: -x.key)
        return new_layer

    def in_frame(self, x, y):
        """
        Returns whether a given pixel coordinate is within the map's render area.
        :param x: X coordinate
        :param y: Y coordinate
        :return: True if an object at that coordinate will be drawn by the map, false otherwise
        """
        if x < -self.OUT_OF_FRAME_DISTANCE:
            return False
        if y < -self.OUT_OF_FRAME_DISTANCE:
            return False
        if x > Settings.Static.GAME_WIDTH + self.OUT_OF_FRAME_DISTANCE:
            return False
        if y > Settings.Static.GAME_HEIGHT + self.OUT_OF_FRAME_DISTANCE:
            return False
        return True

    def get_all_at_position(self, x, y):
        """
        Returns a list of all game objects at that point, regardless of layer
        :param x: X coordinate
        :param y: Y coordinate
        :return: The list of game objects
        """
        objects = []
        for layer in self.layers:
            objects += layer.peek_at_cell(x, y)
        return objects

    def add_to_cell(self, game_object, x, y, layer_key):
        for layer in self.layers:
            if layer.key == layer_key:
                layer.add_to_cell(game_object, x, y)
                return
        raise IndexError(f"No layer with key {layer_key} exists in the map.")

    def update(self, dt, events):
        for layer in self.layers:
            layer.update(dt, events)

    def draw(self, surface, offset=(0, 0)):
        for i, layer in enumerate(self.layers):
            if i == 3:  # draw targets
                layer.draw(surface, offset=offset, density=(GridEntity.DENSITY_WALL, GridEntity.DENSITY_EMPTY))
                layer.draw_overlays(surface, offset)
                layer.draw(surface, offset=offset, density=(GridEntity.DENSITY_CREATURE, GridEntity.DENSITY_PICKUP))
            else:
                layer.draw(surface, offset=offset)

    def get_layer(self, key):
        for layer in self.layers:
            if layer.key == key:
                return layer
        return None

    def cell_in_range(self, x, y):
        return 0 <= x <= self.width - 1 and 0 <= y <= self.height - 1

    def raycast(self, start, end, blocking_types, offset=False):
        """
        Find first entity in a line
        :param start: first square to check
        :param end: final square to check
        :param blocking_types: densities of obstacles that stop the raycast
        :param offset: if true, start on second square
        :return: last open square and the entity that was hit
        """
        diff = end - start
        if not diff.magnitude():
            if offset:
                return None, None
            else:
                if not self.cell_in_range(start.x, start.y):
                    return None, None
                for item in self.get_all_at_position(start.x, start.y):
                    if item.density in blocking_types:
                        return None, item
                return start, None
        prev = None
        if abs(diff.y) > abs(diff.x):
            for dy in range(1 if offset else 0, abs(diff.y)+1):
                scale = abs(dy / diff.y)
                p = start + diff*scale
                p.x = round(p.x)
                p.y = round(p.y)
                if not self.cell_in_range(p.x, p.y):
                    return prev, None
                for item in self.get_all_at_position(p.x, p.y):
                    if item.density in blocking_types:
                        return prev, item
                prev = p
        else:
            for dx in range(1 if offset else 0, abs(diff.x)+1):
                scale = abs(dx / diff.x)
                p = start + diff*scale
                p.x = round(p.x)
                p.y = round(p.y)
                if not self.cell_in_range(p.x, p.y):
                    return prev, None
                for item in self.get_all_at_position(p.x, p.y):
                    if item.density in blocking_types:
                        return prev, item
                prev = p
        return end, None

    def get_entity(self, squares, origin=Pose((0, 0)), factions=None):
        for square in squares:
            p = square + origin
            for item in self.get_all_at_position(p.x, p.y):
                if not factions or item.faction in factions:
                    return square, item
        return None, None

    def filter_line_of_sight(self, squares, origin, blocking_types=(GridEntity.DENSITY_WALL,)):
        new_squares = []
        for square in squares:
            sq, item = self.raycast(origin, origin + square, blocking_types, offset=True)
            if sq and (square + origin - sq).magnitude() == 0:
                new_squares.append(square)
        return new_squares

    def check_line_of_sight(self, square, origin, blocking_types=(GridEntity.DENSITY_WALL,)):
        end, item = self.raycast(origin, origin + square, blocking_types, offset=True)
        return end and (square + origin - end).magnitude() == 0

    class MapCell(list):
        # Making this its own class in case we wanted to add anything fancy to it later for pathfinding, etc.
        pass

    class MapLayer:
        def __init__(self, parent_map, key=None):
            self.map = parent_map
            self.cells = [[Map.MapCell() for _ in range(parent_map.width)] for _ in range(parent_map.height)]
            self._populated_cells = set()
            self.key = key

            # Parallax multipliers; lower numbers mean the layer moves slower with a given offset
            self.x_parallax = 1
            self.y_parallax = 1
            self.x_offset = 0
            self.y_offset = 0

            self._updates_enabled = True
            self._draws_enabled = True

        def enable_updates(self, enable=True):
            if enable:
                self._updates_enabled = True
            else:
                self._updates_enabled = False

        def enable_draws(self, enable=True):
            if enable:
                self._draws_enabled = True
            else:
                self._draws_enabled = False

        def add_to_cell(self, game_object, x, y):
            self.cells[y][x].append(game_object)

            coordinates = (x, y)
            game_object.add_to_layer(self, x, y)
            if coordinates not in self._populated_cells:
                self._populated_cells.add(coordinates)

        def pop_from_cell(self, x, y):
            if not self.cells[y][x]:
                return None
            result = self.cells[y][x].pop()
            if not self.cells[y][x] and (x, y) in self._populated_cells:
                self._populated_cells.remove((x, y))
            return result

        def peek_at_cell(self, x, y):
            if not self.cell_in_range(x, y):
                return []
            return self.cells[y][x].copy()

        def cell_occupied(self, x, y):
            return len(self.peek_at_cell(x, y)) > 0

        def map_cell_occupied(self, x, y):
            return len(self.map.get_all_at_position(x, y)) > 0

        def cell_in_range(self, x, y):
            return 0 <= x <= self.map.width - 1 and 0 <= y <= self.map.height - 1

        def pop_all_from_cell(self, x, y):
            result = self.peek_at_cell(x, y)
            self.cells[y][x] = []
            if (x, y) in self._populated_cells:
                self._populated_cells.remove((x, y))
            return result

        def remove_from_cell(self, x, y, item):
            self.cells[y][x].remove(item)
            if not self.cells[y][x] and (x, y) in self._populated_cells:
                self._populated_cells.remove((x, y))

        def populated_cells(self):
            for x, y in self._populated_cells.copy():
                yield self.cells[y][x]

        def cell_coordinates(self):
            for y, row in enumerate(self.cells):
                for x, cell in enumerate(row):
                    yield x, y

        def populated_cells_and_coordinates(self):
            for x, y in self._populated_cells:
                yield self.cells[y][x], x, y

        def draw(self, surface, offset=(0, 0), density=None):
            if not self._draws_enabled:
                return
            camera_position = Camera.position
            top_left = camera_position - Pose((Settings.Static.GAME_WIDTH//2, Settings.Static.GAME_HEIGHT//2), 0)
            bottom_right = camera_position + Pose((Settings.Static.GAME_WIDTH//2, Settings.Static.GAME_HEIGHT//2), 0)
            x1, y1 = self.world_pixel_to_grid(*top_left.get_position())
            x2, y2 = self.world_pixel_to_grid(*bottom_right.get_position())
            for x in range(int(x1 - 2), int(x2+3)):
                for y in range(int(y1 - 2), int(y2+3)):
                    if self.map.cell_in_range(x, y):
                        cell = self.peek_at_cell(x, y)
                        for game_object in cell:
                            if not density or game_object.density in density:
                                game_object.draw(surface, offset=offset)

        def draw_overlays(self, surface, offset=(0, 0)):
            for cell in self._populated_cells:
                entities = self.peek_at_cell(*cell)
                for entity in entities:
                    entity.draw_targets(surface, offset)

        def update(self, dt, events):
            if not self._updates_enabled:
                return
            updated_objects = set()
            camera_position = Camera.position
            top_left = camera_position - Pose((Settings.Static.GAME_WIDTH//2, Settings.Static.GAME_HEIGHT//2), 0)
            bottom_right = camera_position + Pose((Settings.Static.GAME_WIDTH//2, Settings.Static.GAME_HEIGHT//2), 0)
            x1, y1 = self.world_pixel_to_grid(*top_left.get_position())
            x2, y2 = self.world_pixel_to_grid(*bottom_right.get_position())
            turn_entities = set(TurnManager.entities)
            for x in range(int(x1 - 2), int(x2+3)):
                for y in range(int(y1 - 2), int(y2+3)):
                    if self.map.cell_in_range(x, y):
                        cell = self.peek_at_cell(x, y)
                        for game_object in cell:
                            if game_object in updated_objects:
                                continue
                            else:
                                if game_object not in turn_entities:
                                    if game_object.is_player or isinstance(game_object, Enemy):
                                        TurnManager.add_entities(game_object)
                                        turn_entities.add(game_object)
                                updated_objects.add(game_object)
                                game_object.update(dt, events)

            for game_object in updated_objects:
                if game_object not in turn_entities:
                    TurnManager.remove_entities(game_object)


        def grid_to_world_pixel(self, x, y):
            x = ((x * Map.TILE_WIDTH) + self.x_offset) * self.x_parallax
            y = ((y * Map.TILE_HEIGHT) + self.y_offset) * self.y_parallax
            return x, y

        def world_pixel_to_grid(self, x, y):
            x = ((x) - self.x_offset)/Map.TILE_WIDTH
            y = ((y) - self.y_offset)/Map.TILE_HEIGHT
            return x, y