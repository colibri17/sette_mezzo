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
        self.deck = DECK if deck is None else deck
        self._update_probs()

    def update(self, card):
        self.deck[card] -= 1
        self._update_probs()

    def _update_probs(self):
        probs = list(np.array(list(self.deck.values())) / np.array(list(self.deck.values())).sum())
        self.card_probs = {card: prob for card, prob in zip(CARD_NAMES, probs)}

    def get_allowed_cards(self):
        return list(key for key, value in self.card_probs.items() if value > 0)

    def get_prob_of_card(self, card):
        return self.card_probs[card]

    def get_probs(self):
        return self.card_probs.values()
