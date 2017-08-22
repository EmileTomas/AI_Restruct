SELF_TURN=1
ENEMY_TURN=2

class Battle:
    def __init__(self,player_hero,enemy_hero):
        self.player_hero=player_hero
        self.enemy_hero=enemy_hero
        self.turn=None
        self.round_count=0



class Hero:
    def __init__(self,player_info):
        self.id=player_info['playerId']
        self.name = player_info['playerName']
        self.max_hp = player_info['domains'][0]['maxhp']
        self.hp=player_info['domains'][0]['hp']

        self.hand_cards = player_info['hand_card']

        self.max_crystal=0
        self.crystal=0
