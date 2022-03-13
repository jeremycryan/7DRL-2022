from cProfile import label
from re import A
from turtle import goto
import pygame
import sys
import yaml

from demo.EnemyDropHandler import EnemyDropHandler
from demo.SpellHUD import SpellHUD
from lib.Animation import Spawn
from lib.GridEntity import GridEntity
from lib.ImageHandler import ImageHandler
from lib.Map import Map
from lib.Camera import Camera
from lib.Scene import TitleScreen
from lib.Settings import Settings
import random
from demo.Player import Player
from demo.Wall import Wall, Floor, Decorator, Exit
from demo.Enemy import Bat, Spider, Wolf, Slime, Orc, Shade
from demo.TurnManager import TurnManager
from demo.CraftingMenu import CraftingMenu
from demo.ParticleHandler import ParticleHandler
import os

class Game:
    def __init__(self):
        pygame.init()
        EnemyDropHandler.init()
        ImageHandler.init()
        Camera.init()

        self.screen = pygame.Surface((640, 360))
        self.true_screen = pygame.display.set_mode((1280, 720))
        self.fps_font = pygame.font.SysFont("monospace", 10, 1, 0)
        self.fpss = []
        pygame.display.set_caption(Settings.Static.WINDOW_CAPTION)

        self.black = pygame.Surface((Settings.Static.GAME_WIDTH, Settings.Static.GAME_HEIGHT))
        self.black.fill((0, 0, 0))
        self.shade_shown = 1
        self.starting = True
        self.ending = False
        self.proceed_to_next_level = False
        self.stored_player_spells = []

        self.run_game_from_menu()

    def end_level(self):
        self.proceed_to_next_level = True

    def update_shade(self, dt, events):
        if self.starting:
            self.shade_shown -= dt * 2
            self.shade_shown = max(0, self.shade_shown)
            if self.shade_shown <= 0:
                self.starting = False
        if self.ending:
            self.shade_shown += dt * 3
            self.shade_shown = min(1, self.shade_shown)
            if self.shade_shown >= 1:
                self.end_level()
        self.black.set_alpha(self.shade_shown * 255)

    def run_game_from_menu(self):
        self.run_menu()
        self.on_run_start()
        while True:
            self.main()

    def on_run_start(self):
        """
        Run when you first start a run
        """
        EnemyDropHandler.init()  # Don't keep drop history from previous run
        self.stored_player_spells = []  # Don't keep spells from previous run

    def run_menu(self):
        menu_scene = TitleScreen()
        clock = pygame.time.Clock()
        clock.tick(60)
        while not menu_scene.is_over():
            events = pygame.event.get()
            dt = clock.tick(60)/1000
            menu_scene.update(dt, events)
            menu_scene.draw(self.screen, (0, 0))

            scaled = pygame.transform.scale(self.screen, (Settings.Static.WINDOW_WIDTH, Settings.Static.WINDOW_HEIGHT))
            self.true_screen.blit(scaled, (0, 0))
            pygame.display.flip()

            pygame.display.flip()

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
        self.screen.blit(surf, (10, 340))

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

        mapLength = 6
        mapBossRoom = "rooms/boss_room_1.yaml"
        mapBranchLength = 0
        mapBranchChance = 0
        roomAttemptLimit = 30
        placementAttemptLimit = 30


        # TODO: Somehow determine a good height for the map, in tiles.
        mapWidth = Settings.Static.MAP_WIDTH
        mapHeight = Settings.Static.MAP_HEIGHT

        width = Settings.Static.ROOM_WIDTH * mapWidth
        height = Settings.Static.ROOM_HEIGHT * mapHeight

        # Don't change any of this
        map = Map(width, height)
        _entity_layer = map.add_empty_layer(0)
        _pickup_layer = map.add_empty_layer(Settings.Static.PICKUP_LAYER)
        floor_layer = map.add_empty_layer(1)
        floor_layer.enable_updates(False)  # Don't waste time calling update on floor tiles

        # Using rooms from yaml, assemble the map.
        # TODO Daniel improve this section
        
        wall = "X"
        floor = "."
        up, down, left, right = "U", "D", "L", "R"

        PATHS = os.listdir("rooms/small_rooms")

        rooms = []
        for path in PATHS:
            rooms.append(self.get_yaml_room("rooms/small_rooms/" + path))
        
        roomGrid = [[False for _ in range(mapWidth)] for _ in range(mapHeight)]
        centerX = mapWidth//2
        centerY = mapHeight//2

        # Make array of wall tiles the size of the map to add rooms into
        stringMap = [wall * width for _ in range(height)] 

        # Spawn Room
        self.merge_room_onto_character_array(self.get_yaml_room("rooms/special_rooms/spawn_room.yaml"), stringMap, (centerX, centerY), closed_walls=[])
        roomGrid[centerX][centerY] = True

        currentX = centerX
        currentY = centerY
        branchBaseX = centerX
        branchBaseY = centerY

        mapData = [] 

        generationSuceeded = True
        for stepCount in range(mapLength):
            # DO NEXT STEP IN TO-BOSS PATH

            placementSucceded = False
            for roomAttemptCount in range(roomAttemptLimit):
                
                # pick a room
                room = random.choice(rooms)
                roomWidth = room["width"]
                roomHeight = room["height"]

                #place attempt code
                for placeAttemptCount in range(placementAttemptLimit):

                    attemptX = random.randrange(-roomWidth, roomWidth+1)
                    attemptY = random.randrange(-roomHeight, roomHeight+1)
                    
                    # If same space or not connected due to angle
                    if (attemptX == 0 and attemptY == 0) or (abs(attemptX) == roomWidth and abs(attemptY) == roomHeight):
                        continue

                    attemptX = currentX + attemptX
                    attemptY = currentY + attemptY

                    # checking logic here

                    placementAllowed = True
                    for roomSpaceX in range(roomWidth):
                        for roomSpaceY in range(roomHeight):
                            try:
                                if roomGrid[roomSpaceX + attemptX][roomSpaceY + attemptY]:
                                    placementAllowed = False
                            except:
                                placementAllowed = False

                    if not placementAllowed:
                        continue

                    #place stuff time
                    for roomSpaceX in range(roomWidth):
                        for roomSpaceY in range(roomHeight):
                            roomGrid[roomSpaceX + attemptX][roomSpaceY +attemptY] = True

                    mapData.append([attemptX, attemptY, room])
                    currentX = attemptX
                    currentY = attemptY
                    placementSucceded = True
                    break

                if not placementSucceded:
                    continue

                break

            if not placementSucceded:
                generationSuceeded = False
                break
            #if random.random() < mapBranchChance:
            #    # MAKE BRANCH
            #    for _ in random.randrange(mapBranchLength - 1 , mapBranchLength + 2):
            #
            #        testX = random.choice(range(mapWidth))
            #        testY = random.choice(range(mapWidth))





                    #x and y are in room coordinates
                    #self.merge_room_onto_character_array(room, stringMap, (x, y), closed_walls=[up])

        if generationSuceeded:
            for roomToPlace in mapData:
                self.merge_room_onto_character_array(roomToPlace[2], stringMap, (roomToPlace[0], roomToPlace[1]), closed_walls=[])

        #apply U D L R in tile_array into floors based on room coordinates
        #searches based on room coordinate

        # Turn our room array back into a map.
        exits = []
        for y, row in enumerate(stringMap):
            for x, item in enumerate(row):
                if item is wall:
                    new_tile = Wall()
                elif item is wall:
                    new_tile = Wall()
                elif item == "E":
                    new_tile = Exit()
                    exits.append(new_tile)
                else:
                    new_tile = Floor()
                floor_layer.add_to_cell(new_tile, x, y)

        # Must do this to make sure tiles display right
        self.load_layer_sprites(floor_layer)
        for exit in exits:
            exit.solid = False  # must do after load_layer_sprites because of tileset rules
        self.add_decorators(map)

        return map
    
    def tryPlaceRoom(self):
        pass

    def add_decorators(self, map):
        new_layer = map.add_empty_layer(Settings.Static.DECORATOR_LAYER)
        floor_layer = map.get_layer(1)
        for cell, x, y in floor_layer.populated_cells_and_coordinates():
            for item in cell:
                if type(item) == Floor:
                    if random.random() < 0.03:
                        self.add_decorator(new_layer, x, y, True)
                    break
                if type(item) == Wall:
                    if new_layer.cell_in_range(x, y+1):
                        cell = map.get_layer(1).peek_at_cell(x, y+1)
                        for item in cell:
                            if type(item) == Floor:
                                if random.random() < 0.1:
                                    self.add_decorator(new_layer, x, y, False)
                                    break
                    break

    def add_decorator(self, layer, x, y, is_floor):
        layer.add_to_cell(Decorator(is_floor), x, y)

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
                enemy_type = random.choice([Bat, Spider, Wolf, Slime, Orc, Shade])
                enemy = enemy_type()
                enemy_objects.append(enemy)
                layer.add_to_cell(enemy, x, y)
                enemies += 1

        return enemy_objects

    def main(self):

        TurnManager.init()
        ParticleHandler.init()
        self.proceed_to_next_level = False
        self.ending = False
        self.starting = True

        map = self.generate_map()
        player = Player()
        player.add_starting_spells(self.stored_player_spells)
        map.add_to_cell(player, 7 + Settings.Static.ROOM_WIDTH * Settings.Static.MAP_WIDTH//2, 7 + Settings.Static.ROOM_HEIGHT * Settings.Static.MAP_HEIGHT//2, 0)
        player.add_animation(Spawn(player))
        Camera.position = player.position.copy()
        spell_hud = SpellHUD(player)
        crafting_menu = CraftingMenu(player)
        enemies = self.spawn_enemies(map.get_layer(0))
        TurnManager.add_entities(player, *enemies)
        vignette = ImageHandler.load("images/vignette.png")

        Camera.change_objects(objects=[player], weights=[1], mouse_weight=0.15)

        clock = pygame.time.Clock()
        clock.tick(60)

        while True:
            dt = clock.tick(120)/1000
            if dt > 0.15:
                dt = 0.15
            events = pygame.event.get()

            self.screen.fill((0, 0, 0))

            TurnManager.take_next_turn()

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

            offset = Camera.get_game_offset().get_position()

            self.update_fpss(dt, events)
            self.update_shade(dt, events)
            spell_hud.update(dt, events)
            Camera.update(dt, events)
            map.update(dt, events)
            crafting_menu.update(dt, events)
            map.draw(self.screen, offset)
            ParticleHandler.update(dt, events)
            ParticleHandler.draw(self.screen, offset=offset)

            self.screen.blit(vignette, (0, 0), special_flags=pygame.BLEND_MULT)

            self.draw_fps_font()

            crafting_menu.draw(self.screen, (0, 0))
            spell_hud.draw(self.screen, (10, 10))
            if self.shade_shown > 0:
                self.screen.blit(self.black, (0, 0))

            scaled = pygame.transform.scale(self.screen, (Settings.Static.WINDOW_WIDTH, Settings.Static.WINDOW_HEIGHT))
            self.true_screen.blit(scaled, (0, 0))
            pygame.display.flip()

            if player.advanced:
                self.ending = True
            if self.proceed_to_next_level:
                GridEntity.allies = []
                break

        self.stored_player_spells = player.spells_as_names()


if __name__ == "__main__":
    Game()
