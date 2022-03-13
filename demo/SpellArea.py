from lib import Math
from lib.Primitives import Pose
from lib.Math import get_line


class SpellArea:
    def __init__(self, origin=Pose((0, 0)), squares=None):
        if squares is None:
            squares = []
        self.origin = origin
        self.squares = squares


class Point(SpellArea):
    def __init__(self, origin=Pose((0, 0))):
        """
        Single target
        :param origin: target square
        """
        super().__init__(origin, [origin])


class Line(SpellArea):
    def __init__(self, origin=Pose((0, 0)), endpoint=Pose((0, 0)), offset=True, line_of_sight=False):
        """
        Target all squares in a line
        :param origin: source square
        :param endpoint: final square in line
        :param offset: start at second square (e.g. to avoid caster)
        :param line_of_sight: if true, only squares with line of sight to origin are affected
        """
        super().__init__(origin)
        self.endpoint = endpoint
        self.line_of_sight = line_of_sight
        self.squares = get_line(origin, endpoint, offset=offset)  # TODO (low priority): check line of sight


class Cross(SpellArea):
    def __init__(self, origin=Pose((0, 0)), radius=1, no_origin=False):
        """
        Target all squares in a line
        :param origin: source square
        :param radius: size of cross
        :param no_origin: true if origin is not included
        """
        super().__init__(origin)
        self.squares = Math.get_squares(diagonal=radius, origin=origin)
        if not no_origin:
            self.squares.append(origin)


class Circle(SpellArea):
    def __init__(self, origin=Pose((0, 0)), radius=1, include_origin=True, line_of_sight=False):
        """
        Target all squares in a line
        :param origin: center of circle
        :param radius: radius of circle
        :param line_of_sight: if true, only squares with line of sight to origin are affected
        """
        super().__init__(origin)
        self.radius = radius
        self.line_of_sight = line_of_sight
        for dx in range(-int(radius), int(radius) + 1):
            for dy in range(-int(radius), int(radius) + 1):
                p = Pose((dx, dy))
                if p.magnitude() <= radius and (include_origin or p.magnitude() > 0):
                    self.squares.append(p + origin)  # TODO (low priority): check line of sight


class Cone(SpellArea):
    def __init__(self, origin=Pose((0, 0)), endpoint=Pose((0, 0)), line_of_sight=False):
        """
        Target all squares in a triangular cone
        :param origin: source square
        :param endpoint: final square in axis of cone
        :param line_of_sight: if true, only squares with line of sight to origin are affected
        """
        super().__init__(origin)
        self.endpoint = endpoint
        self.line_of_sight = line_of_sight
        self.squares = []  # TODO: implement cone
