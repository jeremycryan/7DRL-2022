from lib.GridEntity import GridEntity
from lib.Sprite import StaticSprite

import pygame


class Player(GridEntity):
    def __init__(self, position=(0, 0)):
        super().__init__(position)
        sprite = StaticSprite.from_path("images/pigeon.png")
        sprite.set_colorkey((255, 0, 255))
        self.sprites.append(sprite)

    def add_to_layer(self, layer, x, y):
        super().add_to_layer(layer, x, y)

    def update(self, dt, events):
        super().update(dt, events)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and not self.animating():
                    self.move(y=-1)
                if event.key == pygame.K_s and not self.animating():
                    self.move(y=1)
                if event.key == pygame.K_a and not self.animating():
                    self.move(x=-1)
                if event.key == pygame.K_d and not self.animating():
                    self.move(x=1)

    def draw(self, surface, offset=(0, 0)):
        super().draw(surface, offset=offset)
        hovered = self.layer.map.get_hovered_tile()
        if hovered:
            color = (255, 255, 0)
            if any([item.solid for item in self.layer.map.get_all_at_position(hovered.x, hovered.y)]):
                color = (255, 0, 0)
            off = hovered - self.position_on_grid
            self.draw_highlight(surface, *off.get_position(), color, offset=offset)