import random

from lib import Math
from lib.GridEntity import GridEntity
from lib.Primitives import Pose


def wander(self, squares):
    """ Move in a random direction """
    random.shuffle(squares)
    for square in squares:
        if self.can_move(*square.get_position()):
            return square
    return None


def select_target(self, targets, squares=None, radius=None, visible=False):
    """ Return nearest square in targets, within radius, and in the given set of squares """
    targets.sort(key=lambda s: s.magnitude())
    for target in targets:
        if radius and target.magnitude() > radius:
            break
        if (not squares) or any([(target - square).magnitude() == 0 for square in squares]):
            if not visible or self.layer.map.check_line_of_sight(target, self.position_on_grid):
                return target
    return None


def find(self, radius=1, factions=None, visible=True, squares=None):
    """ Return nearest entity from given faction (or any hostile faction by default), or None if none in range """
    if not squares:
        squares = Math.get_squares_in_range(radius)
    else:
        squares = filter_radius(self, squares, radius=radius)
    if visible:
        squares = self.layer.map.filter_line_of_sight(squares, self.position_on_grid)
    if not factions:
        factions = [GridEntity.FACTION_ALLY, GridEntity.FACTION_HOSTILE]
        factions.remove(self.faction)
    if not len(squares):
        return None, None
    square, entity = self.layer.map.get_entity(squares, origin=self.position_on_grid, factions=factions)
    return square, entity


def hunt(self, target, squares=None):
    """ Move in direction of target, or return False if unable to move closer """
    if not squares:
        squares = Math.get_squares_in_range(1, no_origin=True)
    squares = filter_moveable(self, squares)
    if not len(squares):
        return False
    squares.sort(key=lambda s: (s-target).magnitude())
    return squares[0]


def filter_moveable(self, squares):
    new_squares = []
    for square in squares:
        if self.can_move(*square.get_position()):
            new_squares.append(square)
    return new_squares


def filter_radius(self, squares, radius):
    new_squares = []
    for square in squares:
        if square.magnitude() <= radius:
            new_squares.append(square)
    return new_squares


def get_squares(self, linear=0, diagonal=0, radius=0, custom=0):
    squares = []
    if not hasattr(linear, "__iter__"):
        linear = (linear,)
    if not hasattr(diagonal, "__iter__"):
        diagonal = (diagonal,)
    if linear:  # Cardinal movement
        for i in linear:
            squares.append(Pose((i, 0)))
    if diagonal:  # Diagonal movement
        for i in diagonal:
            squares.append(Pose((i, i)))
    if radius:  # Arbitrary movement
        squares += Math.get_squares_in_range(radius, no_origin=True)
    if custom == 1:  # Knight's move away
        squares.append(Pose((1, 2)))
        squares.append(Pose((2, 1)))

    rotations = [((0, 1), (-1, 0)), ((-1, 0), (0, -1)), ((0, -1), (1, 0))]
    for r in rotations: # 4-way symmetry
        for square in squares[:]:
            x = square.x*r[0][0] + square.y*r[0][1]
            y = square.x*r[1][0] + square.y*r[1][1]
            squares.append(Pose((x, y)))
    return squares

