import pygame

from lib.Primitives import GameObject
from lib.Settings import Settings


class CalloutManager:
    NEW_LEVEL = 0
    LOST_PAGE = 1

    queue = None
    on_this_message = 0
    MESSAGE_TIME = 4

    header_render = None
    body_render = None

    @classmethod
    def init(cls):
        cls.queue = []
        cls.header_font = pygame.font.Font("fonts/pixantiqua.ttf", 24)
        cls.body_font = pygame.font.Font("fonts/smallest_pixel.ttf", 10)
        cls.rect_surf = pygame.surface.Surface((Settings.Static.GAME_WIDTH, 75))
        cls.lost_page_found = cls.body_font.render("Lost spell found!", 1, (133, 133, 133))

        pass

    @classmethod
    def update(cls, dt, events):
        cls.on_this_message += dt
        if cls.through() > 1:
            cls.next_message()

    @classmethod
    def current_message(cls):
        if not cls.queue:
            return None
        else:
            return cls.queue[0]

    @classmethod
    def next_message(cls):
        cls.queue = cls.queue[1:]
        cls.on_this_message = 0
        if cls.current_message():
            cls.header_render = cls.header_font.render(cls.current_message()[1], 0, (255, 255, 255))
            cls.body_render = cls.body_font.render(cls.current_message()[2], 0, (133, 133, 133))

    @classmethod
    def through(cls):
        return cls.on_this_message/cls.MESSAGE_TIME

    @classmethod
    def draw(cls, surf, offset=(0, 0)):
        if not cls.queue:
            return
        shownness = cls.shown() * 2
        banner_shownness = min(cls.shown() * 2, 1)
        text_shownness = min(max(0, cls.shown() - 0.4) * 2, 1)
        max_height = cls.rect_surf.get_height()
        cls.rect_surf.set_alpha(255)
        surf.blit(cls.rect_surf, (0, -max_height + int(banner_shownness*max_height)))
        surf.blit(cls.rect_surf, (0, Settings.Static.GAME_HEIGHT - int(banner_shownness*max_height)))

        if text_shownness > 0:
            if cls.current_message()[0] == cls.LOST_PAGE:
                surf.blit(cls.lost_page_found, (Settings.Static.GAME_WIDTH//2 - cls.lost_page_found.get_width()//2, 14))
            if cls.header_render:
                surf.blit(cls.header_render, (Settings.Static.GAME_WIDTH//2 - cls.header_render.get_width()//2, 24))
            if cls.body_render:
                surf.blit(cls.body_render, (Settings.Static.GAME_WIDTH//2 - cls.body_render.get_width()//2, 50)) \

        cls.rect_surf.set_alpha((1 - text_shownness) * 255)
        surf.blit(cls.rect_surf, (0, -max_height + int(banner_shownness*max_height)))
        surf.blit(cls.rect_surf, (0, Settings.Static.GAME_HEIGHT - int(banner_shownness*max_height)))

    @classmethod
    def shown(cls):
        thresh = 0.2
        if cls.through() < 0 or cls.through() > 1:
            return 0
        elif cls.through() < thresh:
            return cls.through() / thresh
        elif cls.through() > (1 - thresh):
            return (1 - cls.through()) / thresh
        else:
            return 1

    @classmethod
    def post_message(cls, message_type, message_header, message_body):
        cls.queue.append((message_type, message_header, message_body))
        if len(cls.queue) == 1:
            cls.on_this_message = 0
            if cls.current_message():
                cls.header_render = cls.header_font.render(cls.current_message()[1], 0, (255, 255, 255))
                cls.body_render = cls.body_font.render(cls.current_message()[2], 0, (170, 170, 170))

