import sys
import math


class Card:
    def __init__(self, number, inst_id, loc, type, cost, atk, df, ability, mhc, ehc, cd):
        self.card_number = number
        self.instance_id = inst_id
        self.location = loc
        self.card_type = type
        self.cost = cost
        self.attack = atk
        self.defense = df
        self.abilities = ability
        self.my_health_change = mhc
        self.enemy_health_change = ehc
        self.card_draw = cd


# helper methods
def debug(msg):
    print(str(msg), file=sys.stderr)


my_deck = {}

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
# game loop
while True:
    mode = "DRAFT"
    my_mana = 0

    for i in range(2):
        player_health, player_mana, player_deck, player_rune = [int(j) for j in input().split()]
        if player_mana > 0:
            mode = "BATTLE"

        if i == 0:
            my_mana = player_mana

    opponent_hand = int(input())
    card_count = int(input())

    cards = {}

    for i in range(card_count):
        card_number, instance_id, location, card_type, cost, attack, defense, abilities, my_health_change, opponent_health_change, card_draw = input().split()
        card_number = int(card_number)
        instance_id = int(instance_id)
        location = int(location)
        card_type = int(card_type)
        cost = int(cost)
        attack = int(attack)
        defense = int(defense)
        my_health_change = int(my_health_change)
        opponent_health_change = int(opponent_health_change)
        card_draw = int(card_draw)

        # todo: is instance id unique?

        debug("card: num %s, instance_id %s, location %s, card_type %s, cost %s, attack %s, defense %s, my_health_change %s, op_health_change %s, card_draw %s" %
              (card_number, instance_id, location, card_type, cost, attack, defense, my_health_change, opponent_health_change, card_draw))

        cards[len(cards)] = Card(card_number, instance_id, location, card_type, cost, attack, defense, abilities, my_health_change, opponent_health_change, card_draw)

    if mode == "DRAFT":
        debug("draft")

        # pick cheapest card
        lowest_cost = 100
        cheapest_card = 0
        for card_no in cards.keys():
            if cards[card_no].cost < lowest_cost:
                lowest_cost = cards[card_no].cost
                cheapest_card = card_no

        print("PICK %s" % cheapest_card)
    else:
        debug("battle")
        battle_command = ""

        # set target
        target = -1
        for card_no in cards.keys():
            enemy_card = cards[card_no]
            if enemy_card.location != -1:
                continue

            if "G" in enemy_card.abilities:
                target = enemy_card.instance_id

        # play cheapest cards available
        can_play_card = True
        while can_play_card:
            lowest_cost = 100
            cheapest_card = 100
            for card_no in cards.keys():
                card = cards[card_no]
                if card.location != 0:
                    continue

                if cards[card_no].cost < lowest_cost:
                    lowest_cost = cards[card_no].cost
                    cheapest_card = card_no

            if cheapest_card < 100:
                card_to_play = cards[cheapest_card]
                if card_to_play.cost <= my_mana:
                    battle_command += "SUMMON %s;" % card_to_play.instance_id
                    my_mana -= card_to_play.cost
                    cards.pop(cheapest_card, None)
                else:
                    can_play_card = False
            else:
                can_play_card = False

        for card_no in cards.keys():
            card = cards[card_no]
            if card.location != 1:
                continue

            if "G" in card.abilities and target > -1:
                continue

            # todo: re-evaluate target health to determine if it's dead

            battle_command += "ATTACK %s %s;" % (card.instance_id, target)

        if len(battle_command) > 0:
            print(battle_command)
        else:
            print("PASS")
