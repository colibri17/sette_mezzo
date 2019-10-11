import logging

from players.player import Player

logger = logging.getLogger('sette-mezzo')


class GreedyProgrammer(Player):

    def __init__(self, limit=None):
        super().__init__(limit)

    def greedy_policy(self, state):
        return {"hit": .50, "stick": .50}

    def act(self, environment):
        pass
