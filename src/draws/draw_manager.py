import itertools
import logging

import draws.draw_factory
import env
from decks import deck_factory

logger = logging.getLogger('sette-mezzo')


class DrawManager:
    """
    This class allows to work on combinations of
    card sequences, by filtering, updating or removing
    some of them.
    """

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

    def freeze(self):
        self.draw_ensemble = [x.freeze() for x in self.draw_ensemble]

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
            # we want to generate all the possible card sequences the
            # player can obtain including his initial card
            # It is like draw_list is consistent with the input_deck added by
            # the card the player already drawn
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
        """
        Opponent strategy keeps playing up to its own
        limit is reached, independently of the player sum
        """
        for draw_list in self.draw_ensemble:
            # Current sum
            draw_sum = draw_list.sum()
            # Sum without last element
            draw_sum_nolast = draw_list.delete_last().sum()
            # If draw_list sum is less than the limit
            # the player keeps hitting and so the
            # state is not a stop state
            if draw_sum < opponent_player.limit:
                continue
            elif draw_sum >= opponent_player.limit:
                # If the following is not true the player stopped before
                if draw_sum_nolast < opponent_player.limit:
                    # TODO: check the second > because might be a >=
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

    def add_terminal_state(self):
        """Add a terminal state"""
        self.add_collection([env.terminal])
