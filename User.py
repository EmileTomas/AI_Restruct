from Client import Client
from Printer import Printer
from AI import Agent
printer = Printer()

class User:
    def __init__(self, username, passwd):
        self.username = username
        self.passwd = passwd
        self.client = Client()
        self.AI=None

    def login(self):
        printer.print_title("Login And Match")
        self.client.login(self.username, self.passwd)

    def start_match(self, output=False):
        printer.print_title("Start Match")
        self.client.start_match_fight(output=output)

    def round_begin(self, output=False):
        printer.print_title("Round Begin")
        self.client.round_begin(output=output)
        printer.print_battle(self.client.battle.battle_info)

        self.AI=Agent(self.client.battle)

    def wait_or_attack(self,output=False):
        if self.client.battle.self_turn():
            printer.print_title("Attack")
            self.attack(output=output)
            printer.print_title("Round End")
            self.client.round_end(output=output)
        else:
            printer.print_title("Wait Enemy Round")
            self.client.wait_enemy_round(output=output)
            printer.print_title("Round End")


    def attack(self,output=False):
        self.AI.attack()

    def battle_over(self):
        return self.client.battle_over()

    def show_result(self):
        if self.client.battle.battle_info.player_hero.hp<=0:
            print("You Lose")
        else:
            print("You Win")

    def write_result(self):
        if self.client.battle.battle_info.player_hero.hp > 0:
            f = open("Result.txt", 'r')
            win = int(f.read())
            f.close()
            f=open("Result.txt", 'w')
            f.write(str(win+1))
            f.close()