import time

from pygame.pixelarray import PixelArray

from demo.Button import Button
from demo.EnemyDropHandler import EnemyDropHandler
from demo.Pickup import LetterTile
from lib.ImageHandler import ImageHandler
from lib.Primitives import GameObject
from lib.Settings import Settings
from lib.Sprite import StaticSprite
from lib.Primitives import Pose
import pygame
from lib.Math import lerp, PowerCurve
import math

from demo.Spell import list_spells, get_spell, list_known_spells


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

    LETTER_POSITIONS_ADJUSTED = False

    LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    LETTER_POSITIONS_DICT = None

    def __init__(self, player):
        super().__init__()
        if not CraftingMenu.LETTER_POSITIONS_ADJUSTED:
            CraftingMenu.LETTER_POSITIONS_ADJUSTED = True
            CraftingMenu.LETTER_POSITIONS = [(i[0] + 8, i[1]) for i in CraftingMenu.LETTER_POSITIONS]
            CraftingMenu.LETTER_POSITIONS_DICT = {self.LETTERS[i]: self.LETTER_POSITIONS[i] for i in range(len(self.LETTERS))}
        self.picked_up_tiles = []
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
        self.menu_bar = ImageHandler.load("images/ui/spell_menu_bar.png")
        self.menu_bar.set_colorkey((255, 0, 255))
        craft_button_surf = ImageHandler.load("images/craft_button.png")
        craft_button_surf.set_colorkey((255, 0, 255))
        craft_button_hover = ImageHandler.load("images/craft_button_hover.png")
        craft_button_hover.set_colorkey((255, 0, 255))
        craft_button_disabled = ImageHandler.load("images/craft_button_disabled.png")
        craft_button_disabled.set_colorkey((255, 0, 255))
        craft_button_clicked = ImageHandler.load("images/craft_button_clicked.png")
        craft_button_clicked.set_colorkey((255, 0, 255))

        self.craft_button = Button(craft_button_surf, (0, 0), hover_surf=craft_button_hover, disabled_surf=craft_button_disabled,click_surf=craft_button_clicked, enabled=False, on_click=self.craft)
        self.banner = Banner(self)
        self.info_book = InfoBook(self)


    def show(self):
        self.recalculate_tiles()
        self.hidden = False
        self.player.lock()
        if self.shown <= 0:
            self.info_book.select_spell_tab()

    def pick_up(self, tile):
        if self.picked_up_tiles:
            return
        self.picked_up_tiles.append(tile)
        if self.banner.hovered():
            if tile in self.banner.tiles[:]:
                self.banner.tiles.remove(tile)
        else:
            for player_tile in self.player.letter_tiles[:]:
                if tile.letter == player_tile.letter:
                    self.player.letter_tiles.remove(player_tile)
                    self.recalculate_tiles()
                    break

    def drop_all(self):
        if self.picked_up_tiles:
            if self.banner.hovered() and len(self.banner.tiles) < 9:
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

        surf.blit(self.menu_bar, (Settings.Static.GAME_WIDTH//2 - self.menu_bar.get_width()//2, 0 - int(self.shown * 20)))
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
        self.info_book.draw(surf, offset=offset)
        for tile in self.picked_up_tiles:
            tile.go_to_mouse()
            tile.draw(surf, offset=offset)

    def toggle_hidden(self):
        if self.hidden and self.player.can_make_turn_movement():
            self.show()
        else:
            self.hide()

    def update(self, dt, events):
        speed = 5
        Settings.Dynamic.MENU_SHOWN = self.shown
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

        if self.shown > 0:
            self.recalculate_tiles()
            self.info_book.refresh()

        for tile in self.tiles + self.picked_up_tiles:
            tile.update(dt, events)

        self.craft_button.update(dt, events)
        self.banner.update(dt, events)
        self.info_book.update(dt, events)

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

        if not self.banner.can_craft():
            self.craft_button.disable()
        else:
            self.craft_button.enable()

    def craft(self):
        if not self.banner.can_craft():
            return False

        idx = 0
        for item in self.player.spells:
            if item or not idx:
                idx += 1
            else:
                break
        if idx >= len(self.player.spells):
            return False

        spell_name = self.banner.get_word()
        self.player.spells[idx] = get_spell(self.player, spell_name)
        self.player.cooldown[idx] = len(spell_name)
        self.banner.tiles = []
        self.info_book.refresh()


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
        arr.replace((93, 44, 40), (28, 18, 28))
        arr.replace((138, 72, 54), (57, 31, 33))
        arr.replace((191, 111, 74), (93, 44, 40))
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
    def __init__(self, menu):
        super().__init__()
        self.menu = menu
        self.sprite = StaticSprite(ImageHandler.load("images/craft_banner.png"), colorkey=(255, 0, 255))
        self.sprite.position = Pose((Settings.Static.GAME_WIDTH//2, Settings.Static.GAME_HEIGHT - 40), 0)
        self.info = ImageHandler.load("images/ui/craft_help.png")
        self.position = self.sprite.position.copy()
        self.tiles = []
        self.tile_spacing = 32

    def draw(self, surf, offset=(0, 0)):
        self.sprite.draw(surf, offset=offset)
        for tile in self.tiles:
            tile.draw(surf, offset=offset)
        if not self.tiles:
            surf.blit(self.info, (self.sprite.position.x - self.info.get_width()//2 + offset[0], self.sprite.position.y - self.info.get_height()//2 + offset[1]))

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
        return self.get_word() in list_known_spells() and not self.get_word().lower() in [spell.__class__.__name__.lower() for spell in self.menu.player.spells]


class InfoBook(GameObject):

    SPELL_MODE = 0
    ENEMY_MODE = 1

    def __init__(self, menu):
        super().__init__()
        self.menu = menu
        self.surf = ImageHandler.load("images/ui/UI_Spellcraft_Info_Background.png")
        self.surf.set_colorkey((0, 0, 0))
        self.position = Pose((Settings.Static.GAME_WIDTH - 74, Settings.Static.GAME_HEIGHT//2))

        spell_button_surf = ImageHandler.load("images/ui/UI_Spellcraft_Info_SpellsTab_Active.png")
        spell_button_surf_selected = ImageHandler.load("images/ui/UI_Spellcraft_Info_SpellsTab_Deactive.png")
        spell_button_surf.set_colorkey((0, 0, 0))
        spell_button_surf_selected.set_colorkey((0, 0, 0))
        self.spell_button = Button(spell_button_surf_selected,
                                   (self.position - Pose((31, 120))).get_position(),
                                   disabled_surf=spell_button_surf,
                                   on_click=self.select_spell_tab,
                                   grow_percent=0,
                                   pulse = False)

        enemy_button_surf = ImageHandler.load("images/ui/UI_Spellcraft_Info_EnemiesTab_Active.png")
        enemy_button_surf_selected = ImageHandler.load("images/ui/UI_Spellcraft_Info_EnemiesTab_Deactive.png")
        enemy_button_surf.set_colorkey((0, 0, 0))
        enemy_button_surf.set_colorkey((0, 0, 0))
        self.enemy_button = Button(enemy_button_surf_selected,
                                   (self.position - Pose((-21, 120))).get_position(),
                                   disabled_surf=enemy_button_surf,
                                   on_click=self.select_enemy_tab,
                                   grow_percent=0,
                                   pulse = False)

        self.spell_list_font = pygame.font.Font("fonts/pixantiqua.ttf", 12)

        self.spell_help = ImageHandler.load("images/ui/spell_help.png")
        self.enemy_help = ImageHandler.load("images/ui/enemy_help.png")

        self.select_spell_tab()
        self.mode = self.SPELL_MODE

    def select_spell_tab(self):
        self.spell_button.disable()
        self.enemy_button.enable()
        self.refresh()
        self.mode = self.SPELL_MODE

    def compile_spell_list(self):
        self.spell_list = list_known_spells()
        available_spell_letters = [tile.letter for tile in self.menu.player.letter_tiles] \
                                  + [tile.letter for tile in self.menu.picked_up_tiles] \
                                  + [tile.letter for tile in self.menu.banner.tiles]
        self.spell_list_surfs = []
        for spell in self.spell_list:

            spell = spell.capitalize()
            letters = []
            if spell in [spell.__class__.__name__ for spell in self.menu.player.spells if spell]:
                color = (48, 3, 217)
                spell = "* " + spell.capitalize() + " *"
                for letter in spell:
                    letters.append(self.spell_list_font.render(letter, 0, (color)))
            else:
                available = available_spell_letters.copy()
                for letter in spell:
                    color = 87, 28, 39
                    if letter.upper() not in available:
                        color = (191, 111, 74)
                    else:
                        available.remove(letter.upper())
                    letters.append(self.spell_list_font.render(letter, 0, (color)))
            self.spell_list_surfs.append(letters)

    def compile_enemy_names(self):
        self.enemy_list = Settings.Dynamic.KNOWN_ENEMIES.copy()
        self.enemy_list_surfs = []
        for enemy in self.enemy_list:
            letters = []
            for i, letter in enumerate(enemy.capitalize()):
                color = (191, 111, 74)
                if i >= len(EnemyDropHandler.get_drops_so_far(enemy.upper())):
                    color = 87, 28, 39
                letters.append(self.spell_list_font.render(letter, 1, color))
            self.enemy_list_surfs.append(letters)

    def draw_spell_names(self, surf, offset=(0, 0)):
        x = offset[0] + self.position.x
        y = offset[1] + self.position.y - 95

        surf.blit(self.spell_help, (x + 1 - self.spell_help.get_width()//2, y - 5))
        y += self.spell_help.get_height() + 5

        for letter_list in self.spell_list_surfs:
            x = offset[0] + self.position.x
            width = sum([item.get_width() for item in letter_list])
            x -= width//2
            for letter in letter_list:
                surf.blit(letter, (x, y - letter.get_height()//2))
                x += letter.get_width()
            y += 12

    def draw_enemy_names(self, surf, offset=(0, 0)):
        x = offset[0] + self.position.x
        y = offset[1] + self.position.y - 95

        surf.blit(self.enemy_help, (x + 1 - self.enemy_help.get_width()//2, y - 5))
        y += self.enemy_help.get_height() + 5
        for letter_list in self.enemy_list_surfs:
            x = offset[0] + self.position.x
            width = sum([item.get_width() for item in letter_list])
            x -= width//2
            for letter in letter_list:
                surf.blit(letter, (x, y - letter.get_height() // 2))
                x += letter.get_width()
            y += 12

    def select_enemy_tab(self):
        self.spell_button.enable()
        self.enemy_button.disable()
        self.mode = self.ENEMY_MODE

    def draw(self, surf, offset=(0, 0)):
        offset = int(offset[1] * 0.5), offset[0]
        x, y = (self.position + Pose(offset) - Pose(self.surf.get_size())*0.5).get_position()
        surf.blit(self.surf, (int(x), int(y)))
        self.spell_button.draw(surf, *offset)
        self.enemy_button.draw(surf, *offset)
        if self.mode == self.SPELL_MODE:
            self.draw_spell_names(surf, offset=offset)
        else:
            self.draw_enemy_names(surf, offset=offset)

    def refresh(self):
        self.compile_spell_list()
        self.compile_enemy_names()

    def update(self, dt, events):
        self.spell_button.update(dt, events)
        self.enemy_button.update(dt, events)
