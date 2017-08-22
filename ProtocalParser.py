from Battle import *
from Card import *

ATTACK_PROTOCAL = 1
CRYSTAL_PROTOCAL = 2
MILIRTARY_PROTOCAL = 3
DRAW_CARD_PROTOCAL = 4
SKILL_ATTACK_PROTOCAL = 6
BUFF_PROTOCAL = 8
DAMAGE_PROTOCAL = 9
ROUND_BEGIN_PROTOCAL = 10
USE_SKILL_CARD_PROTOCAL = 11
HAND_CARD_CHANGE_PROTOCAL = 13
ROUND_END_PROTOCAL = 14


class PushInfoListener:
    def __init__(self, battle, client,repository):
        self.battle = battle
        self.client = client
        self.repository=repository

    def parse_frame(self, output=False):
        frame_json = self.client.recv(output=output)

        for proto_json in frame_json['data']['event']['protos']:
            self.__parse_and_refresh(proto_json,output=output)

    def __parse_and_refresh(self, proto_json,output=False):
        proto_id = proto_json['protoId']
        if proto_id == ATTACK_PROTOCAL:
            pass
        elif proto_id == CRYSTAL_PROTOCAL:
            self.__parse_crystal_proto(proto_json)
        elif proto_id == MILIRTARY_PROTOCAL:
            pass
        elif proto_id == DRAW_CARD_PROTOCAL:
            self.__parse_draw_card_proto(proto_json)
        elif proto_id == SKILL_ATTACK_PROTOCAL:
            pass
        elif proto_id == BUFF_PROTOCAL:
            pass
        elif proto_id == DAMAGE_PROTOCAL:
            pass
        elif proto_id == ROUND_BEGIN_PROTOCAL:
            self.__parse_round_begin_proto(proto_json)
        elif proto_id == USE_SKILL_CARD_PROTOCAL:
            pass
        elif proto_id == HAND_CARD_CHANGE_PROTOCAL:
            self.__parse_hand_card_change_proto(proto_json,output=output)
        elif proto_id == ROUND_END_PROTOCAL:
            pass
        else:
            raise Exception("No such Protocal" + str(proto_id))

    def __parse_target_proto(self, proto_json, proto_id):
        if proto_json['protoId'] != proto_id:
            raise Exception("Wrong Protocal ID" + str(proto_json['protoId']) + " Received")

        self.__parse_and_refresh(proto_json)

    def __parse_crystal_proto(self, proto_json):
        player_hero = self.battle.player_hero
        enemy_hero = self.battle.enemy_hero

        if proto_json['playerId'] == player_hero.id:
            player_hero.max_crystal = proto_json['maxToken']
            player_hero.crystal = proto_json['token']
        else:
            enemy_hero.max_crystal = proto_json['maxToken']
            enemy_hero.crystal = proto_json['token']

    def __parse_round_begin_proto(self, proto_json):
        self.battle.round_count =proto_json['round']
        if proto_json['playerId']==self.battle.player_hero.id:
            self.battle.turn=SELF_TURN
        else:
            self.battle.turn=ENEMY_TURN

    def __parse_hand_card_change_proto(self, proto_json,output=False):
        player_hero = self.battle.player_hero
        enemy_hero = self.battle.enemy_hero

        if proto_json['playerId'] == player_hero.id:
            draw_card_event_json=self.client.recv(output=output)
            for card_json in draw_card_event_json['data']['event']['protos']:
               self.__parse_target_proto(card_json,DRAW_CARD_PROTOCAL)
        else:
            unknown_card=Card(-1,-1,-1)
            enemy_hero.hand_cards.append(unknown_card)
        #TODO 手牌id变化协议在使用抽牌卡的情况下的行为暂时不知道

    def __parse_draw_card_proto(self,proto_json):
        card = self.repository.search_card(proto_json['sid'])
        self.battle.player_hero.hand_cards.append(card)