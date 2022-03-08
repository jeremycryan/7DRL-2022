from lib.GridEntity import GridEntity
from lib.ImageHandler import ImageHandler
from lib.Sprite import StaticSprite, InvisibleSprite


class Enemy(GridEntity):
    name = "ENEMY"
    hit_points = 1


    def __init__(self):
        super().__init__()
        self.sprite = self.load_sprite()

    def load_sprite(self):
        """
        By default, return an invisible sprite.
        :return:
        """
        return InvisibleSprite()
