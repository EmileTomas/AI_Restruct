import shutil
from Battle import *


class Printer():
    def print_title(self, str, blank_line_num=3):
        print(blank_line_num * '\n')

        terminal_size = shutil.get_terminal_size().columns
        special_char_len = (terminal_size - len(str)) // 2
        print(special_char_len * '=' + str + special_char_len * '=')

    def print_battle(self,battle):
        m11=battle.get_pos_info(11,SELF)
        m12=battle.get_pos_info(12,SELF)
        m13=battle.get_pos_info(13,SELF)
        m21=battle.get_pos_info(21,SELF)
        m22=battle.get_pos_info(22,SELF)
        m23=battle.get_pos_info(23,SELF)
        m31=battle.get_pos_info(31,SELF)
        m32=battle.get_pos_info(32,SELF)
        m33=battle.get_pos_info(33,SELF)

        e11=battle.get_pos_info(11,ENEMY)
        e12=battle.get_pos_info(12,ENEMY)
        e13=battle.get_pos_info(13,ENEMY)
        e21=battle.get_pos_info(21,ENEMY)
        e22=battle.get_pos_info(22,ENEMY)
        e23=battle.get_pos_info(23,ENEMY)
        e31=battle.get_pos_info(31,ENEMY)
        e32=battle.get_pos_info(32,ENEMY)
        e33=battle.get_pos_info(33,ENEMY)

        mb=battle.player_hero.hp
        eb=battle.enemy_hero.hp

        if battle.turn==SELF:
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

