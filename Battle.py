from Connector import FightServerConnector
from Cards import *

SELF = 0
ENEMY = 1


class Battle:
    def __init__(self, player_id, fight_server_info, transceiver):
        self.fight_server_connector = FightServerConnector(*fight_server_info, transceiver)
        self.battle_info = BattleInfo(player_id)
        self.parser = Parser(self, transceiver)

    def send_ready(self, output=False):
        self.fight_server_connector.send_fight_ready(output=output)
        self.fight_server_connector.wait_both_ready(output=output)

        player_hero_info, enemy_hero_info = self.fight_server_connector.enter_battle(self.battle_info.player_id)
        self.battle_info.player_hero = Hero(player_hero_info)
        self.battle_info.enemy_hero = Hero(enemy_hero_info)

    def round_begin(self, output=False):
        self.parser.parse_frame(output=output)

    def wait_enemy_round(self, output=False):
        self.parser.parse_frame(enemy_round=True, output=output)

    def round_end(self, output=False):
        self.fight_server_connector.send_round_end(output=output)
        self.parser.parse_frame(output=output)

    def self_turn(self):
        return self.battle_info.self_turn()

    def use_policy(self, policies, output=False):
        for policy in policies:
            if policy.card.card_type == GENERAL_CARD:
                if self.battle_info.field.get_general_num() != 5:
                    self.__use_general_card(policy.card, policy.pos, output=output)
                    self.parser.parse_frame(output=output)

            else:
                self.__use_skill_card(policy.card, policy.pos)
                # TODO elf.parser.,....

    def __use_general_card(self, card, pos, output=False):
        self.fight_server_connector.send_cmd("fight@addGeneral", {'id': card.id, 'pos': pos}, output=output)

    def __use_skill_card(self, card, pos, output=False):
        self.fight_server_connector.send_cmd("fight@useSkillCard", {'id': card.id, 'pos': pos}, output=output)


class BattleInfo:
    def __init__(self, player_id):
        self.player_id = player_id
        self.player_hero = None
        self.enemy_hero = None
        self.turn = None
        self.round_count = 0
        self.field = Field()

    def self_turn(self):
        return self.turn == SELF

    def remove_card(self, card_id):
        for pos, card in enumerate(self.player_hero.hand_cards):
            if card.id == card_id:
                del self.player_hero.hand_cards[pos]
                return

        for pos, card in enumerate(self.enemy_hero.hand_cards):
            if card.id == card_id:
                del self.enemy_hero.hand_cards[pos]
                return
        raise Exception("No such card id:" + str(card_id))

    def cause_damage(self, id, damage):
        if id == 1 or id == 2:
            # Direct Damage
            if self.turn == SELF:
                self.enemy_hero.hp -= damage
            else:
                self.player_hero.hp -= damage
        else:
            # General Damage
            general = self.field.find_general(id)
            if general != None:
                general.hp -= damage
            else:
                raise Exception("No Damage Target Found, Target ID:" + str(id))


class Hero:
    def __init__(self, player_info):
        self.id = player_info['playerId']
        self.name = player_info['playerName']
        self.max_hp = player_info['domains'][0]['maxhp']
        self.hp = player_info['domains'][0]['hp']

        self.hand_cards = player_info['hand_card']

        self.max_crystal = 0
        self.crystal = 0


