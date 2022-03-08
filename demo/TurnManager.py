class TurnManager:

    entities = None
    next_entity_turn = 0

    @classmethod
    def init(cls, initial_entities=None):
        cls.entities = initial_entities if initial_entities else []
        cls.next_entity_turn = 0

    @classmethod
    def take_next_turn(cls):
        if not any([entity.taking_turn for entity in cls.entities]):
            cls.entities[cls.next_entity_turn].take_turn()
            cls.next_entity_turn += 1
            if cls.next_entity_turn >= len(cls.entities):
                cls.next_entity_turn = 0

    @classmethod
    def add_entities(cls, *args):
        cls.entities += args

    @classmethod
    def remove_entities(cls, *args):
        for entity in args:
            if not entity in cls.entities:
                continue
            index = cls.entities.index(entity)
            if index < cls.next_entity_turn:
                cls.next_entity_turn -= 1
            cls.entities.pop(index)
