from demo.Pickup import LetterTile, HealthPickupSmall
import random

class EnemyDropHandler:

    enemy_drops_so_far = None

    @classmethod
    def init(cls):
        cls.enemy_drops_so_far = {}

    @classmethod
    def get_drop(cls, enemy):
        key = enemy.name
        if not key in cls.enemy_drops_so_far:
            new_tile = LetterTile(key[0])
            cls.enemy_drops_so_far[key] = [new_tile]
            return new_tile
        if len(cls.enemy_drops_so_far[key]) < len(key):
            new_tile = LetterTile(key[len(cls.enemy_drops_so_far[key])])
            cls.enemy_drops_so_far[key].append(new_tile)
            return new_tile
        else:
            if random.random() < 0.05:
                pip = HealthPickupSmall()
                return pip
            if random.random() < 0.1:
                new_tile = LetterTile(random.choice(enemy.name))
                return new_tile

    @classmethod
    def get_drops_so_far(cls, key):
        if key in cls.enemy_drops_so_far:
            return cls.enemy_drops_so_far[key].copy()
        else:
            return []