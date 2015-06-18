Authored by: Hou GuoChen Gary

# Project folder structure
--------------------------

The project folder is structured as follows:

	liftigniter_challenge
		__init__.py
		constants.py
		games.py
		main.py
		pieces.py
		player.py
		README.md
		utility.py
		
constants.py: global constants used for the project

games.py: game class controller that controls the process of the game.

main.py: main method that defines the iteraction with user on command line input.

pieces.py: chess piece classes that models typical chess pieces.

player.py: defines the player and A! class

README.md: (this file) instructions for interacting with the program

utility.py: custom utility functions used by modules.

# How to play
-------------

## Input

The solution supports interaction via stdin in the command line interface.
Note: Game requires system support for ANSI color code in order to play.

1. Navigate to project level folder `../path/to/liftigniter_challenge`
2. In command line interface, type the following to start game:

		$ python main.py
		
3. You should see the following welcome message:

		Welcome to LiftIgniter chess! Select a game type:

		1. AI vs. AI
		2. Human vs. AI
		3. Human vs. Human

		Select game mode:: 

4. Input `1` to watch 2 AI players play chess against each other.
5. Input `2` to play against AI player.
6. Input `3` to play against another player.

7. Game mode ending with different possible outcomes would result in the following outputs:

DRAW

		Draw with 50 idle moves
		
STALEMATE

		Stalemated!
		
WHITE WIN
	
		Checkmated! White wins!
		
BLACK WIN
		
		Checkmated! Black wins!