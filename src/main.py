import logging

from agents import dp, greedy
from decks.deck_factory import Deck
from env import SetteMezzoEnv, Player

logger = logging.getLogger('sette-mezzo')

depth = 3

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
    state.apply_action(action)

returns = state.returns()
#
# # Learn
# dp_agent.learn()
# action = dp_agent.act()
# logger.info('Player draw_list %s, action %s', dp_agent.draw_collection.data, action)
#
# i = 2
# playing = action == 'hit'
# while playing:
#     player_card = input('Player card number %d: ' % i)
#     if len(dp_agent.draw_collection.data) > depth:
#         logger.info('More than allowed depth. Increase the variable depth')
#         playing = False
#         break
#     if not dp_agent.is_busted():
#         action = dp_agent.act()
#         logger.info('Player draw_list %s, action %s', dp_agent.draw_collection.data, action)
#     else:
#         logger.info('Player is busted!')
#         playing = False
#     if action == 'stick':
#         playing = False
