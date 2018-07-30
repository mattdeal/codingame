import sys


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

    def will_kill(self, other_card):
        if "W" in other_card.abilities:
            return False
        if "L" in self.abilities:
            return True
        if self.attack > other_card.defense:
            return True

    def will_be_killed(self, other_card):
        return other_card.will_kill(self)


# helper methods
def debug(msg):
    print(str(msg), file=sys.stderr)


# https://docs.google.com/spreadsheets/d/1G_2qWMMrF7H-S3kHu_V4FmSgPHEpbMro-7r8MDU0Ewc/edit#gid=2138550420

# v2 seems to prioritize defense
# card_rank = {1: 48, 2: 27, 3: 21, 4: 5, 5: 81, 6: 51, 7: 62, 8: 30, 9: 31, 10: 121, 11: 83, 12: 17, 13: 95, 14: 108,
#              15: 32, 16: 110, 17: 33, 18: 26, 19: 36, 20: 123, 21: 60, 22: 97, 23: 24, 24: 68, 25: 91, 26: 49, 27: 70,
#              28: 85, 29: 101, 30: 93, 31: 124, 32: 102, 33: 104, 34: 100, 35: 148, 36: 140, 37: 47, 38: 8, 39: 40,
#              40: 76, 41: 106, 42: 122, 43: 115, 44: 77, 45: 87, 46: 141, 47: 3, 48: 65, 49: 79, 50: 103, 51: 43, 52: 98,
#              53: 151, 54: 114, 55: 6, 56: 9, 57: 4, 58: 71, 59: 82, 60: 89, 61: 29, 62: 59, 63: 18, 64: 105, 65: 61,
#              66: 150, 67: 112, 68: 94, 69: 11, 70: 57, 71: 119, 72: 74, 73: 44, 74: 88, 75: 34, 76: 96, 77: 52, 78: 147,
#              79: 54, 80: 46, 81: 146, 82: 125, 83: 15, 84: 99, 85: 84, 86: 22, 87: 50, 88: 113, 89: 155, 90: 154,
#              91: 23, 92: 78, 93: 42, 94: 13, 95: 25, 96: 45, 97: 67, 98: 38, 99: 14, 100: 7, 101: 86, 102: 111, 103: 16,
#              104: 69, 105: 41, 106: 72, 107: 137, 108: 80, 109: 35, 110: 10, 111: 73, 112: 64, 113: 144, 114: 75,
#              115: 153, 116: 157, 117: 39, 118: 2, 119: 28, 120: 129, 121: 58, 122: 37, 123: 109, 124: 126, 125: 63,
#              126: 90, 127: 12, 128: 107, 129: 66, 130: 53, 131: 143, 132: 127, 133: 158, 134: 138, 135: 117, 136: 20,
#              137: 131, 138: 130, 139: 159, 140: 132, 141: 19, 142: 55, 143: 56, 144: 92, 145: 116, 146: 139, 147: 128,
#              148: 120, 149: 149, 150: 118, 151: 1, 152: 160, 153: 136, 154: 134, 155: 142, 156: 152, 157: 145, 158: 133,
#              159: 156, 160: 135}

# v3 prioritize G ability
card_rank = {1: 151, 2: 118, 3: 47, 4: 57, 5: 4, 6: 55, 7: 100, 8: 38, 9: 110, 10: 56, 11: 69, 12: 94, 13: 99, 14: 103,
             15: 127, 16: 63, 17: 83, 18: 12, 19: 141, 20: 136, 21: 3, 22: 91, 23: 86, 24: 95, 25: 23, 26: 18, 27: 2,
             28: 119, 29: 61, 30: 8, 31: 9, 32: 15, 33: 17, 34: 122, 35: 75, 36: 109, 37: 19, 38: 98, 39: 105, 40: 93,
             41: 96, 42: 117, 43: 80, 44: 39, 45: 51, 46: 73, 47: 87, 48: 37, 49: 1, 50: 26, 51: 6, 52: 62, 53: 77,
             54: 130, 55: 79, 56: 142, 57: 143, 58: 70, 59: 112, 60: 121, 61: 21, 62: 97, 63: 104, 64: 65, 65: 7,
             66: 125, 67: 106, 68: 48, 69: 129, 70: 111, 71: 24, 72: 114, 73: 40, 74: 27, 75: 58, 76: 92, 77: 49,
             78: 108, 79: 72, 80: 44, 81: 5, 82: 101, 83: 59, 84: 74, 85: 11, 86: 85, 87: 28, 88: 45, 89: 60, 90: 126,
             91: 25, 92: 144, 93: 30, 94: 68, 95: 13, 96: 76, 97: 22, 98: 52, 99: 84, 100: 34, 101: 64, 102: 29,
             103: 32, 104: 50, 105: 33, 106: 41, 107: 128, 108: 14, 109: 102, 110: 123, 111: 16, 112: 67, 113: 88,
             114: 54, 115: 43, 116: 145, 117: 135, 118: 150, 119: 71, 120: 148, 121: 10, 122: 42, 123: 20, 124: 31,
             125: 82, 126: 124, 127: 132, 128: 147, 129: 120, 130: 138, 131: 137, 132: 107, 133: 140, 134: 158,
             135: 154, 136: 160, 137: 153, 138: 134, 139: 146, 140: 36, 141: 46, 142: 155, 143: 131, 144: 113, 145: 157,
             146: 81, 147: 78, 148: 35, 149: 149, 150: 66, 151: 115, 152: 53, 153: 156, 154: 90, 155: 89, 156: 159,
             157: 116, 158: 133, 159: 139, 160: 152}

