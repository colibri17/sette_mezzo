import logging

from agents import dp, greedy
from decks.deck_factory import Deck
from env import SetteMezzoEnv, Player

logger = logging.getLogger('sette-mezzo')

depth = 4
limit = 4

deck = Deck()
logger.info('Deck %s', deck)
players = {Player(0): dp.DpAgent(),
           Player(1, limit=limit): greedy.BookmakerAgent(limit=limit)}
agents = list(players.values())

state = SetteMezzoEnv(list(players.keys()), deck, depth)

# Draw initial player cards
state.apply_action(None)
state.apply_action(None)

# Playing the game
while not state.is_terminal():
    agent = agents[state.current_player.id]
    action = agent.step(state)
    logger.info('Player %s action %s', state.current_player.id, action)
    state.apply_action(action)

returns = state.returns()
end = 'winned' if returns[0] > returns[1] else 'tied' if returns[0] == returns[1] else 'lost'
logger.info(f"Returns: {returns}, you {end}")
