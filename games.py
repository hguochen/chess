# std lib imports
import copy

# local imports
import constants
import pieces


class EndGameException(Exception):
    """

    EndGameException raised when the game ends.

    """
    pass


class Game(object):
    """

    Class representing the game state. Board layout is stored as a list of
    pieces as each piece knows its own position.

    """
    def __init__(self):
        # list all pieces in the game
        self._pieces = []
        self.color_to_move = constants.WHITE
        # no. of moves without a capture, 50 moves indicate a draw
        self.idle_move_count = 0
        self.last_moved_piece = None
        self.en_passant_pos = None

        # initialize board
        # pawns
        for i in xrange(8):
            self._pieces.append(pieces.Pawn(constants.WHITE, (i, 1)))
            self._pieces.append(pieces.Pawn(constants.BLACK, (i, 6)))
        # others
        ranks = {constants.WHITE: 0, constants.BLACK: 7}
        for color, rank in ranks.items():
            self._pieces.append(pieces.Rook(color, (0, rank)))
            self._pieces.append(pieces.Knight(color, (1, rank)))
            self._pieces.append(pieces.Bishop(color, (2, rank)))
            self._pieces.append(pieces.Queen(color, (3, rank)))
            self._pieces.append(pieces.King(color, (4, rank)))
            self._pieces.append(pieces.Bishop(color, (5, rank)))
            self._pieces.append(pieces.Knight(color, (6, rank)))
            self._pieces.append(pieces.Rook(color, (7, rank)))

    def get_piece_at(self, pos):
        """

        Get the piece at given position.

        """
        for piece in self._pieces:
            if piece.pos == pos:
                return piece

    def move_piece_to(self, piece, pos):
        """

        Update the piece's position and capture any existing piece. All moves
        should be made with this method.

        """
        # Make sure we're not dealing with a piece from another game:
        piece = self.get_piece_at(piece.pos)
        previous_piece = self.get_piece_at(pos)

        # Check for taking
        if previous_piece:
            # Make sure it's a different colour (should be caught elsewhere)
            if previous_piece.color == piece.color:
                raise RuntimeError("%s tried to take own %s." %
                                   (piece.name.title(), previous_piece.name))
            # Make sure it's not a king
            if previous_piece.__class__ == pieces.King:
                raise RuntimeError("%s took %s!" % (piece, previous_piece))

            # Remove the piece
            self._pieces.remove(previous_piece)

        # Move the piece
        old_pos = piece.pos
        piece.pos = pos

        # Handle special cases. Pawns:
        if piece.__class__ == pieces.Pawn:
            # Promotion. TODO: Handle promotion to other officers
            if (piece.color == pieces.WHITE and piece.pos[1] == 7 or
               piece.color == pieces.BLACK and piece.pos[1] == 0):
                self._pieces.remove(piece)
                self._pieces.append(pieces.Queen(piece.color, piece.pos))

            # En passant
            if piece.pos == self.en_passant_pos:
                if piece.pos[1] == 2:
                    taken_pawn = self.get_piece_at((piece.pos[0], 3))
                elif piece.pos[1] == 5:
                    taken_pawn = self.get_piece_at((piece.pos[0], 4))
                else:
                    raise RuntimeError("Messed up en passant.")
                if not taken_pawn:
                    raise RuntimeError("Messed up en passant again.")
                self._pieces.remove(taken_pawn)

        # Castling
        if piece.__class__ == pieces.King:
            if old_pos[0] - pos[0] == 2:  # Queen side castling
                queen_rook = self.get_piece_at((0, pos[1]))
                queen_rook.pos = (3, pos[1])
                queen_rook.has_moved = True
            if old_pos[0] - pos[0] == -2:  # King side castling
                king_rook = self.get_piece_at((7, pos[1]))
                king_rook.pos = (5, pos[1])
                king_rook.has_moved = True

        # Update en passant status
        if (piece.__class__ == pieces.Pawn and piece.pos[1] in [3, 4] and
           not piece.has_moved):
            if piece.pos[1] == 3:
                self.en_passant_pos = ((piece.pos[0], 2))
            else:
                self.en_passant_pos = ((piece.pos[0], 5))
        else:
            self.en_passant_pos = None

        # Update game state for castling etc.
        piece.has_moved = True
        self.last_moved_piece = piece

        # Alter idle move count - reset if it's a take or a pawn move
        if piece.__class__ == pieces.Pawn or previous_piece:
            self.idle_move_count = 0
        else:
            self.idle_move_count += 1

    def check_endgame(self):
        """

        Raises EndGameException if the previous move ended the game.

        """
        # See if that's the end of the game
        if not self.get_valid_moves(self.color_to_move):
            # In check? That's checkmate
            if self.in_check():
                raise EndGameException("Checkmated! %s wins!" %
                                       constants.COLOR_NAMES[
                                       not self.color_to_move].title())
            else:
                raise EndGameException("Stalemated!")

        if self.idle_move_count >= 50:
            raise EndGameException("Draw with 50 idle moves")

    def is_piece_at_risk(self, piece):
        """True if the piece can be taken, otherwise False.

        """
        opposing_moves = self.get_valid_moves(not piece.color,
                                              testing_check=True)
        for move in opposing_moves:
            if self.get_piece_at(move[1]) == piece:
                # They have a move that could potentially take the piece
                # on the next turn
                return True
        return False

    def in_check(self, color=None):
        """

        If the current player's King is under threat.

        """
        if color is None:
            color = self.color_to_move

        # See if any of the other player's moves could take the king
        king = [piece for piece in self._pieces if
                piece.__class__ == pieces.King and piece.color == color][0]
        if self.is_piece_at_risk(king):
            return True

        # The king isn't under attack
        return False

    def get_pieces(self, color=None):
        """

        Pieces with the given color, or all pieces.

        """
        if color is None:
            return self._pieces
        return [piece for piece in self._pieces if piece.color == color]

    def get_valid_moves_for_piece(self, piece, testing_check=False):
        """Get the moves the given piece can legally make.

        """
        moves = []

        # Get every possible move
        for pos in piece.get_valid_moves(self, testing_check=testing_check):
            moves.append((piece, pos))

        # If we're not worried about putting ourself in check, we're done.
        if testing_check:
            return moves

        # Filter out moves that would put the King in check
        would_check = []
        for move in moves:
            test_game = copy.deepcopy(self)
            test_game.move_piece_to(move[0], move[1])
            if test_game.in_check(piece.color):
                would_check.append(move)

        return [move for move in moves if not move in would_check]

    def get_valid_moves(self, color, testing_check=False):
        """All possible moves for the given color.

        Returns a list of tuples, piece then move. Includes taking the King,
        so check should be handled separately. Pass testing_check to allow
        moves that would put the King at risk.

        """
        moves = []

        # Get every possible move
        for piece in self.get_pieces(color):
            moves.extend(self.get_valid_moves_for_piece(piece,
                         testing_check=testing_check))
        return moves
