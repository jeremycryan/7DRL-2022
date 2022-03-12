import random


def wander(self):
    """ Move in a random direction """
    directions = [(1, 0), (0, 1), (0, -1), (-1, 0)]
    random.shuffle(directions)
    for direction in directions:
        if self.can_move(*direction):
            self.move(*direction)
            self.align_sprites()
            break

def find(self, range=1, factions=None, visible=False, squares=None):
    """ Return nearest entity from given faction (or any hostile faction by default), or None if none in range """
    return None

def hunt(self, target, range=0, squares=None):
    """ Move in direction of target, or return False if unable to move closer """
    return None

def attack(self, target, spell):
    """ Cast spell at the target, or return False if out of range"""
    return None