from Server import *
from ProtocalParser import *



class User:
    def __init__(self, username, passwd):
        self.username = username
        self.passwd = passwd

        self.id = None
        self.name = None
        self.level = None
        self.repository = None
        self.deck = None

        self.battle = None

        self.transceiver=None
        self.game_server_connector=None
        self.fight_server_connector=None

        self.login_server_connector=LoginServerConnector(username,passwd)

    def login(self):
        game_server_info = self.login_server_connector.login()
        self.transceiver=self.login_server_connector.transceiver

        self.game_server_connector=GameServerConnector(*game_server_info,self.transceiver)
        self.__obtain_player_info()

    def __obtain_player_info(self):
        player_info = self.game_server_connector.get_player_info(output=True)
        self.id = player_info["player_id"]
        self.name = player_info["player_name"]
        self.level = player_info["player_level"]
        self.repository, self.deck = self.game_server_connector.get_card_info()

    def start_match_fight(self, output=False):
        fight_server_info=self.game_server_connector.match_player(output=output)
        self.fight_server_connector=FightServerConnector(*fight_server_info,self.transceiver)

        self.fight_server_connector.send_fight_ready(output=output)
        self.fight_server_connector.wait_both_ready(output=output)
        self.battle = self.fight_server_connector.enter_battle(self.id, self.repository, output=output)

        self.push_info_listener=PushInfoListener(self.battle, self.repository,self.transceiver)

    def round_begin(self,output=False):
        self.push_info_listener.parse_frame(output=output)

    def round_end(self,output=False):
        # Attack side need send ROUND_END command first
        if self.battle.turn==SELF_TURN:
            self.fight_server_connector.send_round_end(output=output)

        # RECV ROUND_END_PROTOCAL
        self.push_info_listener.parse_frame(output=output)

    def user_card(self):
        pass
