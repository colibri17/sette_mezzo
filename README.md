# Introduction
This repository implements an algorithm to optimally playing "sette e mezzo" (https://en.wikipedia.org/wiki/Sette_e_mezzo).
The algorithm uses a policy iteration algorithm to identify the best choice to make in a game status. The two possible choice are `hit`, meaning
to draw the next card, and `stick`, meaning to stop.   
The algorithm computes the best strategy by assuming the opponent player keeps playing up to a certain own limit (which can be specified by the user) is reached, independently of the player sum.
Other opponent strategies can be found in the `draw_manager.py` module.

# Install
Python dependencies can be installed with pipenv. From the code directory run:  
```pipenv install```
