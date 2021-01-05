import logging
import settings
from agents import dp, greedy
from decks.deck_factory import Deck
from env import SetteMezzoEnv, Player

logger = logging.getLogger('sette-mezzo')

depth = 4

deck = Deck()
logger.info('Deck %s', deck)
players = {Player(0): dp.DpAgent(),
           Player(1, limit=5): greedy.BookmakerAgent(limit=5)}
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
logger.info(f"Returns: {returns}")
