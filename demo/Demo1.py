import pygame
import sys
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


class Game:
    def __init__(self):
        pygame.init()
        ImageHandler.init()
        Camera.init()
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

    def generate_map(self):
        map = Map(21, 14)
        _entity_layer = map.add_empty_layer(0)
        floor_layer = map.add_empty_layer(1)
        floor_layer.enable_updates(False)  # Don't waste time calling update on floor tiles

        for x, y in floor_layer.cell_coordinates():
            if random.random() < 0.4:
                new_tile = Wall()
            else:
                new_tile = Floor()
            floor_layer.add_to_cell(new_tile, x, y)

        self.load_layer_sprites(floor_layer)
        return map

    def load_layer_sprites(self, layer):
        # This is necessary to pick the right tile sprites after the map has been generated
        for cell in layer.populated_cells():
            for tile in cell:
                tile.load_sprite()

    def main(self):
        clock = pygame.time.Clock()
        clock.tick(60)

        map = self.generate_map()
        player = Player()
        map.add_to_cell(player, 2, 2, 0)

        Camera.change_objects(objects=[player], weights=[1], mouse_weight=0.15)

        while True:
            dt = clock.tick(60)/1000
            events = pygame.event.get()

            self.screen.fill((0, 0, 0))

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

            scaled = pygame.transform.scale2x(self.screen)
            self.true_screen.blit(scaled, (0, 0))

            pygame.display.flip()



if __name__=="__main__":
    Game()
