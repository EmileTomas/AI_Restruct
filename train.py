from User import *
from Printer import *
import time
import sys

if __name__ == '__main__':
    printer = Printer()

    user = User(sys.argv[1], "1")
    user.login()
    user.start_match_fight(output=True)

    GAME_NOT_END = False

    while True:
        printer.print_title("Round Begin")
        user.round_begin(True)

        if user.battle.turn == SELF_TURN:
            printer.print_title("ATTACK USE CARD")
        else:
            pass

        printer.print_title("Round End")
        user.round_end(True)

        time.sleep(10)


