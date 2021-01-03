import logging
import settings
import env
from players import dp, greedy

logger = logging.getLogger('sette-mezzo')

depth = 4

environment = env.SetteMezzoEnv(depth)
logger.info('Deck %s', environment.game_deck.data)

dp_player = dp.DynamicProgrammer()
greedy_player = greedy.GreedyProgrammer(limit=5)

# Set initial state
environment.set_current_players(greedy_player, dp_player)
opponent_card = input('Opponent initial card: ')
environment.get_card_and_update(opponent_card)
environment.set_current_players(dp_player, greedy_player)
player_card = input('Player initial card: ')
environment.get_card_and_update(player_card)

# Learn
environment.set_current_players(dp_player, greedy_player)
dp_player.learn(environment)
action = dp_player.act()
logger.info('Player draw_list %s, action %s', dp_player.draw_collection.data, action)

i = 2
playing = action == 'hit'
while playing:
    player_card = input('Player card number %d: ' % i)
    environment.get_card_and_update(player_card)
    if len(dp_player.draw_collection.data) > depth:
        logger.info('More than allowed depth. Increase the variable depth')
        playing = False
        break
    if not dp_player.is_busted():
        action = dp_player.act()
        logger.info('Player draw_list %s, action %s', dp_player.draw_collection.data, action)
    else:
        logger.info('Player is busted!')
        playing = False
    if action == 'stick':
        playing = False
