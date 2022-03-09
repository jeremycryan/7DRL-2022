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
        WINDOW_WIDTH = 1280
        WINDOW_HEIGHT = 720
        GAME_WIDTH = 640
        GAME_HEIGHT = 360

    class Dynamic:
        """
        Settings that can change during runtime
        """
        SHOW_FPS_COUNTER = True
