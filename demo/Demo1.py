import pygame
import sys
import yaml

from demo.SpellHUD import SpellHUD
from lib.ImageHandler import ImageHandler
from lib.Map import Map
from lib.GridEntity import GridEntity
from lib.Sprite import StaticSprite
from lib.Camera import Camera
from lib.Settings import Settings
import random
import time
from demo.Player import Player
from demo.Wall import Wall, Floor
from demo.Enemy import Goomba
from demo.TurnManager import TurnManager


class Game:
    def __init__(self):
        pygame.init()
        ImageHandler.init()
        Camera.init()
        TurnManager.init()
        self.screen = pygame.Surface((640, 360))
        self.true_screen = pygame.display.set_mode((1280, 720))
        self.fps_font = pygame.font.SysFont("monospace", 10, 1, 0)
        self.fpss = []
        self.main()

    def update_fpss(self, dt, events):
        self.fpss.append(dt)
        self.fpss = self.fpss[-100:]

    def draw_fps_font(self):
        avg_dt = sum(self.fpss)/len(self.fpss)
        if avg_dt == 0:
            fps = "Very high"
        else:
            fps = str(int(len(self.fpss)/sum(self.fpss)))

        surf = self.fps_font.render(f"FPS:{' '*max(0,6-len(fps))}{fps}", False, (255, 255, 255))
        self.screen.blit(surf, (10, 10))

    def get_yaml_room(self, path):
        """
        Loads a room from a yaml file. Returns None if no path is found.
        :param path: The file path
        :return: The contents of the yaml file or None
        """
        try:
            with open(path) as file:
                return yaml.safe_load(file)
        except:
            return None

    @staticmethod
    def merge_room_onto_character_array(room, array, origin=(0, 0), closed_walls=""):
        """
        Copies the contents of the room onto the array, overwriting any prior contents
        :param room: An object with property "tiles" that contains a list of strings
        :param array: A list of strings
        :param origin: The top left coordinate of the room, in room coordinates.
        :param closed_walls: An iterable of characters that should be treated as walls when the room is merged. Probably
            some combination of U, D, L, R for the temporary walls.
        """
        tiles = room["tiles"]
        th = len(tiles)
        tw = len(tiles[0])

        origin = origin[0] * Settings.Static.ROOM_WIDTH, origin[1] * Settings.Static.ROOM_HEIGHT

        for y, row in enumerate(array):
            new_row = ""
            for x, item in enumerate(row):
                if 0 <= y - origin[1] < th and 0 <= x - origin[0] < tw:
                    char = tiles[y - origin[1]][x - origin[0]]
                    if char in closed_walls:
                        char = "X"
                    new_row += char
                else:
                    new_row += item
            array[y] = new_row

    def generate_map(self):
        # TODO: Somehow determine a good height for the map, in tiles.
        width = Settings.Static.ROOM_WIDTH * 2
        height = Settings.Static.ROOM_HEIGHT * 2

        # Don't change any of this
        map = Map(width, height)
        _entity_layer = map.add_empty_layer(0)
        floor_layer = map.add_empty_layer(1)
        floor_layer.enable_updates(False)  # Don't waste time calling update on floor tiles

        # Using rooms from yaml, assemble the map.
        # TODO Daniel improve this section
        wall = "X"
        floor = "."
        up, down, left, right = "U", "D", "L", "R"
        rooms = [
            self.get_yaml_room("rooms/room_1.yaml")
        ]
        tile_array = [wall * width for _ in range(height)]  # Make array of wall tiles the size of the map to add rooms into
        for y in range(2):
            for x in range(2):
                room = random.choice(rooms)
                self.merge_room_onto_character_array(room, tile_array, (x, y), closed_walls=[up])

        # Turn our room array back into a map.
        for y, row in enumerate(tile_array):
            for x, item in enumerate(row):
                if item is wall:
                    new_tile = Wall()
                else:
                    new_tile = Floor()
                floor_layer.add_to_cell(new_tile, x, y)

        # Must do this to make sure tiles display right
        self.load_layer_sprites(floor_layer)

        return map

    def load_layer_sprites(self, layer):
        # This is necessary to pick the right tile sprites after the map has been generated
        for cell in layer.populated_cells():
            for tile in cell:
                tile.load_sprite()

    def spawn_enemies(self, layer):
        enemies = 0
        enemy_objects = []
        for x, y in layer.cell_coordinates():
            if not any([item.solid for item in layer.map.get_all_at_position(x, y)]) and random.random() < 0.06:
                enemy = Goomba()
                enemy_objects.append(enemy)
                layer.add_to_cell(enemy, x, y)
                enemies += 1

        return enemy_objects

    def main(self):
        clock = pygame.time.Clock()
        clock.tick(60)

        map = self.generate_map()
        player = Player()
        map.add_to_cell(player, 2, 2, 0)
        spell_hud = SpellHUD(player)
        enemies = self.spawn_enemies(map.get_layer(0))
        TurnManager.add_entities(player, *enemies)

        Camera.change_objects(objects=[player], weights=[1], mouse_weight=0.15)

        while True:
            dt = clock.tick(60)/1000
            events = pygame.event.get()

            self.screen.fill((0, 0, 0))

            TurnManager.take_next_turn()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

            offset = Camera.get_game_offset().get_position()

            self.update_fpss(dt, events)
            Camera.update(dt, events)
            map.update(dt, events)
            map.draw(self.screen, offset)
            self.draw_fps_font()

            spell_hud.draw(self.screen, (10, 10))

            scaled = pygame.transform.scale2x(self.screen)
            self.true_screen.blit(scaled, (0, 0))

            pygame.display.flip()



if __name__=="__main__":
    Game()
