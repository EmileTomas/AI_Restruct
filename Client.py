from Connector import *
from Battle import Battle


class Client():
    def __init__(self):
        self.id = None
        self.name = None
        self.level = None

        self.login_connector = GatewayConnector()
        self.game_server_connector = None
        self.battle = None
        self.transceiver = None

    def login(self, username, passwd):
        game_server_info, self.transceiver = self.login_connector.login(username, passwd)

        self.game_server_connector = GameServerConnector(*game_server_info, self.transceiver)
        player_info = self.game_server_connector.get_player_info(output=True)
        self.id = player_info["player_id"]
        self.name = player_info["player_name"]
        self.level = player_info["player_level"]

    def start_match_fight(self, output=False):
        fight_server_info = self.game_server_connector.match_player(output=output)
        self.battle = Battle(self.id, fight_server_info, self.transceiver)
        self.battle.send_ready(output)

    def round_begin(self, output=False):
        self.battle.round_begin(output=output)

    def wait_enemy_round(self,output=False):
        self.battle.wait_enemy_round(output=output)

    def round_end(self,output=False):
        self.battle.round_end(output=output)

    def battle_over(self):
        battle_info=self.battle.battle_info
        if battle_info.player_hero.hp<=0 or battle_info.enemy_hero.hp<=0:
            return True
        else:
            return False
