import copy
import itertools
import logging

import gym
import numpy as np

import decks
import draws
import players.player

logger = logging.getLogger('sette-mezzo')

TOP = 7.5


class SetteMezzoEnv(gym.Env):

    def __init__(self, depth=4):
        self.game_deck = decks.Deck()
        self.initial_deck = decks.Deck()
        self.player = players.player.Player()
        self.opponent_player = players.player.Player()
        self.initial_player = players.player.Player()
        self.depth = depth
        self.top = 7.5
        self.END_NAME, self.END_VALUE = 'END_NAME', -1
        self.action_space = ['hit', 'stick']
        # self.observation_space = self.generate_state_space()

    def reset(self):
        self.game_deck = decks.Deck()
        self.player = players.player.Player()

    def generate_state_space(self):
        raw_draws = self.generate_draws(self.depth)
        consistent_draws = self.filter_draws_by_consistency(raw_draws, self.game_deck)
        init_draws = self.filter_draws_by_initial_state(consistent_draws, self.player)
        end_draws = self.add_terminal_states(init_draws)
        burst_draws = self.add_burst_states(init_draws, self.game_deck)
        return init_draws + end_draws + burst_draws

    def add_burst_states(self, draw_list, deck):
        burst_draws = []
        for card in decks.CARD_NAMES:
            for draw in draw_list:
                burst_draw = draws.Draw(copy.deepcopy(draw.draw_data) + [(card, decks.DECK_VALUES[card])])
                if burst_draw.sum() > self.top and (burst_draw - self.player.draw).is_consistent(deck):
                    burst_draws.append(burst_draw)
        return burst_draws

    def add_terminal_states(self, draw_list):
        end_draws = []
        for draw in draw_list:
            term = draws.Draw(copy.deepcopy(draw.draw_data) + [(self.END_NAME, self.END_VALUE)])
            end_draws.append(term)
        return end_draws

    def filter_draws_by_consistency(self, draw_list, deck):
        allowed_draws = []
        for draw in draw_list:
            draw_sum = draw.sum()
            if (draw - self.player.draw).is_consistent(deck) and draw_sum <= self.top:
                allowed_draws.append(draw)
        logger.debug('Number of allowed draws by consistency %d', len(allowed_draws))
        return allowed_draws

    def filter_draws_by_initial_state(self, draw_list, player):
        allowed_draws = []
        for draw in draw_list:
            if draw.draw_data[:len(player.draw.draw_data)] == player.draw.draw_data:
                allowed_draws.append(draw)
        logger.debug('Number of allowed draws by initial state %s', len(allowed_draws))
        return allowed_draws

    def filter_draws_by_stick(self, draw_list, deck, player):
        allowed_draws = []
        for draw in draw_list:
            draw_sum = draw.sum()
            # Find combinations where we lose
            if draw.is_consistent(deck) and draw_sum <= self.top:
                # -1 so to properly handle when player_sum = 0
                no_last = draws.Draw(draw.draw_data[:-1])
                draw_sum_nolast = -1 if len(no_last) == 0 else no_last.sum()
                # Assuming we play against the dealer we need >=
                if draw_sum_nolast < player.sum() <= draw_sum:
                    allowed_draws.append(draw)
        logger.debug('Number of allowed draws %d', len(allowed_draws))
        return allowed_draws

    def _get_reward_stick(self, deck, player):
        """
        Compute the probability that the deck beats the
        sum reached by the opponent_player
        """
        if self.opponent_player.sum() >= player.sum():
            return -1
        raw_draws = self.generate_draws(self.depth)
        init_draws = self.filter_draws_by_initial_state(raw_draws, self.opponent_player)
        allowed_draws = self.filter_draws_by_stick(init_draws, deck, player)
        draw_probs = self.get_draw_probs(allowed_draws, deck)
        # In this way I obtain the probability of winning as number in [-1,1]
        return 2 * (1 - sum(draw_probs)) - 1

    def get_draw_probs(self, draw_list, deck):
        draw_probs = []
        for draw in draw_list:
            corrected_draw = draw - self.opponent_player.draw
            help_deck = decks.Deck(copy.deepcopy(deck.deck_data))
            draw_prod = 1
            for card_name, card_value in corrected_draw.draw_data:
                draw_prod *= help_deck.get_prob_of_card(card_name)
                help_deck.update(card_name)
            draw_probs.append(draw_prod)
        return draw_probs

    def generate_draws(self, depth):
        raw_draws = []
        for i in range(1, depth + 1):
            for draw_name in tuple(itertools.product(decks.CARD_NAMES, repeat=i)):
                d = draws.Draw([])
                for card_name in draw_name:
                    d.update_with_name(card_name)
                raw_draws.append(d)
            logger.debug('Number of draws %s', len(raw_draws))
        return raw_draws

    def _get_reward_hit(self, player):
        reward = -1 if player.is_burst() else 0
        return reward

    def player_is_burst(self):
        return self.player.is_burst()

    def _update_player_deck(self, card):
        self.player.update(card)

    def set_current_player(self, player):
        self.player = player

    def set_opponent_player(self, opponent_player):
        self.opponent_player = opponent_player

    def get_card(self, card_name=None):
        self.game_deck.update(card_name)
        self.player.update(card_name)
        return card_name

    def step(self, action):
        if action == 'hit':
            card_name = np.random.choice(decks.CARD_NAMES, p=self.game_deck.get_probs())
            self.game_deck.update(card_name)
            self.player.update(card_name)
            burst = self.player_is_burst()
            reward = self._get_reward_hit(self.player)
            return card_name, reward, burst, None
        elif action == 'stick':
            reward = self._get_reward_stick()
            return self.END_NAME, reward, 1, None
        else:
            raise ValueError('Action not allowed')

    def get_transitions_stick(self, draw):
        prob = 1
        reward = self._get_reward_stick(self.initial_deck, self.initial_player)
        term = draws.Draw(copy.deepcopy(draw.draw_data) + [(self.END_NAME, self.END_VALUE)])
        return [[term, reward, prob]]

    def get_transitions_hit(self, draw):
        probs = self.initial_deck.get_probs()
        rewards = []
        next_draws = []
        # Mimic the draw of the next card
        for card_name in self.initial_deck.get_allowed_cards():
            help_deck = copy.deepcopy(self.initial_deck)
            help_player = copy.deepcopy(self.initial_player)
            help_deck.update(card_name)
            help_player.update(card_name)
            reward = self._get_reward_hit(help_player)
            rewards.append(reward)
            next_draws.append(draws.Draw(copy.deepcopy(draw.draw_data) + [(card_name, decks.DECK_VALUES[card_name])]))
        return list(zip(next_draws, rewards, probs))

    def align_deck(self, draw):
        self.initial_deck = copy.deepcopy(self.game_deck)
        self.initial_player = copy.deepcopy(self.player)
        for card_name, _ in (draw - self.player.draw).draw_data:
            self.initial_deck.update(card_name)
            self.initial_player.update(card_name)

    def get_transitions(self, draw, action):
        if draw.draw_data[-1] == (self.END_NAME, self.END_VALUE):
            return [[draw, 0, 1]]
        elif draw.sum() > self.top:
            return [[draw, 0, 1]]
        if len(draw.draw_data) >= self.depth:
            return [[draw, 0, 1]]
        else:
            self.align_deck(draw)
            if action == 'hit':
                return self.get_transitions_hit(draw)
            elif action == 'stick':
                return self.get_transitions_stick(draw)
            else:
                raise ValueError('Action not allowed')

    def render(self):
        pass
