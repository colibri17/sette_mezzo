import decks
import draws
import env


class Player:

    def __init__(self):
        self.draw = draws.Draw([])
        self.deck = decks.Deck()
        self.burst = False

    def update(self, card_name):
        self.draw.update_with_name(card_name)
        self.deck.update(card_name)

    def sum(self):
        return self.draw.sum()

    def is_burst(self):
        return self.draw.sum() > env.TOP

    def set_burst(self, burst):
        self.burst = burst

