import env, settings
import logging
from players import dp, greedy

logger = logging.getLogger('sette-mezzo')

environment = env.SetteMezzoEnv(4)
logger.info('Deck %s', environment.game_deck.deck_data)

dp_player = dp.DynamicProgrammer()
greedy_player = greedy.GreedyProgrammer()

# Set initial state
environment.set_current_player(greedy_player)
opponent_card = input('Opponent initial card: ')
environment.get_card(opponent_card)
environment.set_current_player(dp_player)
player_card = input('Player initial card: ')
environment.get_card(player_card)

# Learn
environment.set_current_player(dp_player)
environment.set_opponent_player(greedy_player)
dp_player.learn(environment)
action = dp_player.act()
logger.info('Player draw %s, action %s', dp_player.draw.draw_data, action)

i = 2
playing = action == 'hit'
while playing:
    player_card = input('Player card number %d: ' % i)
    environment.get_card(player_card)
    action = dp_player.act()
    logger.info('Player draw %s, action %s', dp_player.draw.draw_data, action)
    if action == 'stick' or dp_player.is_burst():
        playing = False

# for _ in range(40):
#     card = environment.get_card('3')
#     dp_player.act(card)
#     environment.step('stick')
#     logger.info('Deck %s', environment.game_deck)
