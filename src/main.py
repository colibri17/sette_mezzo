import logging
import settings
import env
from players import dp, greedy

logger = logging.getLogger('sette-mezzo')

environment = env.SetteMezzoEnv(4)
logger.info('Deck %s', environment.game_deck.deck_data)

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
logger.info('Player draw_list %s, action %s', dp_player.draw_collection.draw_data, action)

i = 2
playing = action == 'hit'
while playing:
    player_card = input('Player card number %d: ' % i)
    environment.get_card_and_update(player_card)
    action = dp_player.act()
    logger.info('Player draw_list %s, action %s', dp_player.draw_collection.draw_data, action)
    if action == 'stick' or dp_player.is_busted():
        playing = False

# for _ in range(40):
#     card = environment.get_card('3')
#     dp_player.act(card)
#     environment.step('stick')
#     logger.info('Deck %s', environment.game_deck)
