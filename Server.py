from Battle import *
from Transceiver import *
from urllib import parse, request


class ServerConnector:
    def __init__(self, server_type, server_id, transceiver):
        self.server_type = server_type
        self.server_id = server_id
        self.transceiver = transceiver

    def send_cmd(self, cmd, params={}, output=False):
        resp_json = self.transceiver.send_cmd_server(self.server_type, self.server_id, cmd, params, output=output)
        return resp_json


class LoginServerConnector():
    def __init__(self,username,passwd):
        self.login_prefix = "http://proxytest.aszb.aoshitang.com/root/gateway.action?command=%s&%s"
        self.login_suffix = "userName=%s&password=%s&channelId=%s"
        self.gateway_info = None

        self.username=username
        self.passwd=passwd
        self.transceiver = Transceiver()

    def login(self):
        login_response = self.__send_login_request(self.username, self.passwd)
        return self.__connect_gateway(login_response)

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

        game_server_info=jsonObj['data']['gameServer']
        return game_server_info['serverType'],game_server_info['serverId']

    def send_cmd(self, cmd, params, output=False):
        resp_json = self.transceiver.send_cmd_server(self.gateway_info['serverType'],
                                                     self.gateway_info['serverId'], cmd, params, output=output)
        return resp_json


class GameServerConnector(ServerConnector):
    def __init__(self, server_type, server_id, transceiver):
        ServerConnector.__init__(self, server_type, server_id, transceiver)

    def get_player_info(self, output=False):
        json_obj = self.send_cmd("player@getPlayerList", output=output)

        player_id = json_obj['data']['playerList'][0]['playerId']
        player_name = json_obj['data']['playerList'][0]['playerName']
        player_level = json_obj['data']['playerList'][0]['playerLv']
        player_info = {"player_id": player_id, "player_name": player_name, "player_level": player_level}
        return player_info

    def get_card_info(self, output=False):
        json_obj = self.send_cmd("formation@getInfo", output=output)

        repository = self.__parse_card_repository(json_obj)
        deck = self.__parse_deck(json_obj, repository)

        return repository, deck

    def __parse_card_repository(self, json_obj):
        repository = Repository()
        for card_json in json_obj['data']['cards']:
            repository.append_card_via_json(card_json)

        return repository

    def __parse_deck(self, json_obj, repository):
        defaultCards = self.__get_default_deck_json(json_obj)

        deck = Deck()
        for card_json in defaultCards:
            card = repository.search_card(card_json['id'])
            deck.append_card(card)

        return deck

    def __get_default_deck_json(self, jsonObj):
        for group in jsonObj['data']['myCards']:
            if group['isDefault']:
                return group['cards']

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

    def enter_battle(self, user_id, repository, output=False):
        enter_battle_json = self.send_cmd("fight@enterBattle", output=output)
        battle = self.__parse_battle_json(enter_battle_json, user_id, repository, output=output)
        return battle

    def __parse_battle_json(self, enter_battle_json, user_id, repository, output=False):
        player_hero_info, enemy_hero_info, begin_turn = self.__parse_hero_info(enter_battle_json, user_id)
        self_hand_card, enemy_hand_card = self.__parse_hand_card(enter_battle_json, user_id, repository)

        player_hero_info['hand_card'] = self_hand_card
        enemy_hero_info['hand_card'] = enemy_hand_card
        player_hero = Hero(player_hero_info)
        enemy_hero = Hero(enemy_hero_info)
        battle = Battle(player_hero, enemy_hero)

        if len(self_hand_card) == 3:
            print("先手方", len(self_hand_card))
        else:
            print("后手方", len(self_hand_card))

        return battle

    def __parse_hero_info(self, enter_battle_json, user_id):
        player_hero_info = {}
        enemy_hero_info = {}
        begin_turn = None

        if 'attTeam' in enter_battle_json['data']:
            attTeam_info = enter_battle_json['data']['attTeam']
            defTeam_info = enter_battle_json['data']['defTeam']
            if attTeam_info['playerId'] == user_id:
                begin_turn = SELF
                player_hero_info = attTeam_info
                enemy_hero_info = defTeam_info
            else:
                begin_turn = SELF
                player_hero_info = defTeam_info
                enemy_hero_info = attTeam_info
        else:
            raise Exception("Exception While Entering Battle!")

        return player_hero_info, enemy_hero_info, begin_turn

    def __parse_hand_card(self, enter_battle_json, user_id, repository):
        self_hand_card = []
        for card_json in enter_battle_json['data']['grids']:
            card = repository.search_card(card_json['sid'])
            card.id=card_json['id']
            self_hand_card.append(card)

        enemy_hand_card = []
        if enter_battle_json['data']['attTeam']['playerId'] == user_id:
            for i in range(4):
                unknown_card = Card(-1, -1, -1)
                enemy_hand_card.append(unknown_card)
            crystal_card = repository.search_card(10001)
            enemy_hand_card.append(crystal_card)
        else:
            for i in range(3):
                unknown_card = Card(-1, -1, -1)
                enemy_hand_card.append(unknown_card)

        return self_hand_card, enemy_hand_card

    def send_round_end(self, output=False):
        self.send_cmd("fight@endRound", output=output)
