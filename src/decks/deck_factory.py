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
        self.data[card] -= 1
        self._update_probs()

    def copy(self):
        return Deck(dict(self.data))

    def _update_probs(self):
        probs = list(np.array(list(self.data.values())) / np.array(list(self.data.values())).sum())
        self.card_probs = {card: prob for card, prob in zip(CARD_NAMES, probs)}

    def get_prob_of_card(self, card):
        return self.card_probs[card]

    def get_probs(self):
        return self.card_probs.values()

    def get_cards(self):
        return self.card_probs.keys()

    def get_cards_and_probs(self):
        return self.card_probs.items()

    def is_feasible(self):
        return all(value >= 0 for value in self.card_probs.values())

    def __repr__(self):
        return str(self.data)

    def __str__(self):
        return str(self.data)