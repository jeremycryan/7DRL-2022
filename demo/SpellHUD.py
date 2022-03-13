import pygame

from demo.Button import Button
from demo.Pickup import LetterTile
from lib.ImageHandler import ImageHandler
import math
import time

from lib.Settings import Settings
from lib.Math import lerp, PowerCurve

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz 1234567890"

class SpellHUD:

    def __init__(self, player):
        """
        UI for drawing the player's spells and cooldowns
        :param player: The player
        """
        self.player = player

        self.charging_font = pygame.font.Font("fonts/pixantiqua.ttf", 12)
        # TODO use colors from the pallette
        self.charging_letters = {letter: self.charging_font.render(letter, 0, (191, 111, 74)) for letter in LETTERS}
        self.charged_letters = {letter: self.charging_font.render(letter, 0, (48, 3, 217)) for letter in LETTERS}
        self.ready_letters = {letter: self.charging_font.render(letter, 0, (0, 0, 0)) for letter in LETTERS}
        self.index_letters = {letter: self.charging_font.render(letter, 0, (255, 255, 255)) for letter in LETTERS}

        button_surf = ImageHandler.load("images/ui/UI_Btn_Uncraft_Up.png")
        button_hover = ImageHandler.load("images/ui/UI_Btn_Uncraft_Hover.png")
        button_clicked = ImageHandler.load("images/ui/UI_Btn_Uncraft_Pressed.png")
        button_hover.set_colorkey((255, 0, 255))
        button_surf.set_colorkey((255, 0, 255))
        button_clicked.set_colorkey((255, 0, 255))
        self.uncraft_buttons = [
            Button(button_surf.copy(), (0, 0), on_click=self.uncraft, hover_surf=button_hover.copy(), click_surf=button_clicked.copy()) for _ in range(10)
        ]

        self.scroll = ImageHandler.load("images/ui/scroll.png")
        self.scroll.set_colorkey((255, 0, 255))
        self.glow = ImageHandler.load("images/ui/scroll_glow.png")

    def update(self, dt, events):
        for button in self.uncraft_buttons:
            button.update(dt, events)

    def uncraft(self):
        for i, button in enumerate(self.uncraft_buttons):
            if button.is_hovered():
                self.uncraft_spell(i)
                break

    def uncraft_spell(self, idx):
        spell = self.player.spells[idx]
        self.player.letter_tiles += [LetterTile(letter.upper()) for letter in spell.get_name()]
        self.player.spells[idx] = None
        self.player.cooldown[idx] = None

    def get_spells(self):
        return self.player.spells

    def get_cooldowns(self):
        return self.player.cooldown

    def draw_spell(self, surface, spell, cooldown, offset=(0, 0)):
        if spell is None or cooldown is None:
            return

        index = self.get_spells().index(spell)
        index_letters = [self.index_letters[letter] for letter in str(index)]

        if cooldown == 0:
            letters = [self.ready_letters[letter] for letter in spell.get_name().capitalize()]
        else:
            charging_letters = [self.charging_letters[letter] for letter in spell.get_name().capitalize()]
            charged_letters = [self.charged_letters[letter] for letter in spell.get_name().capitalize()]
            letters = charged_letters[:-cooldown] + charging_letters[-cooldown:]

        shown = lerp(0, 1, Settings.Dynamic.MENU_SHOWN, PowerCurve(0.5, 0.5, 2))

        x = offset[0] + 12 + 36 * shown
        x0 = x
        y = offset[1]
        # TODO add wiggle to fully charged spells

        button = self.uncraft_buttons[index]
        if shown > 0:
            button.x = x - 40
            button.y = y + 8
            button.draw(surface)


        if spell is self.player.get_spell():
            surface.blit(self.glow, (x - 32 - self.glow.get_width()//2 + self.scroll.get_width()//2, y - 10 - self.glow.get_height()//2 + self.scroll.get_height()//2), special_flags=pygame.BLEND_ADD)
        surface.blit(self.scroll, (x - 32, y - 10))

        index_width = sum([letter.get_width() for letter in index_letters])
        xi, yi = x - index_width//2 - 7, y
        for letter in index_letters:
            surface.blit(letter, (xi, yi))
            xi += letter.get_width()

        word_width = sum([letter.get_width() for letter in letters])
        offset = 35 - word_width//2
        x += offset


        for letter in letters:
            surface.blit(letter, (x, y + 2 + (cooldown == 0) * math.sin(time.time() * 10 - x) * 1))
            x += letter.get_width()

        if spell is self.player.get_spell():
            pygame.draw.rect(surface, (255, 255, 255), (x0 - 3, y - 3, x -x0 + 6, letter.get_height() + 4), 1)

    def draw(self, surface, offset=(0, 0)):
        x, y = offset[0], offset[1] - 12
        for spell, cooldown in zip(self.get_spells(), self.get_cooldowns()):
            self.draw_spell(surface, spell, cooldown, (x, y))
            y += 35