import logging
import pickle

import numpy as np
import pandas as pd

import settings
from agents import greedy
from decks import deck_factory
from env import SetteMezzoEnv, Player

logger = logging.getLogger('sette-mezzo')

match_summary = []
n = 100000

# Use the same limit you set on train.py
limit = 4
# Use the same depth you set on train.py
depth = 4

# Retrieve the dynamic players I saved in
# train.py.
with open('%s/dp_agents.pkl' % settings.DATA_DIR, 'rb') as handle:
    player_policies = pickle.load(handle)

# Play
logger.info('Starting to play')
for n_game in range(n):

    deck = deck_factory.Deck()
    # logger.info('Deck %s', deck)

    # Randomly draw two random cards
    player_card = np.random.choice(deck_factory.CARD_NAMES, p=list(deck.get_probs()))
    opponent_card = np.random.choice(deck_factory.CARD_NAMES, p=list(deck.get_probs()))

    players = {Player(0): player_policies[(player_card, opponent_card)],
               Player(1, limit=limit): greedy.BookmakerAgent(limit=limit)}
    player_names = list(players.keys())
    agents = list(players.values())

    # Draw initial player cards
    state = SetteMezzoEnv(player_names, deck, depth)
    state.apply_action(None, player_card)
    state.apply_action(None, opponent_card)

    # Play the game
    while not state.is_terminal():
        player_id = state.current_player.id
        agent = agents[player_id]
        action = agent.step(state)
        # logger.info('Player %s action %s', state.current_player.id, action)
        state.apply_action(action)

    returns = state.returns()
    # Do not count matches which did not reach the end
    # Note that we include also matches where the opponent
    # did not played beyond the depth. That's because we do
    # not want th opponent have any advantage when we make
    # the player compete.
    if returns[0] is not None and returns[1] is not None:
        end = 'winned' if returns[0] > returns[1] else 'tied' if returns[0] == returns[1] else 'lost'
        match_summary.append([n_game, player_names[0].draws, player_names[1].draws, end])
        logger.info(f"Returns: {returns}, you {end}")

    # Analysis
    if (n_game + 1) % 1000 == 0:
        logger.warning('Played match number %d', n_game + 1)
        df = pd.DataFrame(match_summary, columns=['game_number', 'player_draw', 'opponent_draw', 'result'])
        df.to_pickle('%s/results.pkl' % settings.DATA_DIR)
