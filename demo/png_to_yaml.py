import pygame
import yaml
from lib.Settings import Settings
import os

PATHS = os.listdir("room_pngs/small_rooms")

OUTPUT_PATH_REL = "rooms/small_rooms"

COLORS_TO_CHARACTER = {
    (0, 0, 0): "X",
    (255, 255, 255): ".",
    (255, 0, 0): "L",
    (0, 255, 0): "R",
    (0, 0, 255): "D",
    (255, 0, 255): "U",
}

if __name__=="__main__":
    for path in PATHS:
        surf = pygame.image.load("room_pngs/small_rooms/" + path)

        yaml_contents = {
            "tiles": [],
        }
        for y in range(surf.get_height()):
            row = ""
            for x in range(surf.get_width()):
                pixel_value = surf.get_at((x, y))
                r, g, b = pixel_value.r, pixel_value.g, pixel_value.b
                if (r, g, b) in COLORS_TO_CHARACTER:
                    row += COLORS_TO_CHARACTER[(r, g, b)]
                else:
                    row += "X"
            yaml_contents["tiles"].append(row)

        yaml_contents["width"] = surf.get_width()//Settings.Static.ROOM_WIDTH
        yaml_contents["height"] = surf.get_height()//Settings.Static.ROOM_HEIGHT

        file_name = path.split("/")[-1][:-4]

        with open(OUTPUT_PATH_REL + file_name + ".yaml", "w") as f:
            yaml.safe_dump(yaml_contents, f)

        print(f"Your file has been generated at {OUTPUT_PATH_REL}.")
    print("Thanks for choosing JarmWare (tm) for your PyGame needs!")
