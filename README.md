# Summary
This repository implements an algorithm to optimally playing [Sette e mezzo](https://en.wikipedia.org/wiki/Sette_e_mezzo).
The algorithm uses policy iteration to identify the best choice to make in the game state. The two possible choices are `hit`, meaning
to draw the next card, and `stick`, meaning to stop.
The algorithm computes the best strategy by assuming the opponent player keeps playing up to a certain score
(which is set to 5 and can be specified by the user) is reached, independently of the player sum.

# Rules
Sette e mezzo is played with a 40-card deck, a standard deck with eights, nines, and tens removed. The value of cards ace 
through seven is their pip value (1 through 7), face cards are worth 0.5 point each.  
At the very beginning of the match both players draw a card.  
Then, the first player repeatedly picks cards from the deck until either reaches a scored greater
than 7.5 (in this is case is boosted and immediately loses the game) or he sticks, reaching a certain score 
defined by the sum of the values of his cards that is not releaved to the opponent.   
Then, the opponent player repeats the process by deciding whether to draw a card or stick at each step. In this variant of the game, 
he sticks as soon as he reaches a score greater than or equal to a certain limit (which is set to 5 and can be specified by the user).   
At the end of the game, both players compare their scores. The player wins when his score is greater than 
the score of the opponent.

# Solving the game
The algorithm used to solve the game is based on reinforcement learning. Specifically, policy iteration is implemented.  
Policy iteration is composed by two steps:
* *Policy evaluation*, which finds the value of each state according to the current policy. This step is performed by using dynamic programming.
* *Policy improvement*, which greedly update the current policy towards the best next possible action.
These two steps are computed iteratively up to convergence.
  
The game proceeds as it follows:
* The user is asked for player and opponent cards.  
  *Example: Assume for example player card is 2 and opponent card is 6*
* All the possible states are generated. Namely, the combinations of all the allowed card sequences 
  which can be drawn are produced. This process is carried out by first generating all the 
  possible card combinations with a given lenght. Then, we filter out the ones that are not allowed. 
  Specifically:
  * If a combination does not match with the cards in the deck, it is filtered out.
  * If a combination scores more than 7.5, it is filtered out.
  * If a combination does not match with the initial card drawn by the player, it is filtered out
* The reinforcement learning applies. As said, we apply policy iteration algorithm, iteratively ciclying
  on policy evaluation and policy improvements steps. 

# Install
The library can be installed by using `pip`

```pipenv install```
