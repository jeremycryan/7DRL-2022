import pygame
import sys
from lib.ImageHandler import ImageHandler
from lib.Map import Map
from lib.GridEntity import GridEntity
from lib.Sprite import StaticSprite
from lib.Settings import Settings
import random


class Player(GridEntity):
    def __init__(self, position=(0, 0)):
        super().__init__(position)
        sprite = StaticSprite.from_path("images/pigeon.png")
        sprite.set_alpha(200)
        sprite.set_colorkey((255, 0, 255))
        self.sprites.append(sprite)

    def update(self, dt, events):
        super().update(dt, events)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.move(y=-1)
                if event.key == pygame.K_s:
                    self.move(y=1)
                if event.key == pygame.K_a:
                    self.move(x=-1)
                if event.key == pygame.K_d:
                    self.move(x=1)


class Wall(GridEntity):
    def __init__(self, position=(0, 0)):
        super().__init__(position)
        self.solid = True

    def load_sprite(self):
        surf = ImageHandler.load("images/tileset.png")
        tw = 64  # tile width

        # Big donut
        self.add_grid_rule(StaticSprite(surf, rect=(0, 0, tw, tw)), ("SSS", "S@S", "SS."))
        self.add_grid_rule(StaticSprite(surf, rect=(tw, 0, tw, tw)), ("SSS", "S@S", "?.?"))
        self.add_grid_rule(StaticSprite(surf, rect=(2*tw, 0, tw, tw)), ("SSS", "S@S", ".SS"))
        self.add_grid_rule(StaticSprite(surf, rect=(0, tw, tw, tw)), ("SS?", "S@.", "SS?"))
        self.add_grid_rule(StaticSprite(surf, rect=(2*tw, tw, tw, tw)), ("?SS", ".@S", "?SS"))
        self.add_grid_rule(StaticSprite(surf, rect=(0, 2*tw, tw, tw)), ("SS.", "S@S", "SSS"))
        self.add_grid_rule(StaticSprite(surf, rect=(tw, 2*tw, tw, tw)), ("?.?", "S@S", "SSS"))
        self.add_grid_rule(StaticSprite(surf, rect=(2*tw, 2*tw, tw, tw)), (".SS", "S@S", "SSS"))

        # Big vertical waffle
        self.add_grid_rule(StaticSprite(surf, rect=(3*tw, 0, tw, tw)), ("?SS", ".@S", "?S."))
        self.add_grid_rule(StaticSprite(surf, rect=(4*tw, 0, tw, tw)), ("SSS", "S@S", ".S."))
        self.add_grid_rule(StaticSprite(surf, rect=(5*tw, 0, tw, tw)), ("SS?", "S@.", ".S?"))
        self.add_grid_rule(StaticSprite(surf, rect=(3*tw, tw, tw, tw)), ("?S.", ".@S", "?S."))
        self.add_grid_rule(StaticSprite(surf, rect=(4*tw, tw, tw, tw)), (".S.", "S@S", ".S."))
        self.add_grid_rule(StaticSprite(surf, rect=(5*tw, tw, tw, tw)), (".S?", "S@.", ".S?"))
        self.add_grid_rule(StaticSprite(surf, rect=(3*tw, 2*tw, tw, tw)), ("?S.", ".@S", "?SS"))
        self.add_grid_rule(StaticSprite(surf, rect=(4*tw, 2*tw, tw, tw)), (".S.", "S@S", "SSS"))
        self.add_grid_rule(StaticSprite(surf, rect=(5*tw, 2*tw, tw, tw)), (".S?", "S@.", "SS?"))

        # Big horizontal waffle
        self.add_grid_rule(StaticSprite(surf, rect=(0, 3*tw, tw, tw)), ("?.?", "S@S", "SS."))
        self.add_grid_rule(StaticSprite(surf, rect=(tw, 3*tw, tw, tw)), ("?.?", "S@S", ".S."))
        self.add_grid_rule(StaticSprite(surf, rect=(2*tw, 3*tw, tw, tw)), ("?.?", "S@S", ".SS"))
        self.add_grid_rule(StaticSprite(surf, rect=(0, 4*tw, tw, tw)), ("SS.", "S@S", "SS."))
        self.add_grid_rule(StaticSprite(surf, rect=(tw, 4*tw, tw, tw)), (".S.", "S@S", ".S."))
        self.add_grid_rule(StaticSprite(surf, rect=(2*tw, 4*tw, tw, tw)), (".SS", "S@S", ".SS"))
        self.add_grid_rule(StaticSprite(surf, rect=(0, 5*tw, tw, tw)), ("SS.", "S@S", "?.?"))
        self.add_grid_rule(StaticSprite(surf, rect=(tw, 5*tw, tw, tw)), (".S.", "S@S", "?.?"))
        self.add_grid_rule(StaticSprite(surf, rect=(2*tw, 5*tw, tw, tw)), (".SS", "S@S", "?.?"))

        # Solid wall
        self.add_grid_rule(StaticSprite(surf, rect=(tw, tw, tw, tw)), ("SSS", "S@S", "SSS"), likelihood=0.5)
        self.add_grid_rule(StaticSprite(surf, rect=(tw, 4*tw, tw, tw)), ("SSS", "S@S", "SSS"))

        # Small donut
        self.add_grid_rule(StaticSprite(surf, rect=(5*tw, 3*tw, tw, tw)), ("?.?", ".@S", "?S."))
        self.add_grid_rule(StaticSprite(surf, rect=(5*tw, 4*tw, tw, tw)), ("?S.", ".@S", "?.?"))
        self.add_grid_rule(StaticSprite(surf, rect=(6*tw, 3*tw, tw, tw)), ("?.?", "S@.", ".S?"))
        self.add_grid_rule(StaticSprite(surf, rect=(6*tw, 4*tw, tw, tw)), (".S?", "S@.", "?.?"))

        # Small square
        self.add_grid_rule(StaticSprite(surf, rect=(3*tw, 3*tw, tw, tw)), ("?.?", ".@S", "?SS"))
        self.add_grid_rule(StaticSprite(surf, rect=(3*tw, 4*tw, tw, tw)), ("?SS", ".@S", "?.?"))
        self.add_grid_rule(StaticSprite(surf, rect=(4*tw, 3*tw, tw, tw)), ("?.?", "S@.", "SS?"))
        self.add_grid_rule(StaticSprite(surf, rect=(4*tw, 4*tw, tw, tw)), ("SS?", "S@.", "?.?"))

        # Skinny vertical bit
        self.add_grid_rule(StaticSprite(surf, rect=(6*tw, 0, tw, tw)), ("?.?", ".@.", "?S?"))
        self.add_grid_rule(StaticSprite(surf, rect=(6*tw, tw, tw, tw)), ("?S?", ".@.", "?S?"))
        self.add_grid_rule(StaticSprite(surf, rect=(6*tw, 2*tw, tw, tw)), ("?S?", ".@.", "?.?"))

        # Skinny horizontal bit
        self.add_grid_rule(StaticSprite(surf, rect=(0, 6*tw, tw, tw)), ("?.?", ".@S", "?.?"))
        self.add_grid_rule(StaticSprite(surf, rect=(tw, 6*tw, tw, tw)), ("?.?", "S@S", "?.?"))
        self.add_grid_rule(StaticSprite(surf, rect=(2*tw, 6*tw, tw, tw)), ("?.?", "S@.", "?.?"))

        # Single block
        self.add_grid_rule(StaticSprite(surf, rect=(6*tw, 5*tw, tw, tw)), ("?.?", ".@.", "?.?"))

        # Default tile in case we've missed something
        self.add_grid_rule(StaticSprite(surf, rect=(0, 0, tw, tw)), ("@",))

        # Use rules to find the most appropriate sprite
        self.add_sprite(self.get_sprite_from_grid_rules())


