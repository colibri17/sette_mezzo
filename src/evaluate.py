import itertools
import logging

import pandas as pd

from decks import deck_factory
import env
import settings
from players import dp, greedy

logger = logging.getLogger('sette-mezzo')

match_summary = []
player_policies = {}
n = 100000
depth = 5
limit = 5

# Learn starting from an initial configuration
logger.info('Learning..')
for ind, (player_card, opponent_card) in enumerate(itertools.product(deck_factory.CARD_NAMES, repeat=2)):
    logger.info('Training number %d', ind + 1)
    # Reset the game
    environment = env.SetteMezzoEnv(depth)
    dp_player = dp.DynamicProgrammer()
    greedy_player = greedy.GreedyProgrammer(limit=limit)
    # Set initial state
    logger.info('Initial card for input_player %s, initial card for opposite input_player %s', player_card, opponent_card)
    environment.set_current_players(greedy_player, dp_player)
    environment.get_card_and_update(opponent_card)
    environment.set_current_players(dp_player, greedy_player)
    environment.get_card_and_update(player_card)

    if environment.game_deck.is_feasible():
        # Player 1 playing
        environment.set_current_players(dp_player, greedy_player)
        dp_player.learn(environment)
        player_policies[(player_card, opponent_card)] = dp_player

# Play
logger.info('Starting to play')
for n_game in range(n):
    if (n_game + 1) % 1000 == 0:
        logger.info('Playing match number %d', n_game + 1)
    # Reset the game
    environment = env.SetteMezzoEnv(depth)
    player_card, opponent_card = environment.get_card_and_update(), environment.get_card_and_update()
    logger.debug('Deck %s', environment.game_deck.deck_data)
    dp_player = player_policies[(player_card, opponent_card)].copy()
    greedy_player = greedy.GreedyProgrammer(limit=limit)
    dp_player.reset_status()
    greedy_player.reset_status()
    environment.reset()

    # Set initial state
    logger.debug('Initial card for input_player %s, initial card for opposite input_player %s', player_card, opponent_card)
    environment.set_current_players(greedy_player, dp_player)
    environment.get_card_and_update(opponent_card)
    environment.set_current_players(dp_player, greedy_player)
    environment.get_card_and_update(player_card)

    action = dp_player.act()
    logger.debug('Player draw_list %s, action %s', dp_player.draw_collection.data, action)
    playing = action == 'hit'
    over_depth = False
    need_to_play = True
    while playing:
        player_card = environment.get_card_and_update(None)
        if dp_player.is_busted():
            playing = False
            need_to_play = False
            logger.debug('Player busted, %s', dp_player.draw_collection.data)
        elif len(dp_player.draw_collection.data) > depth - 1:
            playing = False
            over_depth = True
            need_to_play = False
            logger.debug('Stop evaluating input_player moves, %s', dp_player.draw_collection.data)
        else:
            action = dp_player.act()
            if action == 'stick':
                playing = False
            logger.debug('Player draw_list %s, action %s', dp_player.draw_collection.data, action)

    # Opponent input_player
    if need_to_play:
        environment.set_current_players(greedy_player, dp_player)
        action = greedy_player.act(dp_player)
        logger.debug('Opponent input_player draw_list %s, action %s', greedy_player.draw_collection.data, action)
        playing = action == 'hit'
        while playing:
            opponent_card = environment.get_card_and_update(None)
            if greedy_player.is_busted():
                playing = False
                logger.debug('Opponent input_player busted, %s', greedy_player.draw_collection.data)
            else:
                action = greedy_player.act(dp_player)
                if action == 'stick':
                    playing = False
                logger.debug('Opponent input_player draw_list %s, action %s', greedy_player.draw_collection.data, action)

    # Collect results
    if not over_depth:
        if dp_player.is_busted():
            match_result = -1
            logger.debug('Player busted')
        elif greedy_player.is_busted():
            match_result = 1
            logger.debug('Opponent input_player busted')
        else:
            if dp_player.sum() > greedy_player.sum():
                match_result = 1
                logger.debug('Player won')
            elif dp_player.sum() < greedy_player.sum():
                match_result = -1
                logger.debug('Player lost')
            else:
                match_result = 0
                logger.debug('Player draw_list')
    else:
        match_result = -2

    match_summary.append([n_game, dp_player.draw_collection.data,
                          greedy_player.draw_collection.data,
                          match_result])
    logger.debug('\n' * 2)

    # Analysis
    if (n_game + 1) % 1000 == 0:
        df = pd.DataFrame(match_summary, columns=['game_number', 'player_draw', 'opponent_draw', 'result'])
        df.to_pickle('%s/stats.pkl' % settings.SELECTED_RUNS_DIR)
