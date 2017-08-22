import shutil
from Battle import *


class Printer():
    def print_title(self, str, blank_line_num=3):
        print(blank_line_num * '\n')

        terminal_size = shutil.get_terminal_size().columns
        special_char_len = (terminal_size - len(str)) // 2
        print(special_char_len * '=' + str + special_char_len * '=')

    def print_battle(self, battle):

        m31=m21=m11=e11=e21=e31=1
        mb=m32=m22=m12=e12=e22=e32=eb=2
        m33=m23=m13=e13=e23=e33=3


        if battle.turn==SELF_TURN:
            print("                     Att                                  Def")
        else:
            print("                     Def                                  Att")

        print("         ............................        ............................")
        print("         .        .        .        .        .        .        .        .")
        print("         .%-8s.%-8s.%-8s.        .%-8s.%-8s.%-8s." % (m31, m21, m11, e11, e21, e31))
        print("         .        .        .        .        .        .        .        .")
        print(".....................................        .....................................")
        print(".        .        .        .        .        .        .        .        .        .")
        print(".%-8s.%-8s.%-8s.%-8s.        .%-8s.%-8s.%-8s.%+8s." % (mb, m32, m22, m12, e12, e22, e32, eb))
        print(".        .        .        .        .        .        .        .        .        .")
        print(".....................................        .....................................")
        print("         .        .        .        .        .        .        .        .")
        print("         .%-8s.%-8s.%-8s.        .%-8s.%-8s.%-8s.  " % (m33, m23, m13, e13, e23, e33))
        print("         .        .        .        .        .        .        .        .")
        print("         ............................        ............................")

