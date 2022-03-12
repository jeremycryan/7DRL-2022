import pygame
import yaml

PATH = "room_to_convert.png"
OUTPUT_PATH = "rooms/new_room.yaml"

COLORS_TO_CHARACTER = {
    (0, 0, 0): "X",
    (255, 255, 255): ".",
    (255, 0, 0): "L",
    (0, 255, 0): "R",
    (0, 0, 255): "D",
    (255, 0, 255): "U",
}

if __name__=="__main__":
    surf = pygame.image.load(PATH)

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

    yaml_contents["width"] = surf.get_width()
    yaml_contents["height"] = surf.get_height()

    with open(OUTPUT_PATH, "w") as f:
        yaml.safe_dump(yaml_contents, f)

    print(f"Your file has been generated at {OUTPUT_PATH}.")
    print("Thanks for choosing JarmWare (tm) for your PyGame needs!")
