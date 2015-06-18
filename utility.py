# std lib imports
# local imports
import constants


def get_grid_pos(coordinate):
        """

        Convert input coordinate to system coordinate.
        ie.
        A1 => (0, 0)
        H8 => (7, 7)

        """
        column = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        row = ['1', '2', '3', '4', '5', '6', '7', '8']
        return (column[coordinate[0]] + row[coordinate[1]])


def get_coords_for_grid_ref(grid_ref):
    """Convert traditional coordinates to our coordinates.

    e.g. A1 -> (0, 0)
         H8 -> (7, 7)

    """
    x_for_file = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6,
                  "H": 7}
    y_for_rank = {"1": 0, "2": 1, "3": 2, "4": 3, "5": 4, "6": 5, "7": 6,
                  "8": 7}
    file_letter = grid_ref[0]
    rank_number = grid_ref[1]
    return (x_for_file[file_letter], y_for_rank[rank_number])


def draw_game(game, selected_piece=None):
    """

    Print a string that represents the current game state.

    Uses ANSI color codes to make it readable - game isn't playable without
    color support in the terminal.

    """
    # Get a string for each rank
    rank_strings = []

    # Get possible moves for selected piece
    if selected_piece:
        valid_moves = game.get_valid_moves_for_piece(selected_piece)
        valid_squares = [move[1] for move in valid_moves]
    else:
        valid_squares = []

    # Ranks, top to bottom:
    for y in reversed(range(8)):
        rank_string = " %i " % (y + 1)
        for x in range(8):
            # Get foreground text (must make up two characters)
            piece = game.get_piece_at((x, y))
            if piece:
                if piece == selected_piece or piece == game.last_moved_piece:
                    piece_char = constants.SELECTED_PIECE_CHARACTERS[
                        piece.__class__]
                else:
                    piece_char = constants.PIECE_CHARACTERS[piece.__class__]
                foreground_text = piece_char + " "
            else:
                foreground_text = "  "

            # Get background colour
            if (x, y) in valid_squares:
                square_color = 'HIGHLIGHTED'
            elif x % 2 == y % 2:
                square_color = 'DARK'
            else:
                square_color = 'LIGHT'
            piece_color = constants.WHITE
            if piece and piece.color == constants.BLACK:
                piece_color = constants.BLACK
            begin_code = constants.ANSI_BEGIN % "%s;%s" % (constants.ANSI_BG[square_color],
                                                           constants.ANSI_FG[piece_color])
            rank_string += "%s%s%s" % (begin_code, foreground_text, constants.ANSI_END)
        rank_strings.append(rank_string)
    file_labels = "   A B C D E F G H"

    print "\n".join(rank_strings) + "\n" + file_labels
