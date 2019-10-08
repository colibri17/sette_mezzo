import decks
import env


class Draw:

    def __init__(self, draw):
        self.draw_data = draw

    def update(self, card):
        self.draw_data.append(card)
        return self.draw_data

    def update_with_name(self, card_name):
        self.draw_data.append((card_name, decks.DECK_VALUES[card_name]))
        return self.draw_data

    def sum(self):
        sum_not_mad = sum(value for name, value in self.draw_data if name != 'mad')
        if 'mad' in map(lambda x: x[0], self.draw_data):
            mad_allowed = tuple(x for x in decks.DECK_VALUES['mad'] if x + sum_not_mad <= env.TOP)
            mad_value = 0.5 if not len(mad_allowed) else max(mad_allowed)
            sum_not_mad += mad_value
        return sum_not_mad

    def is_consistent(self, deck):
        draw_names = list(map(lambda x: x[0], self.draw_data))
        is_consistent = all(draw_names.count(x) <= deck.deck_data[x] for x in draw_names)
        return is_consistent

    def without_last_entry(self):
        return self.draw_data[:-1]

    def __len__(self):
        return len(self.draw_data)

    def __sub__(self, other):
        i = 0
        while i < len(other) and self.draw_data[i] == other.draw_data[i]:
            i += 1
        return Draw(self.draw_data[i:])
