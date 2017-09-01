from Transceiver import *
from Cards import *
from urllib import parse, request


class GatewayConnector():
    def __init__(self):
        self.login_prefix = "http://proxytest.aszb.aoshitang.com/root/gateway.action?command=%s&%s"
        self.login_suffix = "userName=%s&password=%s&channelId=%s"
        self.gateway_info = None

        self.transceiver = Transceiver()

    def login(self, username, passwd):
        login_response = self.__send_login_request(username, passwd)
        return self.__connect_gateway(login_response), self.transceiver

    def __send_login_request(self, username, passwd):
        filled_login_suffix = self.login_suffix % (username, passwd, 'ios_dl')
        login_url = self.login_prefix % ("user@login", filled_login_suffix)
        login_params = parse.urlencode({'username': username, 'password': passwd, 'remember': 'false'})

        # Send login Request
        req = request.Request(login_url, login_params.encode('utf-8'))
        resp_json = request.urlopen(req)
        return resp_json

    def __connect_gateway(self, login_resp_json):
        content = login_resp_json.read().decode('utf-8')
        jsonObj = json.loads(content)
        self.gateway_info = jsonObj['data']['gateway']
        self.transceiver.socket_connect(self.gateway_info)
        self.send_cmd("reconnect", {"sessionId": self.gateway_info['sessionId']})

        game_server_info = jsonObj['data']['gameServer']
        return game_server_info['serverType'], game_server_info['serverId']

    def send_cmd(self, cmd, params, output=False):
        resp_json = self.transceiver.send_cmd_server(self.gateway_info['serverType'],
                                                     self.gateway_info['serverId'], cmd, params, output=output)
        return resp_json


class ServerConnector:
    def __init__(self, server_type, server_id, transceiver):
        self.server_type = server_type
        self.server_id = server_id
        self.transceiver = transceiver

    def send_cmd(self, cmd, params={}, output=False):
        resp_json = self.transceiver.send_cmd_server(self.server_type, self.server_id, cmd, params, output=output)
        return resp_json

    def recv(self, output=False):
        return self.transceiver.recv_protos(output)


class GameServerConnector(ServerConnector):
    def __init__(self, server_type, server_id, transceiver):
        ServerConnector.__init__(self, server_type, server_id, transceiver)

    def get_player_info(self, output=False):
        json_obj = self.send_cmd("player@getPlayerList", output=output)

        # If receive update protocal, receive again
        if 'update' in json_obj['data']:
            json_obj = self.transceiver.recv(output=output)

        player_id = json_obj['data']['playerList'][0]['playerId']
        player_name = json_obj['data']['playerList'][0]['playerName']
        player_level = json_obj['data']['playerList'][0]['playerLv']
        player_info = {"player_id": player_id, "player_name": player_name, "player_level": player_level}
        return player_info

    def match_player(self, output=False):
        self.send_cmd("fight@signup", output=output)
        match_result_json = self.transceiver.recv(output=output)

        fight_server_info = match_result_json['data']['schedule']
        return fight_server_info['serverType'], fight_server_info['serverId']


class FightServerConnector(ServerConnector):
    def __init__(self, server_type, server_id, transceiver):
        ServerConnector.__init__(self, server_type, server_id, transceiver)

    def send_fight_ready(self, output=False):
        self.send_cmd("fight@ready", output=output)

    def wait_both_ready(self, output=False):
        self.transceiver.recv(output=output)

    def enter_battle(self, user_id, output=False):
        enter_battle_json = self.send_cmd("fight@enterBattle", output=output)
        player_hero_info, enemy_hero_info = self.__parse_battle_json(enter_battle_json, user_id, output=output)
        return player_hero_info, enemy_hero_info

    def __parse_battle_json(self, enter_battle_json, user_id, output=False):
        player_hero_info, enemy_hero_info = self.__parse_hero_info(enter_battle_json, user_id)
        self_hand_card, enemy_hand_card = self.__parse_hand_card(enter_battle_json, user_id)

        player_hero_info['hand_card'] = self_hand_card
        enemy_hero_info['hand_card'] = enemy_hand_card

        if len(self_hand_card) == 3:
            print("先手方", len(self_hand_card))
        else:
            print("后手方", len(self_hand_card))

        return player_hero_info, enemy_hero_info

    def __parse_hero_info(self, enter_battle_json, user_id):
        if 'attTeam' in enter_battle_json['data']:
            attTeam_info = enter_battle_json['data']['attTeam']
            defTeam_info = enter_battle_json['data']['defTeam']
            if attTeam_info['playerId'] == user_id:
                player_hero_info = attTeam_info
                enemy_hero_info = defTeam_info
            else:
                player_hero_info = defTeam_info
                enemy_hero_info = attTeam_info
            return player_hero_info, enemy_hero_info
        else:
            raise Exception("Exception While Entering Battle!")

    def __parse_hand_card(self, enter_battle_json, user_id):
        self_hand_card = []
        for card_json in enter_battle_json['data']['grids']:
            if card_json['cardType'] == GENERAL_CARD:
                card = GeneralCard(card_json)
            else:
                card = SkillCard(card_json)
            self_hand_card.append(card)

        enemy_hand_card = []
        if enter_battle_json['data']['attTeam']['playerId'] == user_id:
            for card_id in enter_battle_json['data']['defTeam']['chooseGrids']:
                unknown_card = UnknownCard(card_id)
                enemy_hand_card.append(unknown_card)
        else:
            for card_id in enter_battle_json['data']['attTeam']['chooseGrids']:
                unknown_card = UnknownCard(card_id)
                enemy_hand_card.append(unknown_card)
        return self_hand_card, enemy_hand_card

    def send_round_end(self, output=False):
        self.send_cmd("fight@endRound", output=output)

    def send_anime_end(self, output=False):
        self.send_cmd("fight@mark", output=output)
