from lib.Settings import Settings


class Map:
    TILE_WIDTH = 32
    TILE_HEIGHT = 32
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
        for layer in self.layers:
            layer.draw(surface, offset=offset)

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
            from demo.Demo1 import Player
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
            for x, y in self._populated_cells:
                yield self.cells[y][x]

        def cell_coordinates(self):
            for y, row in enumerate(self.cells):
                for x, cell in enumerate(row):
                    yield x, y

        def populated_cells_and_coordinates(self):
            for x, y in self._populated_cells:
                yield self.cells[y][x], x, y

        def draw(self, surface, offset=(0, 0)):
            if not self._draws_enabled:
                return
            for cell, x, y in self.populated_cells_and_coordinates():
                wx, wy = self.grid_to_world_pixel(x, y)
                if not self.map.in_frame(wx+offset[0], wy+offset[1]):
                    continue
                for game_object in cell:
                    game_object.draw(surface, offset=offset)

        def update(self, dt, events):
            if not self._updates_enabled:
                return
            updated_objects = set()
            for cell in self.populated_cells():
                for game_object in cell:
                    if game_object in updated_objects:
                        continue
                    else:
                        updated_objects.add(game_object)
                        game_object.update(dt, events)

        def grid_to_world_pixel(self, x, y):
            x = ((x * Map.TILE_WIDTH) + self.x_offset) * self.x_parallax
            y = ((y * Map.TILE_HEIGHT) + self.y_offset) * self.y_parallax
            return x, y

        def world_pixel_to_grid(self, x, y):
            x = ((x/self.x_parallax) - self.x_offset)/Map.TILE_WIDTH
            y = ((y/self.y_parallax) - self.y_offset)/Map.TILE_HEIGHT
            return x, y