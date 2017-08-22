from FunctionLayer import *

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
        self.match_battle = None
        self.function_layer = FunctionLayer()
    def login(self):
        self.function_layer.login(self.username, self.passwd)

        player_info = self.function_layer.get_player_info(output=True)
        self.id = player_info["player_id"]
        self.name = player_info["player_name"]
        self.level = player_info["player_level"]

        self.repository, self.deck = self.function_layer.get_card_info()

    def start_match_fight(self, output=False):
        self.function_layer.match_player(output=output)
        self.function_layer.send_fight_ready(output=output)
        self.function_layer.wait_both_ready(output=output)
        self.match_battle = self.function_layer.enter_battle(self.id, self.repository, output=output)

        self.push_info_listener=PushInfoListener(self.match_battle, self.function_layer.client, self.repository)

    def round_begin(self,output=False):
        self.push_info_listener.parse_frame(output=output)

    def round_end(self,output=False):
        # Attack side need send ROUND_END command first
        if self.match_battle.turn==SELF_TURN:
            self.function_layer.send_round_end(output=output)

        # RECV ROUND_END_PROTOCAL
        self.push_info_listener.parse_frame(output=output)

    def user_card(self):
        pass
