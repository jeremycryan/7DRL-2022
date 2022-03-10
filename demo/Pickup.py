from lib.GridEntity import GridEntity
from lib.ImageHandler import ImageHandler
from lib.Sprite import StaticSprite

class Pickup(GridEntity):

    is_pickup = True

    def __init__(self):
        super().__init__()
        self.solid = False

    def on_pickup(self, pickupper):
        self.destroy()

class LetterTile(Pickup):

    def __init__(self, letter):
        super().__init__()
        self.letter = letter
        self.add_sprite(StaticSprite(ImageHandler.load("images/big_tile.png"), colorkey=(255, 0, 255)))