class Floor(Wall):
    def __init__(self, position=(0, 0)):
        super().__init__(position)
        self.solid = False

    def load_sprite(self):
        surf = ImageHandler.load("images/tileset.png")
        tw = 64  # tile width

        rect = random.choice(
            (
                (3*tw, 5*tw, tw, tw),
                (4*tw, 5*tw, tw, tw),
                (5*tw, 5*tw, tw, tw),
            )
        )
        self.add_sprite(StaticSprite(surf, rect=rect))

    def draw(self, surface, offset=(0, 0)):
        super().draw(surface, offset)


class Game:
    def __init__(self):
        pygame.init()
        ImageHandler.init()
        self.screen = pygame.display.set_mode((1280, 720))
        self.fps_font = pygame.font.SysFont("monospace", 16, 1, 0)
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

        surf = self.fps_font.render(f"FPS:{' '*max(0,6-len(fps))}{fps}", True, (255, 255, 255))
        self.screen.blit(surf, (10, 10))

    def main(self):
        clock = pygame.time.Clock()
        clock.tick(60)
        map = Map(20, 20)
        map.add_empty_layer(0)
        floor_layer = map.add_empty_layer(1)

        for x, y in floor_layer.cell_coordinates():
            if random.random() < 0.4:
                new_tile = Wall()
            else:
                new_tile = Floor()
            floor_layer.add_to_cell(new_tile, x, y)
            new_tile.move_to_grid_position(x, y)

        for cell in floor_layer.populated_cells():
            for tile in cell:
                tile.load_sprite()

        player = Player((0, 0))
        map.add_to_cell(player, 2, 2, 0)

        while True:
            dt = clock.tick(60)/1000
            events = pygame.event.get()

            self.screen.fill((0, 0, 0))

            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

            self.update_fpss(dt, events)
            map.update(dt, events)
            map.draw(self.screen, (0, 0))
            self.draw_fps_font()

            pygame.display.flip()



if __name__=="__main__":
    Game()
