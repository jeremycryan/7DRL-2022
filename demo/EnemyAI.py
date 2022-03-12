import random

from lib import Math
from lib.GridEntity import GridEntity
from lib.Primitives import Pose


def wander(self):
    """ Move in a random direction """
    directions = [(1, 0), (0, 1), (0, -1), (-1, 0)]
    random.shuffle(directions)
    for direction in directions:
        if self.can_move(*direction):
            self.move(*direction)
            self.align_sprites()
            break


def find(self, radius=1, factions=None, visible=True, squares=None):
    """ Return nearest entity from given faction (or any hostile faction by default), or None if none in range """
    if not squares:
        squares = Math.get_squares_in_range(radius)
    if not factions:
        factions = [GridEntity.FACTION_ALLY, GridEntity.FACTION_HOSTILE]
        factions.remove(self.faction)
    square, entity = self.layer.map.get_entity(squares, origin=self.position_on_grid, factions=factions)
    if visible and square:
        squares = self.layer.map.filter_line_of_sight([square], self.position_on_grid)
        print("A")
        if not squares:
            return None, None
    return square, entity


def hunt(self, target, squares=None):
    """ Move in direction of target, or return False if unable to move closer """
    if not squares:
        squares = Math.get_squares_in_range(1.5, no_origin=True)
    squares = filter_moveable(self, squares)
    if not len(squares):
        return False
    squares.sort(key=lambda s: (s-target).magnitude())
    return squares[0]


def attack(self, target, spell):
    """ Cast spell at the target, or return False if out of range"""
    return None


def filter_moveable(self, squares):
    new_squares = []
    for square in squares:
        if self.can_move(*square.get_position()):
            new_squares.append(square)
    return new_squares
