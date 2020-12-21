# Introduction
This repository implements an algorithm to optimally playing "sette e mezzo" (https://en.wikipedia.org/wiki/Sette_e_mezzo).
The algorithm uses a policy iteration algorithm to identify the best choice to make in a game status. The two possible choice are `hit`, meaning
to draw the next card, and `stick`, meaning to stop.   
The algorithm computes the best strategy by assuming the opponent player keeps playing up to a certain own limit (which can be specified by the user) is reached, independently of the player sum.
Other opponent strategies can be found in the `draw_manager.py` module.

# Rules
Sette e mezzo is played with a 40-card deck, a standard deck with eights, nines, and tens removed. The value of cards ace 
through seven is their pip value (1 through 7), face cards are worth 0.5 point each.  
At the very beginning of the match both players draw a card.  
Then, the first player repeatedly picks cards from the deck until either reaches a scored greater
than 7.5 (in this is case is boosted and immediately loses the game) or he stops, reaching a certain score 
defined by the sum of the values of his cards that is not releaved to the opponent.   
Then, the opponent player repeats the process by deciding whether to pick or stop at each step. In this variant of the game, 
he stops as soon as he reaches a score greater or equal to 5.   
At the end of the game, both players compare their scores. The player wins when his score is greater than 
the score of the opponent.

# Install
Python dependencies can be installed with pipenv. From the code directory run:  
```pipenv install```
