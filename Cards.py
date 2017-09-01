# Card Type
GENERAL_CARD = 1
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


class Card:
    def __init__(self, card_json):
        self.id = card_json['id']
        self.sid = card_json['sid']
        self.name = card_json['name']
        self.card_type = card_json['cardType']
        self.cost = card_json['cost']
        self.target_side = card_json['targetSide']

    def is_general_card(self):
        return self.card_type == GENERAL_CARD


class UnknownCard():
    def __init__(self, id):
        self.id = id


class GeneralCard(Card):
    def __init__(self, card_json):
        Card.__init__(self, card_json)
        self.att = card_json['att']
        self.att_range = card_json['attRange']
        self.satt = card_json['satt']
        self.hp = card_json['hp']
        self.max_hp = card_json['maxhp']
        self.general_type = card_json['generalType']
        self.crip = card_json['crip']
        self.mp = card_json['mp']


class SkillCard(Card):
    def __init__(self, card_json):
        Card.__init__(self, card_json)
        self.target_type = card_json['targetType']
        self.effect_type = self.__parse_card_effect(card_json)
        self.attack_range, self.effect_value = self.__parse_effect_value(card_json)

    def __parse_card_effect(self, card_json):
        effect = card_json['effectStr']
        dict = {'水晶': CRYSTAL, '回复': HEAL, '伤害': DAMAGE, '怒气': ANGRY, '减伤': PROTECT, '抽卡': DRAW_CARD}
        return dict[effect]

    def __parse_effect_value(self, card_json):
        short_intro = card_json['shortIntro']
        if self.effect_type == CRYSTAL:
            return None, int(short_intro[2])
        elif self.effect_type == HEAL:
            return None, int(short_intro[2])
        elif self.effect_type == ANGRY:
            return None, int(short_intro[3:5])
        elif self.effect_type == PROTECT:
            return None, int(short_intro[2])
        elif self.effect_type == DRAW_CARD:
            return None, int(short_intro[1])
        elif self.effect_type == DAMAGE:
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