class Field:
    def __init__(self):
        self.field = [[[None, None, None],
                       [None, None, None],
                       [None, None, None]],

                      [[None, None, None],
                       [None, None, None],
                       [None, None, None]]]

    def get_empty_pos(self, self_side_flag=True):
        side = SELF if self_side_flag else ENEMY

        empty_pos = []
        for i in range(3):
            for j in range(3):
                if self.field[side][i][j] == None:
                    empty_pos.append(self.__trans_index_to_pos(side, i, j))
        return empty_pos

    def __trans_index_to_pos(self, side, i, j):
        pos_dict = [[[31, 21, 11],
                     [32, 22, 12],
                     [33, 23, 13]],

                    [[11, 21, 31],
                     [12, 22, 32],
                     [13, 23, 33]]]
        return pos_dict[side][i][j]

    def __trans_pos_to_index(self, side, pos):
        if side == SELF:
            pos = (pos % 10 - 1, 3 - pos // 10)
        else:
            pos = (pos % 10 - 1, pos // 10 - 1)
        return pos

    def put_general(self, general, pos, self_side_flag=True):
        side = SELF if self_side_flag else ENEMY
        index = self.__trans_pos_to_index(side, pos)

        if self.field[side][index[0]][index[1]] != None:
            raise Exception("Exist general in " + str(pos))
        else:
            self.field[side][index[0]][index[1]] = general

    def simulate_attack(self):
        award = 0

        attack_order = [11, 12, 13, 21, 22, 23, 31, 32, 33]
        for pos in attack_order:
            general = self.get_general(pos)
            if general != None:
                award += self.__simulate_general_attack(general, pos)
        return award

    def get_general(self, pos, self_side_flag=True):
        side = SELF if self_side_flag else ENEMY
        index = self.__trans_pos_to_index(side, pos)
        return self.field[side][index[0]][index[1]]

    def get_general_num(self, self_side=True):
        side = SELF if self_side else ENEMY
        general_num = 0
        for i in range(3):
            for j in range(3):
                if self.field[side][i][j] != None:
                    general_num += 1
        return general_num

    def __simulate_general_attack(self, general, pos):
        award = None

        if general.general_type == CHESHI_CARD or general.general_type == JIXIE_CARD \
                or general.general_type == ZHANFA_CARD and general.mp >= 100:
            if general.att_range == SINGLE_ATTAK:
                award = self.__simulate_single_att(general, pos)
            elif general.att_range == HORIZONTAL_ATTAK:
                award = self.__simulate_horizontal_att(general, pos)
            elif general.att_range == VERTICAL_ATTAK:
                award = self.__simulate_vertical_att(general, pos)
            elif general.att_range == GLOBAL_ATTACK:
                award = self.__simulate_global_att(general)
            else:
                raise Exception("General Has Wrong Attack Range!")
        else:
            award = self.__simulate_single_att(general, pos)

        return award

    def __simulate_single_att(self, general, pos):
        award = 0
        index = self.__trans_pos_to_index(SELF, pos)
        for j, enemy_general in enumerate(self.field[ENEMY][index[0]]):
            if enemy_general != None:
                enemy_general.hp -= general.att
                if enemy_general.hp <= 0:
                    award += enemy_general.att + general.att
                else:
                    award += general.att
                return award

        award += 2 * general.att  # Attack Directly
        return award

    def __simulate_horizontal_att(self, general, pos):
        award = 0
        index = self.__trans_pos_to_index(SELF, pos)
        direct_attack = True
        for j, enemy_general in enumerate(self.field[ENEMY][index[0]]):
            if enemy_general != None:
                direct_attack = False
                enemy_general.hp -= general.att
                if enemy_general.hp <= 0:
                    award += enemy_general.att + general.att
                else:
                    award += general.att

        if direct_attack:
            award += 2 * general.att
        return award

    def __simulate_vertical_att(self, general, pos):
        award = 0
        index = self.__trans_pos_to_index(SELF, pos)
        direct_attack = True

        for i in range(3):
            enemy_general = self.field[ENEMY][i][index[1]]
            if enemy_general != None:
                direct_attack = False
                enemy_general.hp -= general.att
                if enemy_general.hp <= 0:
                    award += enemy_general.att + general.att
                else:
                    award += general.att

        if direct_attack:
            award += 2 * general.att
        return award

    def __simulate_global_att(self, general):
        award = 0
        direct_attack = True
        for i in range(3):
            for j in range(3):
                enemy_general = self.field[ENEMY][i][j]
                if enemy_general != None:
                    direct_attack = False
                    enemy_general.hp -= general.att
                    if enemy_general.hp <= 0:
                        award += enemy_general.att + general.att
                    else:
                        award += general.att
        if direct_attack:
            award += 2 * general.att
        return award

    def find_general(self, id):
        for i in range(3):
            for j in range(3):
                general = self.field[SELF][i][j]
                if general != None and general.id == id:
                    return general

                general = self.field[ENEMY][i][j]
                if general != None and general.id == id:
                    return general
        return None

    def remove_dead_general(self):
        for i in range(3):
            for j in range(3):
                general = self.field[SELF][i][j]
                if general != None and general.hp <= 0:
                    self.field[SELF][i][j] = None

                general = self.field[ENEMY][i][j]
                if general != None and general.hp <= 0:
                    self.field[ENEMY][i][j] = None


ATTACK_PROTOCAL = 1
CRYSTAL_PROTOCAL = 2
MILITARY_PROTOCAL = 3
DRAW_CARD_PROTOCAL = 4
SKILL_ATTACK_PROTOCAL = 6
BUFF_PROTOCAL = 8
DAMAGE_PROTOCAL = 9
ROUND_BEGIN_PROTOCAL = 10
USE_SKILL_CARD_PROTOCAL = 11
HAND_CARD_CHANGE_PROTOCAL = 13
ROUND_END_PROTOCAL = 14


class Parser:
    def __init__(self, battle, transceiver):
        self.battle = battle
        self.transceiver = transceiver

    def parse_frame(self, enemy_round=False, output=False):
        frame_json = self.transceiver.recv(output=output)

        for proto_json in frame_json['data']['event']['protos']:
            if enemy_round and proto_json['protoId'] == ROUND_END_PROTOCAL:
                enemy_round = False
            self.__parse_and_refresh(proto_json, output=output)

        if enemy_round:
            self.parse_frame(enemy_round, output=output)

    def __parse_and_refresh(self, proto_json, output=False):
        proto_id = proto_json['protoId']
        if proto_id == ATTACK_PROTOCAL:
            self.__parse_attack_proto(proto_json)
        elif proto_id == CRYSTAL_PROTOCAL:
            self.__parse_crystal_proto(proto_json)
        elif proto_id == MILITARY_PROTOCAL:
            self.__parse_military_proto(proto_json)
        elif proto_id == DRAW_CARD_PROTOCAL:
            self.__parse_draw_card_proto(proto_json)
        elif proto_id == SKILL_ATTACK_PROTOCAL:
            self.__parse_skill_attack_proto(proto_json)
        elif proto_id == BUFF_PROTOCAL:
            pass
        elif proto_id == DAMAGE_PROTOCAL:
            pass
        elif proto_id == ROUND_BEGIN_PROTOCAL:
            self.__parse_round_begin_proto(proto_json)
        elif proto_id == USE_SKILL_CARD_PROTOCAL:
            pass
        elif proto_id == HAND_CARD_CHANGE_PROTOCAL:
            self.__parse_hand_card_change_proto(proto_json, output=output)
        elif proto_id == ROUND_END_PROTOCAL:
            self.battle.fight_server_connector.send_anime_end()
        else:
            raise Exception("No such Protocal" + str(proto_id))

    def __parse_target_proto(self, proto_json, proto_id):
        if proto_json['protoId'] != proto_id:
            raise Exception("Wrong Protocal ID" + str(proto_json['protoId']) + " Received")

        self.__parse_and_refresh(proto_json)

    def __parse_crystal_proto(self, proto_json):
        player_hero = self.battle.battle_info.player_hero
        enemy_hero = self.battle.battle_info.enemy_hero

        if proto_json['playerId'] == player_hero.id:
            player_hero.max_crystal = proto_json['maxToken']
            player_hero.crystal = proto_json['token']
        else:
            enemy_hero.max_crystal = proto_json['maxToken']
            enemy_hero.crystal = proto_json['token']

    def __parse_round_begin_proto(self, proto_json):
        self.battle.battle_info.round_count = proto_json['round']
        if proto_json['playerId'] == self.battle.battle_info.player_hero.id:
            self.battle.battle_info.turn = SELF
        else:
            self.battle.battle_info.turn = ENEMY

    def __parse_hand_card_change_proto(self, proto_json, output=False):
        player_hero = self.battle.battle_info.player_hero
        enemy_hero = self.battle.battle_info.enemy_hero

        if proto_json['playerId'] == player_hero.id:
            draw_card_event_json = self.transceiver.recv(output=output)
            for card_json in draw_card_event_json['data']['event']['protos']:
                self.__parse_target_proto(card_json, DRAW_CARD_PROTOCAL)
        else:
            unknown_card = UnknownCard(proto_json['id'])
            enemy_hero.hand_cards.append(unknown_card)
            # TODO 手牌id变化协议在使用抽牌卡的情况下的行为暂时不知道

    def __parse_draw_card_proto(self, card_json):
        if card_json['cardType'] == GENERAL_CARD:
            card = GeneralCard(card_json)
        else:
            card = SkillCard(card_json)
        self.battle.battle_info.player_hero.hand_cards.append(card)

    def __parse_military_proto(self, proto_json):
        general = GeneralCard(proto_json)
        if proto_json['playerId'] == self.battle.battle_info.player_hero.id:
            self.battle.battle_info.field.put_general(general, proto_json['pos'], self_side_flag=True)
        else:
            self.battle.battle_info.field.put_general(general, proto_json['pos'], self_side_flag=False)
        self.battle.battle_info.remove_card(proto_json['id'])

    def __parse_attack_proto(self, proto_json):
        for target in proto_json['targets']:
            if 'dam' in target:
                self.battle.battle_info.cause_damage(target['id'], target['dam'])
        self.battle.battle_info.field.remove_dead_general()

    def __parse_skill_attack_proto(self, proto_json):
        self.__parse_attack_proto(proto_json)
