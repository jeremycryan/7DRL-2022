from lib.GridEntity import GridEntity
from lib.ImageHandler import ImageHandler
from lib.Sprite import StaticSprite
from lib.Animation import ShrinkToNothing


class Pickup(GridEntity):

    is_pickup = True
    density = GridEntity.DENSITY_EMPTY

    def __init__(self):
        super().__init__()
        self.solid = False

    def on_pickup(self, pickupper):
        self.add_animation(ShrinkToNothing(self, 0.25))


class LetterTile(Pickup):

    def __init__(self, letter):
        super().__init__()
        self.letter = letter
        self.add_sprite(StaticSprite(ImageHandler.load(f"images/letters/UI_LETTER_{letter}.png"), colorkey=(255, 0, 255)))

    def on_pickup(self, pickupper):
        super().on_pickup(pickupper)
        if hasattr(pickupper, "letter_tiles"):
            pickupper.letter_tiles.append(self)


class LostPage(Pickup):

    def __init__(self):
        super().__init__()
        self.add_sprite(StaticSprite(ImageHandler.load("images/lost_page.png"), colorkey=(255, 0, 255)))


    def on_pickup(self, pickupper):
        super().on_pickup(pickupper)
        pickupper.learn_spell()
