import logging

logger = logging.getLogger('sette-mezzo')


class BookmakerAgent:

    def __init__(self, limit=None):
        self.limit = limit

    def step(self, state):
        """
        Given a game state, the agent plays according to
        the greedy strategy: if the player sum is greater
        or equal than the limit it sticks, otherwise it
        hits
        :param state: game state
        :return: action to be played
        """
        current_player = state.current_player
        if current_player.draws.sum() >= self.limit:
            return 'stick'
        else:
            return 'hit'
