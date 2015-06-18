# std lib imports
import re
import copy
import random

# local imports
import constants
import utility
import pieces


class AbstractPlayer(object):
    """

    Abstract class with defines a chess player.

    """
    def __init__(self, game, color):
        self.game = game
        self.color = color

    def get_move(self):
        """

        Return the move that the player wants to make based on the
        current game state.

        """
        raise NotImplementedError()


class Human(AbstractPlayer):
    """

    Represents a human player.

    Read command-line input to get the move.

    """
    def get_move(self):
        """

        Get command line input to move the piece.

        """
        while True:
            # current status
            if self.game.in_check(self.color):
                check_string = " (You're in check!)"
            else:
                check_string = ""
            print "%s to play.%s" % (constants.COLOR_NAMES[self.color].title(),
                                     check_string)

            # Get user input
            move_string = raw_input("Your move: ").strip().upper()

            # Is it an explicit move (from -> to)?
            explicit_match = re.match(r"([A-H][1-8]).*([A-H][1-8])",
                                      move_string)
            if explicit_match:
                from_ref = explicit_match.group(1)
                to_ref = explicit_match.group(2)
                from_pos = utility.get_coords_for_grid_ref(from_ref)
                to_pos = utility.get_coords_for_grid_ref(to_ref)
                piece = self.game.get_piece_at(from_pos)

                # Validate the move
                if not piece:
                    print "No piece at %s" % from_ref
                    continue
                if not piece.color == self.color:
                    print "That's not your %s!" % piece.name
                    continue
                valid_moves = self.game.get_valid_moves_for_piece(piece)
                valid_squares = [move[1] for move in valid_moves]
                if not to_pos in valid_squares:
                    print "That %s can't move to %s!" % (piece.name, to_ref)
                    continue
                return (piece, to_pos)

            # Specified a single square
            if not re.match(r"[A-H][1-8]", move_string):
                print "That's not a valid move. Examples: 'A8', 'D2D4', etc."
                continue
            pos = utility.get_coords_for_grid_ref(move_string)
            piece_on_target = self.game.get_piece_at(pos)

            # If it's not one of ours, see if any of our pieces can move there
            if not piece_on_target or not piece_on_target.color == self.color:
                valid_moves = self.game.get_valid_moves(self.color)
                moves_to_target = [move for move in valid_moves if
                                   move[1] == pos]
                if not moves_to_target:
                    action_string = "move there"
                    if piece_on_target:
                        action_string = ("take that %s" %
                                         constants.PIECE_NAMES[piece_on_target
                                         .__class__])
                    print "None of your pieces can %s." % action_string
                    continue
                elif len(moves_to_target) == 2:
                    piece_one = moves_to_target[0][0]
                    piece_two = moves_to_target[1][0]
                    if piece_one.__class__ == piece_two.__class__:
                        print "Two %ss can move there." % piece_one.name
                    else:
                        print ("The %s and the %s can both move there." %
                               (piece_one.name, piece_two.name))
                    continue
                elif len(moves_to_target) > 1:
                    print "Lots of pieces can move there."
                    continue
                elif len(moves_to_target) == 1:
                    return moves_to_target[0]
                else:
                    raise RuntimeError("Never reached.")

            # It's one of ours; show where it can move and ask again
            piece = piece_on_target
            valid_moves = self.game.get_valid_moves_for_piece(piece)
            if not valid_moves:
                print "That %s has nowhere to go!" % piece.name
                continue

            # Move the piece
            utility.draw_game(self.game, selected_piece=piece)
            input_string = raw_input("Move the %s to: " % piece.name).strip() \
                .upper()
            if not constants.GRID_REF.match(input_string):
                utility.draw_game(self.game)
                print "That's not a square!"
                continue
            coords = utility.get_coords_for_grid_ref(input_string)
            valid_squares = [move[1] for move in valid_moves]
            if coords == piece.pos:
                utility.draw_game(self.game)
                print "That %s is already on %s!" % (piece.name, input_string)
                continue
            if not coords in valid_squares:
                utility.draw_game(self.game)
                print "That %s can't move to %s" % (piece.name, input_string)
                continue
            return (piece, coords)


class Computer(AbstractPlayer):
    """

    AI-controlled player.

    Considers checkmate, checks, captures, retreats and pawn advances.

    """
    def get_move(self):
        if not self.game.color_to_move == self.color:
            raise RuntimeError("Not my turn!")

        available_moves = self.game.get_valid_moves(self.color)

        # Find checking moves
        checking_moves = []
        riskless_checking_moves = []
        for move in available_moves:
            test_game = copy.deepcopy(self.game)
            test_game.move_piece_to(move[0], move[1])
            if test_game.in_check(not self.color):
                # Check for potential mates
                if not test_game.get_valid_moves(not self.color):
                    return move
                checking_moves.append(move)
                if not test_game.is_piece_at_risk(move[0]):
                    riskless_checking_moves.append(move)

        # Find taking moves
        taking_moves = [move for move in available_moves if
                        self.game.get_piece_at(move[1])]

        # Retreats
        retreats = {}
        for move in available_moves:
            if self.game.is_piece_at_risk(move[0]):
                test_game = copy.deepcopy(self.game)
                test_game.move_piece_to(move[0], move[1])
                if test_game.is_piece_at_risk(test_game.get_piece_at(move[1])):
                    continue
                retreats[move] = move[0].value
        highest_value = -999999
        best_retreat = None
        for move, value in retreats.items():
            if value > highest_value:
                best_retreat = move
                highest_value = value
        if best_retreat:
            return best_retreat

        # Find riskless taking moves (free material)
        riskless_taking_moves = []
        for move in taking_moves:
            test_game = copy.deepcopy(self.game)
            test_game.move_piece_to(move[0], move[1])
            if not test_game.is_piece_at_risk(test_game.get_piece_at(move[1])):
                riskless_taking_moves.append(move)
        if riskless_taking_moves:
            return random.choice(riskless_taking_moves)

        # A check is pretty good if it doesn't cost anything
        if riskless_checking_moves:
            return random.choice(riskless_checking_moves)

        # Find the best value taking move
        valued_taking_moves = {}
        for move in taking_moves:
            our_piece = move[0]
            their_piece = self.game.get_piece_at(move[1])
            move_value = their_piece.value - our_piece.value
            valued_taking_moves[move] = move_value
        highest_value = -999999
        best_taking_move = None
        for move, value in valued_taking_moves.items():
            if value > highest_value:
                best_taking_move = move
                highest_value = value

        # Find pawn moves
        pawn_moves = [move for move in available_moves if
                      move[0].__class__ == pieces.Pawn]

        # Good options
        good_options = []
        if pawn_moves:
            good_options.append(random.choice(pawn_moves))
        if checking_moves:
            good_options.append(checking_moves)
        if best_taking_move:
            good_options.append(best_taking_move)
        if good_options:
            return random.choice(good_options)

        # Make any move
        return random.choice(available_moves)
