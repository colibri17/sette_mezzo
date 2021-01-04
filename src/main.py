import logging
import settings
from env import SetteMezzoEnv, Player
from decks.deck_factory import Deck
from agents import dp, greedy

logger = logging.getLogger('sette-mezzo')

depth = 4

deck = Deck()
logger.info('Deck %s', deck)
players = [Player(i) for i in range(2)]
state = SetteMezzoEnv(players, deck, depth)


dp_agent = dp.DpAgent()
greedy_agent = greedy.BookmakerAgent(limit=5)
agents = [dp_agent, greedy_agent]


# Draw initial player cards
state.apply_action(None)
state.apply_action(None)

while not state.is_terminal():
    agent = agents[state.current_player.id]
    action = agent.step(state)
    state.apply_action(action)

# Learn
dp_agent.learn()
action = dp_agent.act()
logger.info('Player draw_list %s, action %s', dp_agent.draw_collection.data, action)

i = 2
playing = action == 'hit'
while playing:
    player_card = input('Player card number %d: ' % i)
    state.get_card_and_update(player_card)
    if len(dp_agent.draw_collection.data) > depth:
        logger.info('More than allowed depth. Increase the variable depth')
        playing = False
        break
    if not dp_agent.is_busted():
        action = dp_agent.act()
        logger.info('Player draw_list %s, action %s', dp_agent.draw_collection.data, action)
    else:
        logger.info('Player is busted!')
        playing = False
    if action == 'stick':
        playing = False
