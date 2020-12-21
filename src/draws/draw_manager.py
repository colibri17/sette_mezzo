import itertools
import logging

import draws.draw_factory
import env
from decks import deck_factory

logger = logging.getLogger('sette-mezzo')


class DrawManager:

    def __init__(self, draw_collection):
        self.draw_ensemble = draw_collection
        self.deck_consistent_draws = []
        self.init_consistent_draws = []
        self.sum_consistent_draws = []
        self.stick_consistent_draws = []
        self.filtered_draws = []

        self.end_draws = []
        self.busted_draws = []

        self.lose, self.tie, self.win = [], [], []
        self.prob_lose, self.prob_tie, self.prob_win = [], [], []
        self.draw_probs = []

    def reset(self):
        self.draw_ensemble = []

    def update_collection(self, new_collection):
        self.draw_ensemble = list(new_collection)

    def add_collection(self, new_collection):
        self.draw_ensemble += new_collection

    def generate(self, depth):
        for i in range(1, depth + 1):
            for cards in tuple(itertools.product(deck_factory.CARD_NAMES, repeat=i)):
                d = draws.draw_factory.DrawCollection([])
                for card in cards:
                    d.update(card)
                self.draw_ensemble.append(d)
            logger.debug('Number of draws %s', len(self.draw_ensemble))
        return self

    def filter_by_sum(self):
        """
        Filter the combinations of card sequences which match with
        the maximum score allowed for the game (i.e. 7.5)
        :return: self
        """
        for draw_list in self.draw_ensemble:
            if draw_list.sum() <= env.TOP:
                self.sum_consistent_draws.append(draw_list)
        self.update_collection(self.sum_consistent_draws)
        logger.debug('Number of sum consistent draws %d', len(self.deck_consistent_draws))
        return self

    def filter_by_deck(self, input_deck, input_player):
        """
        Filter the combinations of card sequences which match with
        the cards available in the deck
        :param input_deck: the comparison deck
        :param input_player:
        :return: self
        """
        for draw_list in self.draw_ensemble:
            # We remove the cards the input player already drawn because
            # we want to generate all the next possibile card sequences the
            # player can generate
            if (draw_list - input_player.draw_collection).is_consistent(input_deck):
                self.deck_consistent_draws.append(draw_list)
        self.update_collection(self.deck_consistent_draws)
        logger.debug('Number of deck consistent draws %d', len(self.deck_consistent_draws))
        return self

    def filter_by_initial_state(self, player):
        """
        Filter the combinations of card sequences which match with the
        initial cards drawn by the player
        :param player:
        :return: self
        """
        for draw_list in self.draw_ensemble:
            if draw_list.data[:len(player.draw_collection.data)] == player.draw_collection.data:
                self.init_consistent_draws.append(draw_list)
        # TODO: add a decorator
        self.update_collection(self.init_consistent_draws)
        logger.debug('Number of init consistent draws %s', len(self.init_consistent_draws))
        return self

    def filter_by_stick(self, input_player_sum, opponent_player):
        for draw_list in self.draw_ensemble:
            draw_sum = draw_list.sum()
            # Find combinations where we lose
            if draw_sum <= env.TOP:
                # -1 so to properly handle when player_sum = 0
                no_last = draws.draw_factory.DrawCollection(draw_list.data[:-1])
                draw_sum_nolast = -1 if len(no_last) == 0 else no_last.sum()
                # Because opponent input_player does not play beyond the limit, so
                # this states should be deleted from the state space
                # because they cannot be reached
                if not (draw_sum_nolast >= opponent_player.limit):
                    # Assuming we play against the dealer we need <=
                    if draw_sum_nolast < input_player_sum < draw_sum:
                        self.stick_consistent_draws.append(draw_list)
        self.update_collection(self.stick_consistent_draws)
        logger.debug('Number of stick consistent draws %s', len(self.stick_consistent_draws))
        return self

    def filter_by_stick_complete_mixed_strategy(self, input_player_sum, opponent_player):
        """
        Player keeps to play up either the sum is greater or equal the opponent sum.
        If it hit its own limit he always stops
        """
        for draw_list in self.draw_ensemble:
            draw_sum = draw_list.sum()
            no_last = draw_list.delete_last()
            no_two_last = draw_list.delete_last().delete_last()
            draw_sum_nolast = -1 if len(no_last) == 0 else no_last.sum()
            draw_sum_notwolast = -2 if len(no_two_last) == 0 else no_two_last.sum()
            if draw_sum_nolast >= input_player_sum:
                continue
            elif draw_sum_nolast >= opponent_player.limit:
                if draw_sum_notwolast < opponent_player.limit <= draw_sum_nolast:
                    if opponent_player.limit < draw_sum_nolast:
                        self.win.append(draw_list)
                    else:
                        self.tie.append(draw_list)
                continue
            elif draw_sum_nolast < input_player_sum:
                if draw_sum > env.TOP:
                    self.win.append(draw_list)
                elif input_player_sum < draw_sum:
                    self.lose.append(draw_list)
                elif input_player_sum == draw_sum:
                    self.tie.append(draw_list)
                elif input_player_sum > draw_sum:
                    continue
                else:
                    raise ValueError
            else:
                raise ValueError
        return self

    def filter_by_stick_complete_player_strategy(self, input_player_sum, opponent_player):
        """
        Player keeps playing up to the opposite sum is beaten. In case of draw he decides to stop
        """
        for draw_list in self.draw_ensemble:
            draw_sum = draw_list.sum()
            no_last = draw_list.delete_last()
            draw_sum_nolast = -1 if len(no_last) == 0 else no_last.sum()
            if draw_sum_nolast >= input_player_sum:
                continue
            elif draw_sum_nolast < input_player_sum:
                if draw_sum > env.TOP:
                    self.win.append(draw_list)
                elif input_player_sum < draw_sum:
                    self.lose.append(draw_list)
                elif input_player_sum == draw_sum:
                    self.tie.append(draw_list)
                elif input_player_sum > draw_sum:
                    continue
                else:
                    raise ValueError
            else:
                raise ValueError
        return self

    def filter_by_stick_complete_bookmaker_strategy(self, input_player_sum, opponent_player):
        """
        Bookmaker strategy keeps playing up to its own limit is reached, independently of the player sum
        """
        for draw_list in self.draw_ensemble:
            draw_sum = draw_list.sum()
            draw_sum_nolast = draw_list.delete_last().sum()
            if draw_sum < opponent_player.limit:
                continue
            elif draw_sum >= opponent_player.limit:
                if draw_sum_nolast < opponent_player.limit:
                    if draw_sum > env.TOP or input_player_sum > draw_sum:
                        self.win.append(draw_list)
                    elif input_player_sum < draw_sum:
                        self.lose.append(draw_list)
                    elif input_player_sum == draw_sum:
                        self.tie.append(draw_list)
                    else:
                        raise ValueError
            else:
                raise ValueError
        return self

    def get_prob_sum_complete(self, input_deck, input_player):
        for draw_ensemble_sum, draw_ensemble in zip([self.prob_lose, self.prob_tie, self.prob_win],
                                                    [self.lose, self.tie, self.win]):
            for draw in draw_ensemble:
                corrected_draw = draw - input_player.draw_collection
                help_deck = input_deck.copy()
                draw_prod = 1
                for card_name in corrected_draw.data:
                    draw_prod *= help_deck.get_prob_of_card(card_name)
                    help_deck.update(card_name)
                draw_ensemble_sum.append(draw_prod)
        return self

    def get_prob_sum(self, input_deck, input_player):
        for draw in self.draw_ensemble:
            corrected_draw = draw - input_player.draw_collection
            help_deck = input_deck.copy()
            draw_prod = 1
            for card_name in corrected_draw.data:
                draw_prod *= help_deck.get_prob_of_card(card_name)
                help_deck.update(card_name)
            self.draw_probs.append(draw_prod)
        return self

    def add_terminal_state(self):
        """Add a terminal state"""
        self.add_collection([env.terminal])
