import env, settings
import logging
from players import dp

logger = logging.getLogger('sette-mezzo')

environment = env.SetteMezzoEnv()
logger.info('Deck %s', environment.game_deck.deck)

dp_player = dp.DynamicProgrammer()

for _ in range(40):
    environment.set_current_player(dp_player)
    dp_player.act(environment)
    environment.step('stick')
    logger.info('Deck %s', environment.game_deck)
