import pygame


class ImageHandler:
    """
    Static class to handle loading of pygame surfaces to improve performance
    """

    initialized = False
    surfaces = None

    class NotInitializedException(Exception):
        pass

    @staticmethod
    def init():
        ImageHandler.initialized = True
        ImageHandler.surfaces = {}

    @staticmethod
    def check_initialized():
        if not ImageHandler.initialized:
            raise ImageHandler.NotInitializedException("Must call ImageHandler.init() before any other methods.")

    @staticmethod
    def clear(path):
        """
        Forgets one thing.
        :param path: The path of the file to remove from memory
        :return:
        """
        ImageHandler.check_initialized()
        if path in ImageHandler.surfaces:
            del ImageHandler.surfaces[path]

    @staticmethod
    def clear_all():
        """
        Forgets everything
        """
        ImageHandler.check_initialized()
        ImageHandler.surfaces = {}

    @staticmethod
    def load(path):
        """
        Loads a surface from file or from cache
        :param path: The path of the image
        :return: The surface. This is likely the same reference others are using, so don't be destructive.
        """
        ImageHandler.check_initialized()
        if path in ImageHandler.surfaces:
            return ImageHandler.surfaces[path]
        surface = pygame.image.load(path).convert()
        ImageHandler.surfaces[path] = surface
        return surface

    @staticmethod
    def load_copy(path):
        """
        Loads a surface, then copies it
        :param path: The path of the image
        :return: The surface
        """
        ImageHandler.check_initialized()
        return ImageHandler.load(path).copy()

    @staticmethod
    def reload(path):
        """
        If for some reason we think the file has changed
        :param path: The path of the image
        :return: The surface freshly loaded from disk
        """
        ImageHandler.check_initialized()
        ImageHandler.clear(path)
        return ImageHandler.load(path)
