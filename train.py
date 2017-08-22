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

    printer.print_title("Round Begin")
    user.round_begin(True)
    printer.print_battle(user.battle)
    if user.battle.turn == SELF:
        printer.print_title("ATTACK USE CARD")
        user.attack()
    else:
        pass

    # 解析卡牌使用后的通知proto
    user.push_info_listener.parse_frame(output=True)
    printer.print_battle(user.battle)

    printer.print_title("Round End")
    # user.round_end(True)
