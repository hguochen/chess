# std lib imports
import re
from pieces import King, Queen, Rook, Bishop, Knight, Pawn
# local imports

# ------------------------ GLOBAL CONSTANTS ----------------------------------#
# Regular expression for a valid grid reference (only used for input)
GRID_REF = re.compile(r"^[A-H][1-8]$")

# Piece types
WHITE = True
BLACK = False

# Color names
COLOR_NAMES = {WHITE: 'white', BLACK: 'black'}

# Square colours
DARK = "DARK"
LIGHT = "LIGHT"
HIGHLIGHTED = "HIGHLIGHTED"

# Piece names
PIECE_NAMES = {King: 'king',
               Queen: 'queen',
               Rook: 'rook',
               Bishop: 'bishop',
               Knight: 'knight',
               Pawn: 'pawn'}

# Values represented by each piece
PIECE_VALUES = {King: 111,
                Queen: 7,
                Rook: 5,
                Bishop: 3,
                Knight: 3,
                Pawn: 1}

# Characters to represent pieces
SELECTED_PIECE_CHARACTERS = {King: "K",
                             Queen: "Q",
                             Rook: "R",
                             Bishop: "B",
                             Knight: "N",
                             Pawn: "P"}

PIECE_CHARACTERS = {King: "K",
                    Queen: "Q",
                    Rook: "R",
                    Bishop: "B",
                    Knight: "N",
                    Pawn: "P"}

# directions
UP = (0, 1)
UP_RIGHT = (1, 1)
RIGHT = (1, 0)
DOWN_RIGHT = (1, -1)
DOWN = (0, -1)
DOWN_LEFT = (-1, -1)
LEFT = (-1, 0)
UP_LEFT = (-1, 1)

# ANSI color codes used to display the chess board
ANSI_BEGIN = "\033[%sm"
ANSI_END = "\033[0m"
ANSI_BG = {DARK: "42", LIGHT: "43", HIGHLIGHTED: "42"}
ANSI_FG = {WHITE: "37", BLACK: "30"}
