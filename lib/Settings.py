class Settings:
    """
    Static class for storing settings for the game.
    """

    def load(self):
        # TODO load these and arbitrary others from YAML
        pass

    class Static:
        """
        Settings that should be loaded once as the application starts, then remain constant at runtime
        """
        TILE_SIZE = 32
        ROOM_WIDTH = 15
        ROOM_HEIGHT = 15
        MAP_WIDTH = 2
        MAP_HEIGHT = 2
        WINDOW_WIDTH = 1280
        WINDOW_HEIGHT = 720
        GAME_WIDTH = 640
        GAME_HEIGHT = 360

        PICKUP_LAYER = 0.8
        DECORATOR_LAYER = 0.9

        STARTING_LETTERS = ["Z", "A", "P"]

    class Dynamic:
        """
        Settings that can change during runtime
        """
        SHOW_FPS_COUNTER = True
