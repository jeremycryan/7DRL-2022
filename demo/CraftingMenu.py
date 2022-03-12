import time

from pygame.pixelarray import PixelArray

from demo.Button import Button
from demo.Pickup import LetterTile
from lib.ImageHandler import ImageHandler
from lib.Primitives import GameObject
from lib.Settings import Settings
from lib.Sprite import StaticSprite
from lib.Primitives import Pose
import pygame
from lib.Math import lerp, PowerCurve
import math


class CraftingMenu(GameObject):

    LETTER_POSITIONS = (
        (155, 94),
        (188, 78),
        (221, 70),
        (254, 66),
        (287, 64),
        (321, 64),
        (354, 66),
        (387, 70),
        (420, 78),
        (453, 94),
        (155, 158),
        (188, 142),
        (221, 134),
        (254, 130),
        (287, 128),
        (321, 128),
        (354, 130),
        (387, 134),
        (420, 142),
        (453, 158),
        (221, 198),
        (254, 194),
        (287, 192),
        (321, 192),
        (354, 194),
        (387, 198),
    )

    LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    LETTER_POSITIONS_DICT = None

    def __init__(self, player):
        super().__init__()
        CraftingMenu.LETTER_POSITIONS_DICT = {self.LETTERS[i]: self.LETTER_POSITIONS[i] for i in range(len(self.LETTERS))}
        self.count_font = pygame.font.Font("fonts/alagard.ttf", 16)
        self.player = player
        self.tiles = []
        self.hidden = True
        self.black = pygame.Surface((Settings.Static.GAME_WIDTH, Settings.Static.GAME_HEIGHT))
        self.black.fill((0, 0, 0))
        self.black.set_alpha(150)
        self.gray_letters = [GrayUITile(letter) for letter in self.LETTERS]
        self.counts = []
        self.position = Pose((0, Settings.Static.GAME_HEIGHT), 0)
        self.curve = PowerCurve(0, 0.8, 1.5)
        self.shown = 0
        craft_button_surf = ImageHandler.load("images/craft_button.png")
        craft_button_surf.set_colorkey((255, 0, 255))
        self.craft_button = Button(craft_button_surf, (0, 0), hover_surf=craft_button_surf, enabled=False)
        self.banner = Banner()

        self.picked_up_tiles = []

    def show(self):
        self.recalculate_tiles()
        self.hidden = False
        self.player.lock()

    def pick_up(self, tile):
        if self.picked_up_tiles:
            return
        self.picked_up_tiles.append(tile)
        if self.banner.hovered():
            for banner_tile in self.banner.tiles[:]:
                if tile.letter == banner_tile.letter:
                    self.banner.tiles.remove(banner_tile)
        for player_tile in self.player.letter_tiles[:]:
            if tile.letter == player_tile.letter:
                self.player.letter_tiles.remove(player_tile)
                self.recalculate_tiles()
                break

    def drop_all(self):
        if self.picked_up_tiles:
            if self.banner.hovered():
                new_tiles = self.picked_up_tiles
                for tile in new_tiles:
                    tile.position = self.picked_up_tiles[0].position.copy()
                    self.banner.add_tile(tile)
            else:
                self.player.letter_tiles += [LetterTile(tile.letter) for tile in self.picked_up_tiles]
            self.picked_up_tiles = []
            self.recalculate_tiles()

    def recalculate_tiles(self):
        self.tiles = [UITile(letter, self) for letter in self.player.letter_tiles]
        counts = []
        for letter in self.LETTERS:
            count = sum([tile.letter == letter for tile in self.tiles])
            counts.append(count)
        self.counts = [self.count_font.render(f"{count}", False, self.count_color(count)) for count in counts]

    @staticmethod
    def count_color(count):
        if count > 0:
            return 255, 255, 255
        else:
            return 101, 115, 146

    def hide(self):
        self.hidden = True
        self.player.unlock()

    def draw_grays(self, surf, offset=(0, 0)):
        for letter in self.gray_letters:
            if letter.letter not in [tile.letter for tile in self.tiles]:
                letter.draw(surf, offset=offset)

    def draw(self, surf, offset=(0, 0)):
        offset = Pose(offset, 0)
        offset += self.position
        offset = offset.get_position()
        if self.shown == 0:
            return
        surf.blit(self.black, (0, 0))
        self.draw_grays(surf, offset)
        for tile in self.tiles:
            tile.draw(surf, offset=offset)
        for letter in self.LETTERS:
            x, y = self.LETTER_POSITIONS_DICT[letter]
            count_surf = self.counts[self.LETTERS.index(letter)]
            x += -count_surf.get_width()//2 + 16 + self.position.x
            y += -count_surf.get_height()//2 + 40 + self.position.y
            surf.blit(count_surf, (x, y))
        self.craft_button.x = Settings.Static.GAME_WIDTH//2 + offset[0]
        self.craft_button.y = Settings.Static.GAME_HEIGHT - 94 + offset[1]
        self.craft_button.draw(surf, *offset)
        self.banner.draw(surf, offset=offset)
        for tile in self.picked_up_tiles:
            tile.go_to_mouse()
            tile.draw(surf, offset=offset)

    def toggle_hidden(self):
        if self.hidden:
            self.show()
        else:
            self.hide()

    def update(self, dt, events):
        speed = 5
        if self.hidden:
            self.shown = max(0, self.shown - speed * dt)
        else:
            self.shown = min(1, self.shown + speed * dt)
        self.position = Pose((0, lerp(Settings.Static.GAME_HEIGHT, 0, self.shown, self.curve)), 0)
        self.black.set_alpha(self.shown * 180)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.toggle_hidden()

        for tile in self.tiles + self.picked_up_tiles:
            tile.update(dt, events)

        self.craft_button.update(dt, events)
        self.banner.update(dt, events)

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.drop_all()

        if self.shown == 0 and self.banner.tiles:
            self.player.letter_tiles += [LetterTile(tile.letter) for tile in self.banner.tiles]
            self.banner.tiles = []
        if self.shown == 0 and self.picked_up_tiles:
            self.player.letter_tiles += [LetterTile(tile.letter) for tile in self.picked_up_tiles]
            self.picked_up_tiles = []

    def craft(self):
        pass

