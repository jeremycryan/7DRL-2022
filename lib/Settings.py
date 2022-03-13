class Settings:
    """
    Static class for storing settings for the game.
    """

    def load(self):
        # TODO load these and arbitrary others from YAML
        pass

    def save(self):
        # TODO save these to YAML
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

        PLAYER_STARTING_HIT_POINTS = 9
        WINDOW_CAPTION = "Spellcraft"

        PICKUP_LAYER = 0.8
        DECORATOR_LAYER = 0.9
        STARTING_LETTERS = [letter for letter in "ABCDEFGHIJLKMNOPQRSTUVWXYZ"] * 3

    class Dynamic:
        """
        Settings that can change during runtime
        """
        SHOW_FPS_COUNTER = True
        KNOWN_SPELLS = ["ZAP", "FLARE", "BOLT", "STAB", "GOLEM"]
        KNOWN_ENEMIES = []
        MENU_SHOWN = 0  # Amount of shown between 0 and 1