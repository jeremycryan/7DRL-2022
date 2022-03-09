import pygame

LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "

class SpellHUD:

    def __init__(self, player):
        """
        UI for drawing the player's spells and cooldowns
        :param player: The player
        """
        self.player = player

        self.charging_font = pygame.font.SysFont("monospace", 12, True)
        # TODO use colors from the pallette
        self.charging_letters = {letter: self.charging_font.render(letter, 0, (128, 128, 128)) for letter in LETTERS}
        self.charged_letters = {letter: self.charging_font.render(letter, 0, (128, 180, 255)) for letter in LETTERS}
        self.ready_letters = {letter: self.charging_font.render(letter, 0, (255, 255, 255)) for letter in LETTERS}

    def get_spells(self):
        return self.player.spells

    def get_cooldowns(self):
        return self.player.cooldown

    def draw_spell(self, surface, spell, cooldown, offset=(0, 0)):
        if spell is None or cooldown is None:
            return

        letters = []
        if cooldown == 0:
            letters = [self.ready_letters[letter] for letter in spell.get_name().upper()]
        else:
            charging_letters = [self.charging_letters[letter] for letter in spell.get_name().upper()]
            charged_letters = [self.charged_letters[letter] for letter in spell.get_name().upper()]
            letters = charged_letters[:-cooldown] + charging_letters[-cooldown:]

        x = offset[0]
        x0 = x
        y = offset[1]
        # TODO add wiggle to fully charged spells
        for letter in letters:
            surface.blit(letter, (x, y))
            x += letter.get_width()

        if spell is self.player.get_spell():
            pygame.draw.rect(surface, (255, 255, 255), (x0 - 3, y - 3, x -x0 + 6, letter.get_height() + 4), 1)

    def draw(self, surface, offset=(0, 0)):
        x, y = offset
        for spell, cooldown in zip(self.get_spells(), self.get_cooldowns()):
            self.draw_spell(surface, spell, cooldown, (x, y))
            y += 15