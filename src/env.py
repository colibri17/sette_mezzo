import logging

import numpy as np

import players.player
from decks import deck_factory
from draws.draws_factory import Draws
from draws.draws_manager import DrawManager

logger = logging.getLogger('sette-mezzo')

TOP = 7.5
END_NAME = 'END'
terminal = Draws([END_NAME])


class Player:

    def __init__(self, id, draws=None, limit=None, busted=False):
        self.id = id
        self.draws = Draws([]) if draws is None else draws
        self.busted = busted
        self.limit = limit

    def update(self, card):
        self.draws.update(card)

    def reset_status(self):
        self.draws = Draws([])
        self.busted = False

    def sum(self):
        return self.draws.sum()

    def is_busted(self):
        return self.draws.sum() > TOP

    def set_bust(self, busted):
        self.busted = busted

    def copy(self):
        return Player(id=self.id,
                      draws=self.draws.copy(),
                      limit=self.limit,
                      busted=self.busted)

    def copy_move_ahead(self, cards):
        forward_player = self.copy()
        for card in cards:
            forward_player.update(card)
        return forward_player


class SetteMezzoEnv:

    def __init__(self, players, deck, depth=4):
        self.num_actions = 0
        self.num_played = 0
        self.players = players
        self.current_player = self.players[0]
        self.game_deck = deck

        # Initial deck and initial player will help during
        # computations
        self.forward_deck = deck_factory.Deck()
        self.forward_player = None
        self.depth = depth

        # Note that the action space is unique across the players
        # the state_space instead changes from player to player
        self.action_space = ['hit', 'stick']
        self.whole_state_space = []

        self.draw_manager = DrawManager([])

    def reset(self):
        self.game_deck = deck_factory.Deck()
        self.player = players.player.Player()

    def apply_action(self, action):
        """
        Apply the provided action to the
        current game state
        :param action: action to be applied
        :return: None
        """
        # Draw initial cards for both the players
        if self.num_actions < 2:
            card = input(f'Initial card player{self.current_player.id}: ')
            self.get_card(card)
            self.updates(card)
            self.current_player = self.players[1 - self.current_player.id]
            self.num_actions += 1
        else:
            if action == 'hit':
                card = self.get_card()
                self.updates(card)
            else:
                self.current_player = self.players[1 - self.current_player.id]
                self.num_played += 1

    def generate_state_space(self, player):
        """
        Generate the combinations of all the allowed card sequences
        which can be drawn including the initial card already
        drawn by the player. Namely. excluding the initial card
        drawn by the opponent the allowed draws are generated. These
        will be the states of the game.
        The maximum card sequence lenght is specified by self.depth
        :param player: the player for which the state space is generated
        :return: the set of all possible allowed combinations
        """
        self.whole_state_space = self.draw_manager.generate(self.depth).draws_ensemble
        self.draw_manager = DrawManager(self.whole_state_space)
        self.draw_manager.filtered_draws = list((self.draw_manager
                                                 .filter_by_deck(self.game_deck, player)
                                                 .filter_by_sum()
                                                 .filter_by_initial_state(player)).draws_ensemble)
        self.draw_manager.add_terminal_state()
        self.draw_manager.freeze()
        return self.draw_manager.draws_ensemble

    def get_card(self, card_name=None):
        """
        Draw the provided card if given. Else
        randomly draw a card from the deck
        :param card_name: name of the card to be drawn if any
        :return: name of the card drawn
        """
        if card_name is None:
            card_name = np.random.choice(deck_factory.CARD_NAMES, p=list(self.game_deck.get_probs()))
        return card_name

    def updates(self, card):
        self.game_deck.update(card)
        self.current_player.update(card)

    def _get_reward_stick(self, forward_deck, player, opponent_player):
        """
        Compute the probability that the player beats the
        the opponent_player according
        to all the future evolutions which can be drawn starting
        from the state the player currently is in
        :param forward_deck: current deck
        :param player: current player
        :param opponent_player: opponent player
        :return: probbility of winning
        """
        player_sum = player.sum()
        # This is the case where the opponent
        # card is higher than player initial card: we lose!
        if opponent_player.sum() > player_sum:
            return -1
        self.draw_manager = DrawManager(self.whole_state_space)
        # We generate all the combinations of cards the opponent
        # can reach accordingly to the drawn cards
        # TODO: check again: we would like to take
        # TODO: all the draws which can be generated by the opponent
        # TODO: considering the cards he already has.
        (self.draw_manager
         .filter_by_deck(self.game_deck, opponent_player)
         .filter_by_initial_state(opponent_player)
         .filter_by_stick(player_sum, opponent_player)
         .sum_probs(forward_deck, opponent_player))
        # In this way I obtain the probability of winning as a number in [-1,1]
        # TODO: rescale so that the sum of the 3 probs is 1
        return 2 * (sum(self.draw_manager.prob_win) + sum(self.draw_manager.prob_tie)) - 1

    def get_transitions_stick(self, draw):
        """
        Return the terminal state,
        the corresponding reward and
        the probability to reach it
        :param draw:
        :return: list having tuples of the form (next_state, reward, prob) as elements
        """
        prob = 1
        opponent_player = self.players[1 - self.current_player.id]
        reward = self._get_reward_stick(self.forward_deck, self.forward_player, opponent_player)
        return [(terminal.freeze(), reward, prob)]

    def _get_reward_hit(self, player):
        return -1 if player.is_busted() else 0

    def get_transitions_hit(self, draws):
        """
        Compute the next possible states, rewards
        and probabilities starting from
        the current draw.
        :param draws: card collection representing current state
        :return: list of all possible next states and corresponding rewards and probs
        """
        transitions = []
        cards_probs = self.forward_deck.get_cards_and_probs()
        # Simulating the draw of the next card
        for card, prob in cards_probs:
            if prob > 0:
                help_player = self.forward_player.copy_move_ahead([card])
                reward = self._get_reward_hit(help_player)
                if help_player.is_busted():
                    transitions.append((terminal.freeze(), reward, prob))
                else:
                    transitions.append((draws.copy().update(card).freeze(), reward, prob))
        return transitions

    def get_transitions(self, draws, action):
        """
        Generates all the possible next states which
        can be reached from the provided card sequence
        combination, together with corresponding rewards
        and reaching probabilities. In the non-trivial cases
        this means copying the current deck and then move
        ahead the game state according to the provided
        sequence of cards (i.e. draws), simulating
        in this way the next cards the player will draw.
        :param draws: Card sequence
        :param action: action to take
        :return: None
        """
        if draws.data[0] == END_NAME:
            return [[draws, 0, 1]]
        if len(draws.data) >= self.depth:
            return [[draws, 0, 1]]
        else:
            # There is a difference in here because we
            # create the deck having init opponent card
            # + init player card (already in self.game_deck)
            # + next player card (which have to be added)
            next_cards = (draws - self.current_player.draws).data
            self.forward_deck = self.game_deck.copy_move_ahead(next_cards)
            self.forward_player = self.current_player.copy_move_ahead(next_cards)
            if action == 'hit':
                return self.get_transitions_hit(draws)
            elif action == 'stick':
                return self.get_transitions_stick(draws)
            else:
                raise ValueError('Action not allowed')

    def returns(self):
        """
        Return the payoffs for
        the players
        :return:
        """
        logger.info('Player0 draws %s', self.players[0].draws)
        logger.info('Player1 draws %s', self.players[1].draws)

        if self.current_player.is_busted():
            if self.current_player.id == 0:
                return [-1, 1]
            else:
                return [1, -1]

        if self.players[0].sum() > self.players[1].sum():
            return [1, -1]
        elif self.players[0].sum() == self.players[1].sum():
            return [0, 0]
        else:
            return [-1, 1]

    def is_terminal(self):
        """
        Assess if the given state
        is terminal
        :return:
        """
        if self.current_player.is_busted():
            logger.info('Player %s busted', self.current_player.id)
            return True
        if self.num_played == 2:
            logger.info('Both players played')
            return True
        return False
