from cProfile import label
from re import A
from turtle import goto
import pygame
import sys
import yaml
import math
import time

from demo.Callout import CalloutManager
from demo.EnemyDropHandler import EnemyDropHandler
from demo.Pickup import LostPage, HealthPickup
from demo.SpellHUD import SpellHUD
from lib.Animation import Spawn
from lib.GridEntity import GridEntity
from lib.ImageHandler import ImageHandler
from lib.Map import Map
from lib.Camera import Camera
from lib.Primitives import Pose
from lib.Scene import TitleScreen, GameOverScreen
from lib.Settings import Settings
import random
from demo.Player import Player
from demo.Wall import Wall, Floor, Decorator, Exit, Stair
from demo.Enemy import Bat, Spider, Wolf, Slime, Orc, Shade, Dragon
from demo.TurnManager import TurnManager
from demo.CraftingMenu import CraftingMenu
from demo.ParticleHandler import ParticleHandler
import threading
import os
from lib.Math import lerp

class Game:
    def __init__(self):
        pygame.init()
        EnemyDropHandler.init()
        ImageHandler.init()
        CalloutManager.init()
        Camera.init()
        self.music = pygame.mixer.Sound("sounds/music.mp3")
        self.music.set_volume(0.3)
        self.music.play(-1)

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
        self.stored_player_letters = []

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
            rate = 3 if not self.game_over else 0.5
            self.shade_shown += dt * rate
            self.shade_shown = min(1, self.shade_shown)
            if self.shade_shown >= 1:
                self.end_level()
        self.black.set_alpha(self.shade_shown * 255)

    def run_game_from_menu(self):
        while True:
            self.run_menu()
            self.on_run_start()
            while True:
                self.main()
                if self.game_over:
                    self.run_game_over()
                    break

    def on_run_start(self):
        """
        Run when you first start a run
        """
        EnemyDropHandler.init()  # Don't keep drop history from previous run
        self.stored_player_spells = []  # Don't keep spells from previous run
        self.stored_player_letters = []
        Player.hit_points = Settings.Static.PLAYER_STARTING_HIT_POINTS  # in case we've gotten heart containers
        self.current_dungeon_level = 1
        self.game_over = False
        self.stored_player_health = Player.hit_points

    def run_game_over(self):
        menu_scene = GameOverScreen(self.current_dungeon_level)
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

        lerpAmount = (self.current_dungeon_level - 1)/6
        mapLength = int(lerp(2,7, lerpAmount))

        lerpAmount = (self.current_dungeon_level - 1) / 7
        mapExtraRooms = int(lerp(0, 9, lerpAmount))

        mapBossRoom = "rooms/boss_room_1.yaml"
        roomAttemptLimit = 20
        placementAttemptLimit = 60


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
        
        centerX = mapWidth//2
        centerY = mapHeight//2

        # Make array of wall tiles the size of the map to add rooms into
        stringMap = [wall * width for _ in range(height)] 

        # Spawn Room

        currentX = centerX
        currentY = centerY
        branchBaseX = centerX
        branchBaseY = centerY

        roomGrid = []

        #generate main path
        for mapGenAttempt in range(50):

            roomGrid = [[False for _ in range(mapWidth)] for _ in range(mapHeight)]
            roomGrid[centerX][centerY] = True

            mapData = []
            generationSuceeded = True
            for stepCount in range(mapLength):
                # DO NEXT STEP IN TO-BOSS PATH

                placementSucceded = False
                for roomAttemptCount in range(roomAttemptLimit):

                    # pick a room
                    if(stepCount == mapLength - 1):
                        room = self.get_yaml_room("rooms/special_rooms/exit_room.yaml")
                    else:
                        room = random.choice(rooms)

                    roomWidth = room["width"]
                    roomHeight = room["height"]

                    #place attempt code
                    for placeAttemptCount in range(placementAttemptLimit):

                        attemptX = random.randrange(-roomWidth, 2)
                        attemptY = random.randrange(-roomHeight, 2)

                        # If same space or not connected due to angle
                        if ((attemptX == 0 and attemptY == 0) or (abs(attemptX) == roomWidth and abs(attemptY) == roomHeight)):
                            continue

                        if not attemptX in range(-roomWidth + 1, 1) and not attemptY in range(-roomHeight + 1, 1):
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

            if generationSuceeded:
                break

        #spam extra rooms
        for extraRoomAttempts in range(mapExtraRooms):
            randomRoomX = random.randrange(0,Settings.Static.MAP_WIDTH)
            randomRoomY = random.randrange(0,Settings.Static.MAP_HEIGHT)
            #``````````````````````````

            placementSucceded = False
            for roomAttemptCount in range(50):

                # pick a room
                room = random.choice(rooms)
                roomWidth = room["width"]
                roomHeight = room["height"]

                # place attempt code
                for placeAttemptCount in range(placementAttemptLimit):

                    attemptX = random.randrange(-roomWidth, roomWidth + 1)
                    attemptY = random.randrange(-roomHeight, roomHeight + 1)

                    # If same space or not connected due to angle
                    if (attemptX == 0 and attemptY == 0) or (
                            abs(attemptX) == roomWidth and abs(attemptY) == roomHeight):
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

                    # place stuff time
                    for roomSpaceX in range(roomWidth):
                        for roomSpaceY in range(roomHeight):
                            roomGrid[roomSpaceX + attemptX][roomSpaceY + attemptY] = True

                    mapData.append([attemptX, attemptY, room])
                    currentX = attemptX
                    currentY = attemptY
                    placementSucceded = True
                    break

                if not placementSucceded:
                    continue

                break

            #````````````````````````

        if generationSuceeded:

            self.merge_room_onto_character_array(self.get_yaml_room("rooms/special_rooms/spawn_room.yaml"), stringMap,(centerX, centerY), closed_walls=[])

            #PURGE U D L R

            #PLACE ROOMS
            for roomToPlace in mapData:

                valid_chars = ["U", "D", "L", "R"]

                closed_walls = []
                try:
                    for blep in range(roomToPlace[2]["height"]):
                        if roomGrid[roomToPlace[0] - 1][roomToPlace[1]+blep]:
                            closed_walls.append("L")
                except:
                    pass

                try:
                    for blep in range(roomToPlace[2]["height"]):
                        if roomGrid[roomToPlace[0] + roomToPlace[2]["width"]][roomToPlace[1] + blep]:
                            closed_walls.append("R")
                except:
                    pass

                try:
                    for blep in range(roomToPlace[2]["width"]):
                        if roomGrid[roomToPlace[0] + blep][roomToPlace[1] - 1]:
                            closed_walls.append("U")
                except:
                    pass

                try:
                    for blep in range(roomToPlace[2]["width"]):
                        if roomGrid[roomToPlace[0] + blep][roomToPlace[1] + roomToPlace[2]["height"]]:
                            closed_walls.append("D")
                except:
                    pass

                for char in closed_walls:
                    if(char in valid_chars):
                        valid_chars.remove(char)

                self.merge_room_onto_character_array(roomToPlace[2], stringMap, (roomToPlace[0], roomToPlace[1]), valid_chars)
        else:
            self.merge_room_onto_character_array(self.get_yaml_room("rooms/special_rooms/backup.yaml"), stringMap,(centerX, centerY), closed_walls=[])

        self.mapdata = mapData;
        self.room_grid = roomGrid;
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
                elif item == "S":
                    new_tile = Stair()
                else:
                    new_tile = Floor()
                floor_layer.add_to_cell(new_tile, x, y)

        # Must do this to make sure tiles display right
        self.load_layer_sprites(floor_layer)
        for exit in exits:
            exit.open()  # must do after load_layer_sprites because of tileset rules
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

    def spawn_enemies(self, layer, player):
        enemies = 0
        enemy_objects = []
        frequency = 0.06

        enimies = [Bat, Wolf, Spider, Slime, Slime, Orc, Shade, Wolf, Spider, Slime, Orc, Shade, Dragon]


        if self.current_dungeon_level == 1:
            frequency = 0.02
            enemy_types = [Bat, Bat, Wolf]
        elif self.current_dungeon_level == 2:
            frequency = 0.0275
            enemy_types = [Bat, Wolf, Spider, Wolf]
        elif self.current_dungeon_level == 3:
            frequency = 0.035
            enemy_types = [Bat, Bat, Slime, Slime, Wolf]
        elif self.current_dungeon_level == 4:
            frequency = 0.035
            enemy_types = [Spider, Spider, Wolf, Spider, Spider, Shade, Wolf]
        elif self.current_dungeon_level == 5:
            frequency = 0.04
            enemy_types = [Spider, Bat, Bat, Slime, Slime, Spider, Bat, Bat, Slime, Slime, Orc]
        elif self.current_dungeon_level == 6:
            frequency = 0.0425
            enemy_types = [Orc, Shade, Orc, Shade, Orc, Shade, Bat]
        elif self.current_dungeon_level == 7:
            frequency = 0.4
            enemy_types = [Bat, Bat, Bat, Bat, Bat, Bat, Bat, Bat, Dragon, Dragon, Bat, Bat, Bat, Bat, Bat, Bat, Bat, Bat, Dragon, Dragon, Spider, Orc, Wolf, Spider] #replace with dragon
        elif self.current_dungeon_level == 42:
            frequency = 0.08
            enemy_types = [Slime]
        else:
            lerpAmount = (self.current_dungeon_level - 8)/40
            frequency = lerp(0.042, .15, lerpAmount)
            enemy_types = []

            for i in range(10):
                enemy_types.append(random.choice(enemies))

            if enemy_types == []:
                enemy_types = [Bat]
                frequency = .15

        for x, y in layer.cell_coordinates():
            if (Pose((x, y)) - Pose((7 + Settings.Static.ROOM_WIDTH * Settings.Static.MAP_WIDTH // 2, 7 + Settings.Static.ROOM_HEIGHT * Settings.Static.MAP_HEIGHT // 2)) ).magnitude() < 9:
                continue
            if not any([item.solid for item in layer.map.get_all_at_position(x, y)]) and random.random() < frequency:
                enemy_type = random.choice(enemy_types)
                enemy = enemy_type()
                enemy_objects.append(enemy)
                layer.add_to_cell(enemy, x, y)
                enemies += 1

        return enemy_objects

    def loading_anim(self):
        font = pygame.font.Font("fonts/smallest_pixel.ttf", 10)
        letters = [font.render(letter, 0, (255, 255, 255)) for letter in "LOADING"]
        width = sum([letter.get_width() for letter in letters])
        t = 0
        clock = pygame.time.Clock()
        while self.loading:
            x, y = Settings.Static.GAME_WIDTH // 2, Settings.Static.GAME_HEIGHT // 2
            i = 0
            x -= width // 2
            self.screen.fill((0, 0, 0))
            for letter in letters:
                i += 1
                self.screen.blit(letter, (x, y + math.sin(t * 8 - i)*2))
                x += letter.get_width()
            events = pygame.event.get()

            t += clock.tick()/1000

            scaled = pygame.transform.scale(self.screen, (Settings.Static.WINDOW_WIDTH, Settings.Static.WINDOW_HEIGHT))
            self.true_screen.blit(scaled, (0, 0))
            pygame.display.flip()


    def main(self):

        TurnManager.init()
        ParticleHandler.init()
        self.proceed_to_next_level = False
        self.ending = False
        self.starting = True

        self.loading = True
        t = threading.Thread(target=self.loading_anim, daemon=True)
        t.start()
        map = self.generate_map()
        self.loading = False

        player = Player()
        player.add_starting_spells(self.stored_player_spells)
        player.letter_tiles += self.stored_player_letters
        map.add_to_cell(player, 7 + Settings.Static.ROOM_WIDTH * Settings.Static.MAP_WIDTH//2, 7 + Settings.Static.ROOM_HEIGHT * Settings.Static.MAP_HEIGHT//2, 0)
        player.add_animation(Spawn(player))
        player.health = self.stored_player_health

        if self.current_dungeon_level > 1:
            pickup = LostPage()
            map.add_to_cell(pickup, player.position_on_grid.x - 2, player.position_on_grid.y, 0)
            pickup = HealthPickup()
            map.add_to_cell(pickup, player.position_on_grid.x +2, player.position_on_grid.y, 0)

        Camera.position = player.position.copy()
        spell_hud = SpellHUD(player)
        crafting_menu = CraftingMenu(player)
        enemies = self.spawn_enemies(map.get_layer(0), player)
        TurnManager.add_entities(player)
        vignette = ImageHandler.load("images/vignette.png")

        Camera.change_objects(objects=[player], weights=[1], mouse_weight=0.15)

        clock = pygame.time.Clock()
        clock.tick(60)

        if self.current_dungeon_level == 1:
            CalloutManager.post_message(CalloutManager.NEW_LEVEL, f"Level {self.current_dungeon_level}", "The Font's Fissure")
        elif self.current_dungeon_level == 2:
            CalloutManager.post_message(CalloutManager.NEW_LEVEL, f"Level {self.current_dungeon_level}", "Respite of Scholars")
        elif self.current_dungeon_level == 3:
            CalloutManager.post_message(CalloutManager.NEW_LEVEL, f"Level {self.current_dungeon_level}", "The Shattered Orthodoxy")
        elif self.current_dungeon_level == 4:
            CalloutManager.post_message(CalloutManager.NEW_LEVEL, f"Level {self.current_dungeon_level}", "Home of the Dialectics")
        elif self.current_dungeon_level == 5:
            CalloutManager.post_message(CalloutManager.NEW_LEVEL, f"Level {self.current_dungeon_level}", "The Lost Phrontistery")
        elif self.current_dungeon_level == 6:
            CalloutManager.post_message(CalloutManager.NEW_LEVEL, f"Level {self.current_dungeon_level}", "Athenaeum Storerooms")
        elif self.current_dungeon_level == 8:
            CalloutManager.post_message(CalloutManager.NEW_LEVEL, f"Level {self.current_dungeon_level}", "Arch of Knowledge")
        elif self.current_dungeon_level == 42:
            CalloutManager.post_message(CalloutManager.NEW_LEVEL, f"Level {self.current_dungeon_level}", "Lost dungeons of Gargabundle")
        else:
            CalloutManager.post_message(CalloutManager.NEW_LEVEL, f"Level {self.current_dungeon_level}", f"The Eternal Library, Shelf {self.current_dungeon_level - 8}")



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
            CalloutManager.update(dt, events)
            map.update(dt, events)
            crafting_menu.update(dt, events)
            map.draw(self.screen, offset)
            ParticleHandler.update(dt, events)
            ParticleHandler.draw(self.screen, offset=offset)

            self.screen.blit(vignette, (0, 0), special_flags=pygame.BLEND_MULT)

            self.draw_fps_font()

            crafting_menu.draw(self.screen, (0, 0))
            spell_hud.draw(self.screen, (10, 10))
            CalloutManager.draw(self.screen)
            if self.shade_shown > 0:
                self.screen.blit(self.black, (0, 0))

            scaled = pygame.transform.scale(self.screen, (Settings.Static.WINDOW_WIDTH, Settings.Static.WINDOW_HEIGHT))
            self.true_screen.blit(scaled, (0, 0))
            pygame.display.flip()

            if player.advanced or player.game_over:
                self.ending = True
                if player.game_over:
                    self.game_over = True
            if self.proceed_to_next_level:
                GridEntity.allies = []
                break

        self.stored_player_spells = player.spells_as_names()
        self.stored_player_letters = player.letter_tiles.copy()
        self.stored_player_health = player.health
        self.current_dungeon_level += 1


if __name__ == "__main__":
    Game()
