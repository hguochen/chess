# std lib imports
import copy

# local imports
import constants
import utility

# ------------------------ Piece Abstract Class ------------------------------#

# Piece types
WHITE = True
BLACK = False


class AbstractPiece(object):
    """

    Abstract class which defines a chess piece. Each chess piece stores their
    own position on board. Subclasses must implement get_vali_moves method.

    """
    def __init__(self, color, position):
        if not color in (WHITE, BLACK):
            raise ValueError('Not a valid color')
        self.color = color
        self.pos = position
        self.name = constants.PIECE_NAMES[self.__class__]
        self.value = constants.PIECE_VALUES[self.__class__]
        self.has_moved = False

    def __str__(self):
        color = constants.COLOR_NAMES[self.color]
        piece = constants.PIECE_NAMES[self.__class__]
        pos = utility.get_grid_pos(self.pos)
        return "%s %s at %s" (color.title(), piece, pos)

    def __repr__(self):
        return self.__str__()

    def get_valid_moves(self, game, check=False):
        """

        Moves allowed in the game. Return a list of positions.
        eg.[(1, 2), (5, 6), ...]

        """
        raise NotImplementedError()

    def get_moves_direction(self, game, direction):
        """

        Find all the moves in a given direction.

        Direction is an offset tuple. eg. (1, 2)

        """
        moves = []

        # start from curr position
        test_move = self.pos

        # add offset until an invalid move is found
        while True:
            test_move = (test_move[0] + direction[0],
                         test_move[1] + direction[1])
            # no more moves
            if (test_move[0] < 0 or test_move[0] > 7 or test_move[1] < 0 or
               test_move[1] > 7):
                break

            # collosion with a piece
            # either way the move ends
            hit = game.get_piece_at(test_move)
            if hit:
                if hit.color == self.color:
                    # same color. not a valid move.
                    break
                else:
                    # different color. is a valid move
                    moves.append(test_move)
                    break

        return moves

    def remove_invalid_moves(self, game, moves):
        """

        Given a list of potential moves, remove all invalid moves.

        Invalid moves are:
        1. not on the board
        2. collision with own piece

        """
        valid_moves = []
        for pos in moves:
            if pos == self.pos:
                continue
            # move is on board
            if (pos[0] < 0 or pos[0] > 7 or pos[1] < 0 or pos[1] > 7):
                # Off the board
                continue

            # collision with own piece
            taken_piece = game.get_piece_at(pos)
            if taken_piece and taken_piece.color == self.color:
                continue

            valid_moves.append(pos)
        return valid_moves

# ------------------------ Piece Concrete Class ------------------------------#


class Pawn(AbstractPiece):
    def get_valid_moves(self, game, testing_check=False):
        """

        Pawns move 1/2 squares each time.

        """
        moves = []

        # get all valid square
        if self.color == WHITE:
            forward_one = (self.pos[0], self.pos[1] + 1)
            forward_two = (self.pos[0], self.pos[1] + 2)
            take_left = (self.pos[0] - 1, self.pos[1] + 1)
            take_right = (self.pos[0] + 1, self.pos[1] + 1)
        elif self.color == BLACK:
            forward_one = (self.pos[0], self.pos[1] - 1)
            forward_two = (self.pos[0], self.pos[1] - 2)
            take_left = (self.pos[0] + 1, self.pos[1] - 1)
            take_right = (self.pos[0] - 1, self.pos[1] - 1)
        else:
            raise RuntimeError("Square not reached.")

        # one square forward
        if not game.get_piece_at(forward_one):
            moves.append(forward_one)

        # two square forward at starting position
        if ((self.color == WHITE and self.pos[1] == 1) or
           (self.color == BLACK and self.pos[1] == 6)):
            if not game.get_piece_at(forward_two):
                moves.append(forward_two)

        # move diagonally
        for taking_move in take_left, take_right:
            taken_piece = game.get_piece_at(taking_move)
            if taken_piece and not taken_piece.color == self.color:
                moves.append(taking_move)

        if game.en_passant_pos in [take_left, take_right]:
            moves.append(game.en_passant_pos)

        return self.remove_invalid_moves(game, moves)


