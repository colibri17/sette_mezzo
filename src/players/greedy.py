import logging

from players.player import Player

logger = logging.getLogger('sette-mezzo')


class GreedyProgrammer(Player):

    def __init__(self, draw_collection=None, policy=None, limit=None):
        super().__init__(draw_collection=draw_collection,
                         policy=policy, limit=limit)

    def _act_bookmaker_strategy(self, opponent_player):
        if self.draw_collection.sum() >= self.limit:
            return 'stick'
        else:
            return 'hit'

    def act_mixed_strategy(self, opponent_player):
        if self.draw_collection.sum() >= self.limit:
            return 'stick'
        else:
            if self.draw_collection.sum() <= opponent_player.draw_collection.sum():
                return 'hit'
            else:
                return 'stick'

    def act(self, opponent_player):
        return self._act_bookmaker_strategy(opponent_player)

    def copy(self):
        pass