class UITile(GameObject):
    def __init__(self, letter, menu):
        super().__init__()
        self.menu = menu
        self.letter = letter.letter
        self.sprite = StaticSprite(ImageHandler.load(f"images/letters/UI_Letter_{letter.letter}.png"), colorkey=(255, 0, 255))
        self.home_position = Pose(CraftingMenu.LETTER_POSITIONS_DICT[letter.letter], 0)
        self.position = self.home_position.copy()

    def draw(self, surf, offset=(0, 0)):
        offset = Pose(offset, 0)
        xoff = 16 + 1 * math.sin(time.time() * 6 + CraftingMenu.LETTERS.index(self.letter)/3)
        yoff = 16 + 2 * -math.cos(time.time() * 6 + CraftingMenu.LETTERS.index(self.letter)/3)
        offset += self.position + Pose((xoff, yoff), 0)
        self.sprite.draw(surf, offset=offset.get_position())

    def update(self, dt, events):
        self.sprite.update(dt, events)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.hovered():
                    self.menu.pick_up(self)

    def go_to_mouse(self):
        mpos = Pose(pygame.mouse.get_pos(), 0)
        mpos.x *= Settings.Static.GAME_WIDTH/Settings.Static.WINDOW_WIDTH
        mpos.y *= Settings.Static.GAME_HEIGHT/Settings.Static.WINDOW_HEIGHT
        self.position = mpos - Pose((16, 16), 0)

    def hovered(self):
        mpos = Pose(pygame.mouse.get_pos(), 0)
        mpos.x *= Settings.Static.GAME_WIDTH/Settings.Static.WINDOW_WIDTH
        mpos.y *= Settings.Static.GAME_HEIGHT/Settings.Static.WINDOW_HEIGHT
        diff = mpos - self.position
        if abs(diff.x - 16) < 16 and abs(diff.y - 16) < 16:
            return True
        return False


class GrayUITile(GameObject):
    def __init__(self, letter):
        super().__init__()
        self.letter = letter
        surface = ImageHandler.load_copy(f"images/letters/UI_Letter_{letter}.png")
        arr = PixelArray(surface)
        arr.replace((93, 44, 40), (20, 20, 20))
        arr.replace((138, 72, 54), (50, 50, 50))
        arr.replace((191, 111, 74), (70, 70, 70))
        del arr

        self.sprite = StaticSprite(surface, colorkey=(255, 0, 255))
        self.home_position = Pose(CraftingMenu.LETTER_POSITIONS_DICT[letter], 0)
        self.position = self.home_position.copy()

    def draw(self, surf, offset=(0, 0)):
        offset = Pose(offset, 0)
        offset += self.position + Pose((16, 16), 0)
        self.sprite.draw(surf, offset=offset.get_position())

    def update(self, dt, events):
        self.sprite.update(dt, events)


class Banner(GameObject):
    def __init__(self):
        super().__init__()
        self.sprite = StaticSprite(ImageHandler.load("images/craft_banner.png"), colorkey=(255, 0, 255))
        self.sprite.position = Pose((Settings.Static.GAME_WIDTH//2, Settings.Static.GAME_HEIGHT - 40), 0)
        self.position = self.sprite.position.copy()
        self.tiles = []
        self.tile_spacing = 32

    def draw(self, surf, offset=(0, 0)):
        self.sprite.draw(surf, offset=offset)
        for tile in self.tiles:
            tile.draw(surf, offset=offset)

    def update(self, dt, events):
        target_y = self.position.y
        target_xs = self.get_target_x_positions()
        for i, tile in enumerate(self.tiles):
            target_x = target_xs[i]
            diff = Pose((target_x, target_y), 0) - tile.position - Pose((16, 16), 0)
            if diff.magnitude() < 2:
                tile.position += diff
            else:
                tile.position += diff * dt * 10
            tile.update(dt, events)

    def get_target_x_positions(self):
        number = len(self.tiles)
        positions = []
        start = self.position.x - self.tile_spacing * (number - 1)/2
        for _ in self.tiles:
            positions.append(start)
            start += self.tile_spacing
        return positions

    def add_tile(self, tile):
        x_positions = self.get_target_x_positions()
        index = 0
        for x_position in x_positions:
            if tile.position.x > x_position - 16:
                index += 1
        self.tiles = self.tiles[:index] + [tile] + self.tiles[index:]

    def hovered(self):
        mpos = Pose(pygame.mouse.get_pos(), 0)
        mpos.x *= Settings.Static.GAME_WIDTH/Settings.Static.WINDOW_WIDTH
        mpos.y *= Settings.Static.GAME_HEIGHT/Settings.Static.WINDOW_HEIGHT
        diff = mpos - self.sprite.position
        if abs(diff.x) < 160 and abs(diff.y) < 40:
            return True
        return False

    def get_word(self):
        return "".join([tile.letter for tile in self.tiles])

    def can_craft(self):
        # TODO determine if current spelling is valid word
        return False