class Knight(AbstractPiece):
    def get_valid_moves(self, game, testing_check=False):
        """

        Knights move in 2x + 1/-1 positions each time.

        """
        moves = []

        offsets = [(1, 2), (2, 1), (2, -1), (1, -2),
                   (-1, -2), (-2, -1), (-2, 1), (-1, 2)]
        for offset in offsets:
            moves.append((self.pos[0] + offset[0], self.pos[1] + offset[1]))

        # Remove obviously invalid moves
        moves = self.remove_invalid_moves(game, moves)
        return moves


class King(AbstractPiece):
    def get_valid_moves(self, game, testing_check=False):
        """

        King moves 1 square at a time.

        """
        moves = []

        offsets = [constants.UP,
                   constants.UP_RIGHT,
                   constants.RIGHT,
                   constants.DOWN_RIGHT,
                   constants.DOWN,
                   constants.DOWN_LEFT,
                   constants.LEFT,
                   constants.UP_LEFT]
        for offset in offsets:
            moves.append((self.pos[0] + offset[0], self.pos[1] + offset[1]))

        # castling move
        y_pos = self.pos[1]
        queen_rook = game.get_piece_at((0, y_pos))
        king_rook = game.get_piece_at((7, y_pos))
        for rook in queen_rook, king_rook:
            if testing_check:
                continue

            if not rook:
                continue

            if game.in_check(self.color):
                continue

            if self.has_moved or rook.has_moved:
                continue

            # make sure squares between king and rook are vacant
            squares_between = []
            if rook.pos[0] < self.pos[0]:  # Queen side
                squares_between = [(1, y_pos), (2, y_pos), (3, y_pos)]
            else:  # King side
                squares_between = [(5, y_pos), (6, y_pos)]
            all_squares_vacant = True
            for square in squares_between:
                if game.get_piece_at(square):
                    all_squares_vacant = False
            if not all_squares_vacant:
                continue

            # none of the squares checks king
            crosses_check = False
            for square in squares_between:
                test_game = copy.deepcopy(game)
                test_game.move_piece_to(self, square)
                if test_game.in_check(self.color):
                    crosses_check = True
                    break
            if crosses_check:
                continue

            # castling on quee side is allowed
            if rook == queen_rook:
                moves.append((2, self.pos[1]))
            else:
                moves.append((6, self.pos[1]))

        # remove invalid moves
        return self.remove_invalid_moves(game, moves)


class Queen(AbstractPiece):
    def get_valid_moves(self, game, testing_check=False):
        """

        Queen moves in all horizontal, parallel and diagonal moves.

        """
        moves = []

        # All directions are valid
        directions = [constants.UP,
                      constants.UP_RIGHT,
                      constants.RIGHT,
                      constants.DOWN_RIGHT,
                      constants.DOWN,
                      constants.DOWN_LEFT,
                      constants.LEFT,
                      constants.UP_LEFT]

        # Keep moving in each direction until we hit a piece or the edge
        # of the board.
        for direction in directions:
            moves.extend(self.get_moves_direction(game, direction))

        return self.remove_invalid_moves(game, moves)


class Bishop(AbstractPiece):
    def get_valid_moves(self, game, testing_check=False):
        """

        Bishop moves in all diagonal squares.

        """
        moves = []

        # only diagonal direction are valid
        directions = [constants.UP_LEFT,
                      constants.UP_RIGHT,
                      constants.DOWN_LEFT,
                      constants.DOWN_RIGHT]

        # move in direction until we hit a piece or edge of board
        for direction in directions:
            moves.extend(self.get_moves_direction(game, direction))
        return self.remove_invalid_moves(game, moves)


class Rook(AbstractPiece):
    def get_valid_moves(self, game, testing_check=False):
        """

        Rook moves in all horizontal squares only.

        """
        moves = []

        directions = [constants.UP, constants.RIGHT,
                      constants.LEFT, constants.DOWN]

        # Keep moving in each direction until we hit a piece or the edge
        # of the board.
        for direction in directions:
            moves.extend(self.get_moves_direction(game, direction))

        moves = self.remove_invalid_moves(game, moves)
        return moves
