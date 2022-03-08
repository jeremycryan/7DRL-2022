from lib.Primitives import Pose
from lib.Settings import Settings
import pygame


class Camera:

    initialized = False
    center_objects = None
    mouse_weight = 0
    weights = None
    speed = None
    position = None

    @classmethod
    def init(cls, objects=None, weights=None, mouse_weight=0, initial_position=(0, 0), speed=4):
        """
        Initializes the camera

        :param initial_position: The camera's initial position as a Pose or (x, y) tuple
        :param speed: The speed the camera will track the objects (the "P" value in PID)
        :param objects: A list of objects the camera will try to center on
        :param weights: An optional list of weights that correspond to the objects. Higher weight means the camera
            will try to track it more.
        :param mouse_weight: An optional weight for the cursor. Defaults to zero.
        :return:
        """
        cls.center_objects = objects if objects is not None else []
        cls.weights = weights if weights else [1 for _ in cls.center_objects]
        cls.mouse_weight = mouse_weight
        cls.initialized = True
        cls.position = initial_position
        cls.speed = speed
        if type(cls.position) is tuple:
            cls.position = Pose(cls.position, 0)

    @classmethod
    def require_initialized(cls):
        if not cls.initialized:
            raise ValueError("Camera must be initialized to call this method.")

    @classmethod
    def get_target_position(cls):
        cls.require_initialized()
        total_weight = sum(cls.weights) + cls.mouse_weight
        average = Pose((0, 0), 0)
        for item, weight in zip(cls.center_objects, cls.weights):
            average += (item.position * weight)*(1/total_weight)
        mouse_game_pos = Pose(pygame.mouse.get_pos(), 0)
        mouse_game_pos.x *= Settings.Static.GAME_WIDTH/Settings.Static.WINDOW_WIDTH
        mouse_game_pos.y *= Settings.Static.GAME_HEIGHT/Settings.Static.WINDOW_HEIGHT
        average += mouse_game_pos * cls.mouse_weight * (1/total_weight)
        return average

    @classmethod
    def update(cls, dt, events):
        cls.require_initialized()
        diff = cls.get_target_position() - cls.position
        cls.position += diff * dt * cls.speed

    @classmethod
    def change_objects(cls, objects, weights, mouse_weight=None, jump_now=False):
        """
        Updates the objects for the camera to track
        :param objects: List of objects
        :param weights: List of weights
        :param mouse_weight: Weight of mouse pointer
        :param jump_now: If true, camera will immediately jump to the new target point rather than pan from its
            previous position
        """
        cls.require_initialized()
        cls.center_objects = objects
        cls.weights = weights
        cls.mouse_weight = mouse_weight if mouse_weight is not None else cls.mouse_weight
        if jump_now:
            cls.position = cls.get_target_position()

    @classmethod
    def get_game_position(cls):
        cls.require_initialized()
        return cls.position.copy() * -1

    @classmethod
    def get_game_offset(cls):
        game_position = cls.get_game_position().copy()
        game_position.x = int(game_position.x)
        game_position.y = int(game_position.y)
        return game_position + Pose((Settings.Static.GAME_WIDTH//2, Settings.Static.GAME_HEIGHT//2), 0)