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
        which can be drawn including the initial card already
        drawn by the player. Namely. excluding the initial card
        drawn by the opponent the allowed draws are generated. These
        will be the states of the game.
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
        self.draw_manager.freeze()
        return self.draw_manager.draw_ensemble

    def _get_reward_stick(self, input_deck, input_player, opponent_player):
        """
        Compute the probability that the input_deck beats the
        sum reached by the opponent_player
        """
        # This is the case where the opponent
        # card is higher than input_player initial card
        input_player_sum = input_player.sum()
        if self.opponent_player.sum() > input_player_sum:
            return -1
        # TODO: why don't we use the self.whole_state_space which
        # TODO: should be already be defined at the very beginning?
        if not self.whole_state_space:
            self.whole_state_space = self.draw_manager.generate(self.depth).draw_ensemble
        self.draw_manager = draws.draw_manager.DrawManager(self.whole_state_space)
        # TODO: why do we use the game deck?
        # TODO: basically we generate the state space here.
        # TODO: Why do not use the same we already computed?
        # Should not we use the input deck?
        # filter_by_deck: Get all the card combinations the opponent can obtain
        (self.draw_manager
         .filter_by_deck(self.game_deck, opponent_player)
         .filter_by_initial_state(opponent_player)
         .filter_by_stick(input_player_sum, opponent_player)
         .get_prob_sum_complete(input_deck, opponent_player))
        # In this way I obtain the probability of winning as a number in [-1,1]
        # TODO: rescale so that the sum of the 3 probs is 1
        return 2 * (sum(self.draw_manager.prob_win) + sum(self.draw_manager.prob_tie)) - 1

    def _get_reward_hit(self, player):
        # TODO: let this method be called by get_transitions_hit
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
        """
        Returns the terminal state,
        the corresponding reward and
        the probability to reach it
        :param draw:
        :return:
        """
        prob = 1
        reward = self._get_reward_stick(self.initial_deck, self.initial_player, self.opponent_player)
        return [(terminal.freeze(), reward, prob)]

    def get_transitions_hit(self, draw):
        """
        Compute the next possible states, rewards
        and probabilities starting from
        the current draw.
        :param draw: card collection representing current state
        :return: list of all possible next states and corresponding rewards and probs
        """
        transitions = []
        cards_probs = self.initial_deck.get_cards_and_probs()
        # Mimic the draw for the next card
        for card, prob in cards_probs:
            # TODO: Instead of checking prob > 0 should
            # TODO: we check on the whole state space?
            if prob > 0:
                help_deck = self.initial_deck.copy()
                help_player = self.initial_player.copy()
                help_deck.update(card)
                help_player.update(card)
                if help_player.is_busted():
                    # If player is busted reward is negative
                    transitions.append((terminal.freeze(), -1, prob))
                else:
                    transitions.append((draw.copy().update(card).freeze(), 0, prob))
        return transitions

    def align_decks(self, draw_list):
        """
        Copy the current deck and then update it with the
        next cards the player will draw.
        :param draw_list:
        :return:
        """
        #TODO: moving in deck and player
        self.initial_deck = self.game_deck.copy()
        self.initial_player = self.player.copy()
        # Threse is a difference because we
        # create the deck having init opponent card
        # + init player card (already in self.game_deck)
        # + next player card (which have to be added)
        for card in (draw_list - self.player.draw_collection).data:
            self.initial_deck.update(card)
            self.initial_player.update(card)

    def get_transitions(self, draw_list, action):
        """
        Generates all the possible next states which
        can be reached from the provided card sequence
        combination, together with corresponding rewards
        and reaching probabilities
        :param draw_list: Card sequence
        :param action: action to take
        :return: None
        """
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
