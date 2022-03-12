from lib.ImageHandler import ImageHandler
from lib.GridEntity import GridEntity
from lib.Sprite import StaticSprite
from lib.Settings import Settings

import random


class Wall(GridEntity):
    density = GridEntity.DENSITY_WALL

    def __init__(self, position=(0, 0)):
        super().__init__(position)
        self.solid = True

    def load_sprite(self):
        surf = ImageHandler.load("images/tileset_engine.png")
        tw = Settings.Static.TILE_SIZE  # tile width

        self.add_grid_rule(StaticSprite(surf, rect=(tw, 0, tw, tw)), ("?.?", ".@S", "?.?"))
        self.add_grid_rule(StaticSprite(surf, rect=(2*tw, 0, tw, tw)), ("?.?", "S@S", "?.?"))
        self.add_grid_rule(StaticSprite(surf, rect=(3*tw, 0, tw, tw)), ("?.?", "S@S", ".SS"))
        self.add_grid_rule(StaticSprite(surf, rect=(4*tw, 0, tw, tw)), ("?.?", "S@S", "SS."))
        self.add_grid_rule(StaticSprite(surf, rect=(5*tw, 0, tw, tw)), ("?.?", "S@.", "?.?"))
        self.add_grid_rule(StaticSprite(surf, rect=(0, tw, tw, tw)), ("?.?", ".@.", "?S?"))
        self.add_grid_rule(StaticSprite(surf, rect=(tw, tw, tw, tw)), ("?.?", ".@S", "?SS"))
        self.add_grid_rule(StaticSprite(surf, rect=(2*tw, tw, tw, tw)), ("?.?", "S@S", "SSS"))
        self.add_grid_rule(StaticSprite(surf, rect=(3*tw, tw, tw, tw)), (".SS", "S@S", "SSS"))
        self.add_grid_rule(StaticSprite(surf, rect=(4*tw, tw, tw, tw)), ("SS.", "S@S", "SS."))
        self.add_grid_rule(StaticSprite(surf, rect=(5*tw, tw, tw, tw)), ("?.?", "S@S", ".S."))
        self.add_grid_rule(StaticSprite(surf, rect=(6*tw, tw, tw, tw)), ("?.?", "S@.", ".S?"))
        self.add_grid_rule(StaticSprite(surf, rect=(0, 2*tw, tw, tw)), ("?S?", ".@.", "?S?"))
        self.add_grid_rule(StaticSprite(surf, rect=(tw, 2*tw, tw, tw)), ("?SS", ".@S", "?SS"))
        self.add_grid_rule(StaticSprite(surf, rect=(2*tw, 2*tw, tw, tw)), ("SSS", "S@S", "SSS"))
        self.add_grid_rule(StaticSprite(surf, rect=(3*tw, 2*tw, tw, tw)), ("SSS", "S@S", "SS."))
        self.add_grid_rule(StaticSprite(surf, rect=(4*tw, 2*tw, tw, tw)), ("SS.", "S@S", ".SS"))
        self.add_grid_rule(StaticSprite(surf, rect=(5*tw, 2*tw, tw, tw)), (".S.", "S@S", "SSS"))
        self.add_grid_rule(StaticSprite(surf, rect=(6*tw, 2*tw, tw, tw)), (".S?", "S@.", "SS?"))
        self.add_grid_rule(StaticSprite(surf, rect=(0, 3*tw, tw, tw)), ("?S.", ".@S", "?SS"))
        self.add_grid_rule(StaticSprite(surf, rect=(tw, 3*tw, tw, tw)), (".SS", "S@S", "SS."))
        self.add_grid_rule(StaticSprite(surf, rect=(2*tw, 3*tw, tw, tw)), ("SSS", "S@S", ".S."))
        self.add_grid_rule(StaticSprite(surf, rect=(3*tw, 3*tw, tw, tw)), ("SS?", "S@.", "?.?"))
        self.add_grid_rule(StaticSprite(surf, rect=(4*tw, 3*tw, tw, tw)), ("?SS", ".@S", "?.?"))
        self.add_grid_rule(StaticSprite(surf, rect=(5*tw, 3*tw, tw, tw)), ("SSS", "S@S", ".SS"))
        self.add_grid_rule(StaticSprite(surf, rect=(6*tw, 3*tw, tw, tw)), ("SS?", "S@.", "SS?"))
        self.add_grid_rule(StaticSprite(surf, rect=(0, 4*tw, tw, tw)), ("?SS", ".@S", "?S."))
        self.add_grid_rule(StaticSprite(surf, rect=(tw, 4*tw, tw, tw)), ("SS.", "S@S", ".S."))
        self.add_grid_rule(StaticSprite(surf, rect=(2*tw, 4*tw, tw, tw)), (".S.", "S@S", ".SS"))
        self.add_grid_rule(StaticSprite(surf, rect=(3*tw, 4*tw, tw, tw)), ("?.?", "S@.", "SS?"))
        self.add_grid_rule(StaticSprite(surf, rect=(4*tw, 4*tw, tw, tw)), ("?.?", ".@S", "?S."))
        self.add_grid_rule(StaticSprite(surf, rect=(5*tw, 4*tw, tw, tw)), (".SS", "S@S", ".S."))
        self.add_grid_rule(StaticSprite(surf, rect=(6*tw, 4*tw, tw, tw)), ("SS?", "S@.", ".S?"))
        self.add_grid_rule(StaticSprite(surf, rect=(0, 5*tw, tw, tw)), ("?S?", ".@.", "?.?"))
        self.add_grid_rule(StaticSprite(surf, rect=(tw, 5*tw, tw, tw)), ("?S.", ".@S", "?S."))
        self.add_grid_rule(StaticSprite(surf, rect=(2*tw, 5*tw, tw, tw)), (".SS", "S@S", ".SS"))
        self.add_grid_rule(StaticSprite(surf, rect=(3*tw, 5*tw, tw, tw)), ("SS.", "S@S", "SSS"))
        self.add_grid_rule(StaticSprite(surf, rect=(4*tw, 5*tw, tw, tw)), (".S.", "S@S", "SS."))
        self.add_grid_rule(StaticSprite(surf, rect=(5*tw, 5*tw, tw, tw)), (".S.", "S@S", ".S."))
        self.add_grid_rule(StaticSprite(surf, rect=(6*tw, 5*tw, tw, tw)), (".S?", "S@.", ".S?"))
        self.add_grid_rule(StaticSprite(surf, rect=(0, 6*tw, tw, tw)), ("?.?", ".@.", "?.?"))
        self.add_grid_rule(StaticSprite(surf, rect=(tw, 6*tw, tw, tw)), ("?S.", ".@S", "?.?"))
        self.add_grid_rule(StaticSprite(surf, rect=(2*tw, 6*tw, tw, tw)), (".SS", "S@S", "?.?"))
        self.add_grid_rule(StaticSprite(surf, rect=(3*tw, 6*tw, tw, tw)), ("SSS", "S@S", "?.?"))
        self.add_grid_rule(StaticSprite(surf, rect=(4*tw, 6*tw, tw, tw)), ("SS.", "S@S", "?.?"))
        self.add_grid_rule(StaticSprite(surf, rect=(5*tw, 6*tw, tw, tw)), (".S.", "S@S", "?.?"))
        self.add_grid_rule(StaticSprite(surf, rect=(6*tw, 6*tw, tw, tw)), (".S?", "S@.", "?.?"))

        # Default tile in case we've missed something
        self.add_grid_rule(StaticSprite(surf, rect=(6*tw, 0, tw, tw)), ("@",))

        # Use rules to find the most appropriate sprite
        self.add_sprite(self.get_sprite_from_grid_rules())


