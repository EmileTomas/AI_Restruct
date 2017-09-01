from User import User
import sys
from Printer import Printer

if __name__ == '__main__':
    printer = Printer()
    user = User(sys.argv[1], "1")
    user.login()
    user.start_match(output=True)

    while True:
        user.round_begin()
        user.wait_or_attack(output=True)

        if user.battle_over():
            break

    user.show_result()
