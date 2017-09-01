import shutil


class Printer():
    def print_title(self, str, blank_line_num=3):
        print(blank_line_num * '\n')

        terminal_size = shutil.get_terminal_size().columns
        special_char_len = (terminal_size - len(str)) // 2
        print(special_char_len * '=' + str + special_char_len * '=')

    def print_battle(self, battle_info):
        self.__print_enemy_hand_cards(battle_info)
        self.__print_field(battle_info)
        self.__print_self_hand_cards(battle_info)

    def __print_field(self, battle_info):
        field_info = self.get_field_info(battle_info)
        print(("         ............................        ............................\n" +
               "         .        .        .        .        .        .        .        .\n" +
               "         .{m31:8s}.{m21:8s}.{m11:8s}.        .{e11:8s}.{e21:8s}.{e31:8s}.\n" +
               "         .        .        .        .        .        .        .        .\n" +
               ".....................................        .....................................\n" +
               ".        .        .        .        .        .        .        .        .        .\n" +
               ".{mb:^8d}.{m32:8s}.{m22:8s}.{m12:8s}.        .{e12:8s}.{e22:8s}.{e32:8s}.{eb:^8d}.\n" +
               ".        .        .        .        .        .        .        .        .        .\n" +
               ".....................................        .....................................\n" +
               "         .        .        .        .        .        .        .        .\n" +
               "         .{m33:8s}.{m23:8s}.{m13:8s}.        .{e13:8s}.{e23:8s}.{e33:8s}.\n" +
               "         .        .        .        .        .        .        .        .\n" +
               "         ............................        ............................").format(**field_info))

    def get_field_info(self, battle_info):
        field_info = {}
        positions = [11, 12, 13, 21, 22, 23, 31, 32, 33]
        for pos in positions:
            field_info["m" + str(pos)] = self.__get_pos_info(battle_info.field, pos)
            field_info["e" + str(pos)] = self.__get_pos_info(battle_info.field, pos, self_side_flag=False)

        field_info['mb'] = battle_info.player_hero.hp
        field_info['eb'] = battle_info.enemy_hero.hp
        return field_info

    def __get_pos_info(self, field, pos, self_side_flag=True):
        general = field.get_general(pos, self_side_flag)
        if general == None:
            return ""
        else:
            return str(general.cost) + "," + str(general.att) + "," + str(general.hp)

    def __print_enemy_hand_cards(self, battle_info):
        hand_cards = battle_info.enemy_hero.hand_cards
        cards_num = len(hand_cards)

        print((" .......... " * cards_num + "\n" +
               " .        . " * cards_num + "\n" +
               " .        . " * cards_num + "\n" +
               " . {:^6d} . " * cards_num + "\n" +
               " .        . " * cards_num + "\n" +
               " .        . " * cards_num + "\n" +
               " .......... " * cards_num + "\n").format(*[card.id for card in hand_cards]))

    def __print_self_hand_cards(self, battle_info):
        hand_cards = battle_info.player_hero.hand_cards
        cards_num = len(hand_cards)

        detail_info = []
        for card in hand_cards:
            if (card.is_general_card()):
                detail_info.append("{:<2d}  {:>2d}".format(card.att, card.hp))
            else:
                detail_info.append("skill")

        print((" .......... " * cards_num + "\n" +
               " .{:<6d}  . " * cards_num + "\n" +
               " .        . " * cards_num + "\n" +
               " . {:^6d} . " * cards_num + "\n" +
               " .        . " * cards_num + "\n" +
               " . {:^6s} . " * cards_num + "\n" +
               " .......... " * cards_num + "\n").format(*[card.cost for card in hand_cards],
                                                         *[card.id for card in hand_cards],
                                                         *detail_info))