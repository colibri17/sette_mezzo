"""
Class which allows to create, modify, copy
decks.
"""

import numpy as np

CARD_NAMES = ['1', '2', '3', '4', '5', '6', '7', 'fig', 'mad']

DECK = {'1': 4,
        '2': 4,
        '3': 4,
        '4': 4,
        '5': 4,
        '6': 4,
        '7': 3,
        'fig': 12,
        'mad': 1}

DECK_VALUES = {'1': 1,
               '2': 2,
               '3': 3,
               '4': 4,
               '5': 5,
               '6': 6,
               '7': 7,
               'fig': 0.5,
               'mad': (0.5, 1, 2, 3, 4, 5, 6, 7)}


class Deck:

    def __init__(self, deck=None):
        self.data = dict(DECK) if deck is None else dict(deck)
        self._update_probs()

    def update(self, card):
        """
        Delete from the deck the provided card
        and update the draw probabilities
        accordingly
        :param card: card
        :return: None
        """
        self.data[card] -= 1
        self._update_probs()

    def copy(self):
        """
        Copy the deck
        :return: new copied deck instance
        """
        return Deck(dict(self.data))

    def copy_move_ahead(self, cards):
        """
        Create a new copied deck instance
        and update it with the provided cards
        :param cards: list of cards used to update the copied deck
        :return: updated copied deck
        """
        forward_deck = self.copy()
        for card in cards:
            forward_deck.update(card)
        return forward_deck

    def _update_probs(self):
        """
        Recompute the probabilities of drawing
        cards in the deck
        :return: None
        """
        probs = list(np.array(list(self.data.values())) / np.array(list(self.data.values())).sum())
        self.card_probs = {card: prob for card, prob in zip(CARD_NAMES, probs)}

    def get_prob_of_card(self, card):
        """
        Get the probability of drawing
        the provided card from the deck
        :param card: card to be evaluated
        :return: a number representing the probability
        """
        return self.card_probs[card]

    def get_probs(self):
        """
        Get the probabilities of drawing
        all the cards in the deck
        :return: list of probabilities
        """
        return self.card_probs.values()

    def get_cards(self):
        """
        Get the cards in the deck
        :return: list of cards
        """
        return self.card_probs.keys()

    def get_cards_and_probs(self):
        return self.card_probs.items()

    def __repr__(self):
        return str(self.data)

    def __str__(self):
        return str(self.data)