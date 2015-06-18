# std lib imports
import sys

# local imports
import player
import constants
import games
import utility


def main():
    game = games.Game()

    # get game type
    print "Welcome to chess! Select a game type:"
    print
    print "1. AI vs. AI"
    print "2. Human vs. AI"
    print "3. Human vs. Human"
    print ""
    while True:
        option = raw_input("Select game mode:: ").strip()
        if not option in ["1", "2", "3"]:
            print "Select an option above (1-3)"
            continue
        if option == "1":
            players = {constants.WHITE: player.Computer(game, constants.WHITE),
                       constants.BLACK: player.Computer(game, constants.BLACK)}
        elif option == "2":
            players = {constants.WHITE: player.Human(game, constants.WHITE),
                       constants.BLACK: player.Computer(game, constants.BLACK)}
        elif option == "3":
            players = {constants.WHITE: player.Human(game, constants.WHITE),
                       constants.BLACK: player.Human(game, constants.BLACK)}
        else:
            raise RuntimeError()
        break

    # game loop
    try:
        while True:
            utility.draw_game(game)

            player_to_move = players[game.color_to_move]
            move = player_to_move.get_move()
            game.move_piece_to(move[0], move[1])
            game.color_to_move = not game.color_to_move
            game.check_endgame()

    except games.EndGameException as e:
        utility.draw_game(game)
        print e

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "\nBye!"
        sys.exit()
