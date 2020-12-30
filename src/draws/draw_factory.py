import env
from decks import deck_factory


class DrawCollection:

    def __init__(self, draw_list):
        self.data = draw_list

    def update(self, card, inplace=True):
        if inplace:
            self.data.append(card)
            return self
        else:
            return DrawCollection(self.data + [card])

    def delete_last(self, inplace=False):
        if inplace:
            del self.data[-1]
            return self
        else:
            return DrawCollection(self.data[:-1])

    def sum(self):
        if not len(self.data):
            return -1
        mad_value = 0
        residual = env.TOP
        for card in self.data:
            card_value = deck_factory.DECK_VALUES[card]
            if card == 'mad':
                mad_value = 1
            else:
                residual = residual - card_value
        if mad_value:
            mad_value = int(residual) if residual >= 1 else 0.5
        return env.TOP - residual + mad_value

    def is_consistent(self, input_deck):
        """
        Check if all the cards contained in input_deck have smaller
        count than cards contained in the game deck.
        :param input_deck: the comparison deck
        :return: True if the input_deck is consistent. False otherwise
        """
        is_consistent = all(self.data.count(x) <= input_deck.data[x] for x in self.data)
        return is_consistent

    def freeze(self):
        return DrawCollection(tuple(self.data))

    def copy(self):
        return DrawCollection(list(self.data))

    def __len__(self):
        return len(self.data)

    def __sub__(self, other):
        i = 0
        while i < len(other) and self.data[i] == other.data[i]:
            i += 1
        return DrawCollection(self.data[i:])

    def __repr__(self):
        return str(self.data)

    def __str__(self):
        return str(self.data)
