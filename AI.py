from Policy import Policy
from Cards import *
import copy


class Agent:
    def __init__(self, battle):
        self.battle = battle

    def attack(self, output=False):
        policies = self.get_policy(output=output)
        print("\nFinal Policy:")
        for policy in policies:
            if policy.card.is_general_card():
                type = " General"
            else:
                type = " Skill"
            print("\tCard ID: " + str(policy.card.id) + type + " Pos: " + str(policy.pos))
        self.battle.use_policy(policies, output=True)

    def get_policy(self, output=False):
        battle_info = copy.deepcopy(self.battle.battle_info)
        policies = []
        n = 1
        while True:
            token = battle_info.player_hero.crystal
            cards = battle_info.player_hero.hand_cards
            possibleCard = self.__select_possible_cards(cards, token)
            if len(possibleCard) == 0:
                break

            policyList = []
            print("Round" + str(n))
            n += 1
            for card in possibleCard:
                print("Card " + str(card.id))
                policy = self.__get_card_use_policy(battle_info, card)
                policyList.append(policy)
            policy = self.__select_best_card_use_policy(policyList)
            print("Best " + str(n) + " Polciy " + str(policy.card.id) + " pos: " + str(policy.pos))
            self.update_battle_info(battle_info, policy)

            policies.append(policy)
        return policies

    def __select_possible_cards(self, cards, tokenNum):
        useable_card = [card for card in cards if card.cost <= tokenNum and card.is_general_card()]
        return useable_card
    def __exist_crystal(self,cards):
        for card in cards:
            if not card.is_general_card() and card.effect_type==CRYSTAL:
                return True
        return False
    def __get_card_use_policy(self, battle_info, card):
        if card.is_general_card():
            policy = self.__evaluate_general_award(battle_info, card)
        else:
            policy = self.__evaluate_skill_award(battle_info, card)
        return policy

    def __evaluate_general_award(self, battle_info, card):
        free_pos = battle_info.field.get_empty_pos(self_side_flag=True)

        best_pos = -1
        best_award = -1
        for pos in free_pos:
            award = self.get_policy_award(battle_info, card, pos)
            print("Testing Card " + str(card.id) + " in pos" + str(pos) + " AWard:" + str(award))
            if award > best_award:
                best_pos = pos
                best_award = award

        return Policy(card, best_pos, best_award)

    def __evaluate_skill_award(self, battle_info, card):
        pass
    def __select_best_card_use_policy(self, policies):
        sorted_policy = sorted(policies, key=lambda x: x.award, reverse=True)
        return sorted_policy[0]

    def get_policy_award(self, battle_info, card, pos):
        battle_info_1 = copy.deepcopy(battle_info)
        global_award1 = battle_info_1.field.simulate_attack()

        battle_info_2 = copy.deepcopy(battle_info)
        battle_info_2.field.put_general(card, pos,self_side_flag=True)
        global_award2 = battle_info_2.field.simulate_attack()

        card_award = global_award2 - global_award1
        if card_award < 0:
            raise Exception("Card Award less than 0")
        return card_award / card.cost

    def update_battle_info(self, battle_info, policy):
        if policy.card.is_general_card():
            battle_info.field.put_general(policy.card, policy.pos)
            battle_info.field.simulate_attack()
            battle_info.field.remove_dead_general()
            battle_info.player_hero.crystal -= policy.card.cost
            battle_info.remove_card(policy.card.id)
