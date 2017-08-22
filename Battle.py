# Card Type
MILITARY_CARD = 1
SKILL_CARD = 2

# Attack Range
SINGLE_ATTAK = 1
HORIZONTAL_ATTAK = 2
VERTICAL_ATTAK = 3
GLOBAL_ATTACK = 4

# Militray Type
JIXIE_CARD = 1
ZHANFA_CARD = 2
CHESHI_CARD = 3

# Effect Type
CRYSTAL = 0
HEAL = 1
DAMAGE = 2
ANGRY = 3
PROTECT = 4
DRAW_CARD = 5

# DAMAGE Tyoe
DIZZY_EFFECT = 1
SINGLE_EFFECT = 2
GLOBAL_EFFECT = 3

# Round turn
SELF = 1
ENEMY = 2


class Card:
    def __init__(self, card_id, type, cost):
        self.sid = card_id
        self.type = type
        self.cost = cost
        self.id = None


class MilitaryCard(Card):
    def __init__(self, card_json):
        Card.__init__(self, card_json['id'], card_json['type'], int(card_json['cost']))
        self.military_type = card_json['generalType']
        self.attack = card_json['att']
        self.hp = card_json['hp']
        self.attack_range = self.__parse_attak_range(card_json['skillIntro'])
        self.special_attack = self.__parse_special_attack(card_json)

    def __parse_attak_range(self, skill_intro):
        dict = {'单体': 1, '横排': 2, '竖排': 3, '全体': 4}
        # 振奋同样是单体
        return dict.get(skill_intro[:2], 1)

    def __parse_special_attack(self, card_json):
        if (card_json['generalType'] == ZHANFA_CARD):
            if (card_json['skillIntro'][:2] == '振奋'):
                return 0
            else:
                return card_json['skillIntro'].split('，')[1][0]
        else:
            return None


class SkillCard(Card):
    def __init__(self, card_json):
        Card.__init__(self, card_json['id'], card_json['type'], int(card_json['cost']))
        self.effect = self.__parse_card_effect(card_json)
        self.attack_range, self.effect_value = self.__parse_effect_value(card_json)

    def __parse_card_effect(self, card_json):
        effect = card_json['effect']
        dict = {'水晶': CRYSTAL, '回复': HEAL, '伤害': DAMAGE, '怒气': ANGRY, '减伤': PROTECT, '抽卡': DRAW_CARD}
        return dict[effect]

    def __parse_effect_value(self, card_json):
        short_intro = card_json['shortIntro']
        if self.effect == CRYSTAL:
            return None, int(short_intro[2])
        elif self.effect == HEAL:
            return None, int(short_intro[2])
        elif self.effect == ANGRY:
            return None, int(short_intro[3:5])
        elif self.effect == PROTECT:
            return None, int(short_intro[2])
        elif self.effect == DRAW_CARD:
            return None, int(short_intro[1])
        elif self.effect == DAMAGE:
            return self.__parse_damage_effect(card_json)
        else:
            raise Exception("Wrong Card Type while Parse Effect Value")

    def __parse_damage_effect(self, card_json):
        short_intro = card_json['shortIntro']
        if (short_intro[:2] == '单体'):
            return SINGLE_EFFECT, int(short_intro[2])
        elif (short_intro[:2] == '全体'):
            return GLOBAL_EFFECT, int(short_intro[2])
        elif (short_intro[-2:] == '眩晕'):
            return DIZZY_EFFECT, int(short_intro[0])
        else:
            raise Exception("Wrong Damage Type while Parse Effect Range")


class Cards:
    def __init__(self):
        self.military_cards = {}
        self.skill_cards = {}

    def append_card_via_json(self, card_json):
        card_id = card_json['id']
        if card_json['type'] == MILITARY_CARD:
            if card_id not in self.military_cards.keys():
                self.military_cards[card_id] = MilitaryCard(card_json)
            else:
                raise Exception("Add Same Card To Repository!")
        else:
            if card_id not in self.skill_cards.keys():
                self.skill_cards[card_id] = SkillCard(card_json)
            else:
                raise Exception("Add Same Card To Repository!")

    def append_card(self, card):
        if card.type == MILITARY_CARD:
            if card.sid not in self.military_cards.keys():
                self.military_cards[card.sid] = card
            else:
                raise Exception("Add Same Card To Repository!")
        else:
            if card.sid not in self.skill_cards.keys():
                self.skill_cards[card.sid] = card
            else:
                raise Exception("Add Same Card To Repository!")


class Repository(Cards):
    def __init__(self):
        Cards.__init__(self)

    def search_card(self, card_id):
        if card_id in self.military_cards.keys():
            return self.military_cards[card_id]
        elif card_id in self.skill_cards.keys():
            return self.skill_cards[card_id]
        else:
            raise Exception("No such card found" + str(card_id))


class Deck(Cards):
    def __init__(self):
        Cards.__init__(self)


class Battle:
    def __init__(self, player_hero, enemy_hero):
        self.player_hero = player_hero
        self.enemy_hero = enemy_hero
        self.turn = None
        self.round_count = 0

        self.self_field = [[None, None, None],
                           [None, None, None],
                           [None, None, None]]

        self.enemy_field = [[None, None, None],
                            [None, None, None],
                            [None, None, None]]

    def put_general(self, general, pos, side):
        if side == SELF:
            self_pos = (pos % 10 - 1, 3 - pos // 10)
            if self.self_field[self_pos[0]][self_pos[1]] != None:
                raise Exception("Exist general in " + str(pos))
            else:
                self.self_field[self_pos[0]][self_pos[1]] = general
        else:
            att_pos = (pos % 10 - 1, pos // 10 - 1)
            if self.enemy_field[att_pos[0]][att_pos[1]] != None:
                raise Exception("Exist general in " + str(pos))
            else:
                self.enemy_field[att_pos[0]][att_pos[1]] = general

    def get_pos_info(self, pos, side):
        general = self.get_general(pos, side)
        if general == None:
            return ""
        else:
            return general.cost, general.attack, general.hp

    def get_general(self, pos, side):
        if side == SELF:
            self_pos = (pos % 10 - 1, 3 - pos // 10)
            return self.self_field[self_pos[0]][self_pos[1]]
        else:
            att_pos = (pos % 10 - 1, pos // 10 - 1)
            return self.enemy_field[att_pos[0]][att_pos[1]]


class Hero:
    def __init__(self, player_info):
        self.id = player_info['playerId']
        self.name = player_info['playerName']
        self.max_hp = player_info['domains'][0]['maxhp']
        self.hp = player_info['domains'][0]['hp']

        self.hand_cards = player_info['hand_card']

        self.max_crystal = 0
        self.crystal = 0


class General:
    def __init__(self, general_json):
        self.military_type = general_json['generalType']
        self.cost = general_json['cost']
        self.hp = general_json['hp']
        self.attack = general_json['att']
        self.attack_range = general_json['attRange']
        self.special_attak = general_json['satt']
        self.pos = general_json['pos']