class Floor(Wall):
    density = GridEntity.DENSITY_EMPTY

    def __init__(self, position=(0, 0)):
        super().__init__(position)
        self.solid = False

    def load_sprite(self):
        surf = ImageHandler.load("images/tileset_engine.png")
        tw = Settings.Static.TILE_SIZE  # tile width

        rect = random.choice(
            (
                (0, 0, tw, tw),
                (6*tw, 0, tw, tw),
            )
        )
        self.add_sprite(StaticSprite(surf, rect=rect))

    def draw(self, surface, offset=(0, 0)):
        super().draw(surface, offset)


class Exit(Wall):

    def open(self):
        self.solid = False

    def load_sprite(self):
        surf = ImageHandler.load("images/Wall_Exit_Open.png")
        self.add_sprite(StaticSprite(surf, rect=surf.get_rect()))


class Decorator(GridEntity):
    density = GridEntity.DENSITY_EMPTY

    def __init__(self, is_floor):
        self.is_floor = is_floor
        super().__init__()
        self.solid = False
        self.load_sprite()

    def load_sprite(self):
        if self.is_floor:
            valid_paths = [
                "Floor_Blood.png",
                "Floor_Bones.png",
                "Floor_Puddle.png",
                "Floor_Rocks1.png",
                "Floor_Rocks2.png",
                #"Floor_Torch.png"
            ]
        else:
            valid_paths = [
                "Wall_Blood.png",
                "Wall_Bones.png",
                "Wall_Moss.png",
                "Wall_Eyes.png",
                "Wall_Torch.png"
            ]
        path = random.choice(valid_paths)
        if path == "Floor_Torch.png":
            self.solid = True
        path = f"images/decorators/{path}"
        self.add_sprite(StaticSprite(ImageHandler.load(path), rect=(0, 0, 32, 32), colorkey=(255, 0, 255)))
