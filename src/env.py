import logging
import gym
import numpy as np
import draws.draw_manager
import draws.draw_factory
import players.player
from decks import deck_factory

logger = logging.getLogger('sette-mezzo')

TOP = 7.5
END_NAME = 'END'
terminal = draws.draw_factory.DrawCollection([END_NAME])


class SetteMezzoEnv(gym.Env):

    def __init__(self, depth=4):
        self.game_deck = deck_factory.Deck()
        self.initial_deck = deck_factory.Deck()
        self.player = players.player.Player()
        self.opponent_player = players.player.Player()
        self.initial_player = players.player.Player()
        self.draw_manager = draws.draw_manager.DrawManager([])
        self.depth = depth
        self.action_space = ['hit', 'stick']
        self.whole_state_space = []

    def reset(self):
        self.game_deck = deck_factory.Deck()
        self.player = players.player.Player()

    def generate_state_space(self, input_player):
        """
        Generate the combinations of all the allowed card sequences
        which can be drawn from here on.
        The maximum card sequence lenght is specified by self.depth
        :param input_player: the player for which the state space is generated
        :return: the set of all possible allowed combinations
        """
        if not self.whole_state_space:
            self.whole_state_space = self.draw_manager.generate(self.depth).draw_ensemble
        self.draw_manager = draws.draw_manager.DrawManager(self.whole_state_space)
        self.draw_manager.filtered_draws = list((self.draw_manager
                                                 .filter_by_deck(self.game_deck, input_player)
                                                 .filter_by_sum()
                                                 .filter_by_initial_state(input_player)).draw_ensemble)
        self.draw_manager.add_terminal_state()
        return self.draw_manager.draw_ensemble

    def _get_reward_stick(self, input_deck, input_player, opponent_player):
        """
        Compute the probability that the input_deck beats the
        sum reached by the opponent_player
        """
        # This is the case where the opponent
        # card is higher than input_player initial card
        input_player_sum = input_player.sum()
        if self.opponent_player.sum() >= input_player_sum:
            return -1
        if not self.whole_state_space:
            self.whole_state_space = self.draw_manager.generate(self.depth).draw_ensemble
        self.draw_manager = draws.draw_manager.DrawManager(self.whole_state_space)
        (self.draw_manager
         .filter_by_deck(self.game_deck, opponent_player)
         .filter_by_initial_state(opponent_player)
         .filter_by_stick_complete_bookmaker_strategy(input_player_sum, opponent_player)
         .get_prob_sum_complete(input_deck, opponent_player))
        # In this way I obtain the probability of winning as number in [-1,1]
        return 2 * (sum(self.draw_manager.prob_win) + sum(self.draw_manager.prob_tie)) - 1

    def _get_reward_hit(self, player):
        return -1 if player.is_busted() else 0

    def set_current_players(self, player, opponent_player):
        self.player = player
        self.opponent_player = opponent_player

    def get_card_and_update(self, card_name=None):
        card_name = self.get_card(card_name)
        self.game_deck.update(card_name)
        self.player.update(card_name)
        return card_name

    def get_card(self, card_name=None):
        if card_name is None:
            card_name = np.random.choice(deck_factory.CARD_NAMES, p=list(self.game_deck.get_probs()))
        return card_name

    def get_transitions_stick(self, draw):
        prob = 1
        reward = self._get_reward_stick(self.initial_deck, self.initial_player, self.opponent_player)
        return [[terminal, reward, prob]]

    def get_transitions_hit(self, draw):
        probs = self.initial_deck.get_probs()
        rewards = []
        next_draw_collection = []
        # Mimic the draw for the next card
        for card in self.initial_deck.get_allowed_cards():
            help_deck = self.initial_deck.copy()
            help_player = self.initial_player.copy()
            help_deck.update(card)
            help_player.update(card)
            if help_player.is_busted():
                rewards.append(-1)
                next_draw_collection.append(terminal)
            else:
                rewards.append(0)
                next_draw_collection.append(draw.copy().update(card))
        return list(zip(next_draw_collection, rewards, probs))

    def align_decks(self, draw_list):
        self.initial_deck = self.game_deck.copy()
        self.initial_player = self.player.copy()
        for card in (draw_list - self.player.draw_collection).data:
            self.initial_deck.update(card)
            self.initial_player.update(card)

    def get_transitions(self, draw_list, action):
        if draw_list.data[0] == END_NAME:
            return [[draw_list, 0, 1]]
        if len(draw_list.data) >= self.depth:
            return [[draw_list, 0, 1]]
        else:
            self.align_decks(draw_list)
            if action == 'hit':
                return self.get_transitions_hit(draw_list)
            elif action == 'stick':
                return self.get_transitions_stick(draw_list)
            else:
                raise ValueError('Action not allowed')
