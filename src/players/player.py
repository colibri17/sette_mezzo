import draws.draw_factory
import draws.draw_manager
import env


class Player:

    def __init__(self, draw_collection=None, policy=None, limit=None):
        self.draw_collection = draws.draw_factory.DrawCollection([]) if draw_collection is None else draw_collection
        self.policy = None if policy is None else policy
        self.busted = self.is_busted()
        self.limit = limit

    def update(self, card_name):
        self.draw_collection.update(card_name)

    def reset_status(self):
        self.draw_collection = draws.draw_factory.DrawCollection([])
        self.busted = False

    def sum(self):
        return self.draw_collection.sum()

    def is_busted(self):
        return self.draw_collection.sum() > env.TOP

    def set_bust(self, burst):
        self.busted = burst

    def copy(self):
        raise NotImplementedError