my_deck = {}

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
# game loop
while True:
    mode = "DRAFT"
    my_mana = 0

    for i in range(2):
        player_health, player_mana, player_deck, player_rune = [int(j) for j in input().split()]

        # detect my mana
        if i == 0:
            my_mana = player_mana

            # detect mode
            if player_mana > 0:
                mode = "BATTLE"

        # todo: runes?  ignore for now
        # todo: deck?

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

        debug(
            "card: num %s, instance_id %s, location %s, card_type %s, cost %s, attack %s, defense %s, my_health_change %s, op_health_change %s, card_draw %s" %
            (card_number, instance_id, location, card_type, cost, attack, defense, my_health_change,
             opponent_health_change, card_draw))

        cards[len(cards)] = Card(card_number, instance_id, location, card_type, cost, attack, defense, abilities,
                                 my_health_change, opponent_health_change, card_draw)

    if mode == "DRAFT":
        debug("draft")

        # pick best value card
        best_value = -100
        best_card = 0
        for card_no in cards.keys():
            test_card = cards[card_no]

            # todo: remove this once the bot can use items correctly, temp fix to not select items
            if test_card.card_type > 0:
                continue

            if card_rank[test_card.card_number] > best_value:
                best_card = card_no
                best_value = card_rank[test_card.card_number]

        print("PICK %s" % best_card)
    else:
        debug("battle")
        battle_command = ""
        enemy_g = {}
        num_enemy_creatures = 0
        num_my_creatures = 0
        num_my_g = 0
        summoned_cards = {}

        # todo: check for enemy D (after G is killed)

        # check enemy board
        target = -1
        for card_no in cards.keys():
            enemy_card = cards[card_no]
            if enemy_card.location != -1:
                continue

            if "G" in enemy_card.abilities:
                target = enemy_card.instance_id
                enemy_g[enemy_card.instance_id] = enemy_card

            num_enemy_creatures += 1

        # check my board
        for card_no in cards.keys():
            my_card = cards[card_no]
            if my_card.location != 1:
                continue

            if "G" in my_card.abilities:
                num_my_g += 1

            num_my_creatures += 1

        # play G creature if opp has creatures
        if num_enemy_creatures > 0 and num_my_g < 1:
            g_to_play = {}
            for card_no in cards.keys():
                my_card = cards[card_no]
                if my_card.location > 0:
                    continue

                if my_card.card_type > 0:
                    continue

                if "G" in my_card.abilities:
                    if my_card.cost not in g_to_play.keys():
                        g_to_play[my_card.cost] = my_card
                    else:
                        g_to_play[my_card.cost + .1] = my_card

            if len(g_to_play) > 0:
                g_card = g_to_play[min(g_to_play.keys())]
                if g_card.cost <= my_mana:
                    battle_command += "SUMMON %s;" % g_card.instance_id
                    summoned_cards[g_card.instance_id] = "Needed G on board"
                    my_mana -= g_card.cost
                    num_my_creatures += 1

        # todo: play item that grants G to my creature
        if num_enemy_creatures > 0 and num_my_g < 1:
            debug("todo: look for items to grant G to a creature")

        # todo: cheap creature and item that grants G to cheap creature
        if num_enemy_creatures > 0 and num_my_g < 1:
            debug("todo: look for cheap creature and item to grant G to cheap creature")

        if target > -1:
            debug("G")
            enemy_g_remaining = len(enemy_g)

            # find cards that can kill enemy G safely
            for enemy_card in enemy_g.values():
                for card_no in cards.keys():
                    my_card = cards[card_no]
                    if my_card.location != 1:
                        continue

                    if my_card.card_type > 0:
                        continue

                    if my_card.attack < 1:
                        continue

                    if my_card.will_kill(enemy_card) and not my_card.will_be_killed(enemy_card):
                        if str(my_card.instance_id) not in battle_command:
                            battle_command += "ATTACK %s %s;" % (my_card.instance_id, enemy_card.instance_id)
                            enemy_g_remaining -= 1

            # todo: find items that can kill enemy G
            if enemy_g_remaining > 0:
                debug("todo: look for items")

            # find cards that will kill enemy G with trade
            if enemy_g_remaining > 0:
                for enemy_card in enemy_g.values():
                    for card_no in cards.keys():
                        my_card = cards[card_no]
                        if my_card.location != 1:
                            continue

                        if my_card.card_type > 0:
                            continue

                        if my_card.attack < 1:
                            continue

                        if my_card.will_kill(enemy_card):
                            if str(my_card.instance_id) not in battle_command:
                                battle_command += "ATTACK %s %s;" % (my_card.instance_id, enemy_card.instance_id)
                                enemy_g_remaining -= 1
                                num_my_creatures -= 1

            # find cards that will damage enemy G
            # sacrifice to kill G mod
            if enemy_g_remaining > 0:
                for enemy_card in enemy_g.values():
                    for card_no in cards.keys():
                        my_card = cards[card_no]
                        if my_card.location != 1:
                            continue

                        if my_card.card_type > 0:
                            continue

                        if my_card.attack < 1:
                            continue

                        if my_card.will_kill(enemy_card):
                            if str(my_card.instance_id) not in battle_command:
                                battle_command += "ATTACK %s %s;" % (my_card.instance_id, enemy_card.instance_id)
                                enemy_g_remaining -= 1
                                num_my_creatures -= 1
                        else:
                            if str(my_card.instance_id) not in battle_command:
                                battle_command += "ATTACK %s %s;" % (my_card.instance_id, enemy_card.instance_id)
                                enemy_card.defense -= my_card.attack
                                num_my_creatures -= 1

            # summon more creatures
            if num_my_creatures < 6:
                debug("look for creatures")
                # play cheapest cards available
                can_play_card = True
                while can_play_card:
                    lowest_cost = 100
                    cheapest_card = 100
                    for card_no in cards.keys():
                        card = cards[card_no]
                        if card.location != 0:
                            continue

                        if card.card_type > 0:
                            continue

                        if cards[card_no].cost < lowest_cost:
                            lowest_cost = cards[card_no].cost
                            cheapest_card = card_no

                    if cheapest_card < 100:
                        card_to_play = cards[cheapest_card]
                        if card_to_play.cost <= my_mana:
                            battle_command += "SUMMON %s;" % card_to_play.instance_id
                            num_my_creatures += 1
                            my_mana -= card_to_play.cost
                            cards.pop(cheapest_card, None)
                        else:
                            can_play_card = False
                    else:
                        can_play_card = False

                    if num_my_creatures > 5:
                        can_play_card = False

            # todo: look for items to play
        else:
            debug("Attack opp")
            # summon more creatures
            if num_my_creatures < 6:
                debug("look for creatures")
                # play cheapest cards available
                can_play_card = True
                while can_play_card:
                    lowest_cost = 100
                    cheapest_card = 100
                    for card_no in cards.keys():
                        card = cards[card_no]
                        if card.location != 0:
                            continue

                        if card.card_type > 0:
                            continue

                        if cards[card_no].cost < lowest_cost:
                            lowest_cost = cards[card_no].cost
                            cheapest_card = card_no

                    if cheapest_card < 100:
                        card_to_play = cards[cheapest_card]
                        if card_to_play.cost <= my_mana:
                            battle_command += "SUMMON %s;" % card_to_play.instance_id

                            if "C" in card_to_play.abilities:
                                battle_command += "ATTACK %s %s;" % (card_to_play.instance_id, target)

                            num_my_creatures += 1
                            my_mana -= card_to_play.cost
                            cards.pop(cheapest_card, None)
                        else:
                            can_play_card = False
                    else:
                        can_play_card = False

                    if num_my_creatures > 5:
                        can_play_card = False

            # todo: look for items to play

            # issue attack orders - opponent
            for card_no in cards.keys():
                card = cards[card_no]
                if card.location != 1:
                    continue

                if card.card_type > 0:
                    continue

                if card.attack < 1:
                    continue

                battle_command += "ATTACK %s %s;" % (card.instance_id, target)

        if len(battle_command) > 0:
            print(battle_command)
        else:
            print("PASS")
