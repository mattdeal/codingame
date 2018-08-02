import sys
from collections import OrderedDict


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

# v3 prioritize G @ 2
# card_rank = {1: 151, 2: 118, 3: 47, 4: 57, 5: 4, 6: 55, 7: 100, 8: 38, 9: 110, 10: 56, 11: 69, 12: 94, 13: 99, 14: 103,
#              15: 127, 16: 63, 17: 83, 18: 12, 19: 141, 20: 136, 21: 3, 22: 91, 23: 86, 24: 95, 25: 23, 26: 18, 27: 2,
#              28: 119, 29: 61, 30: 8, 31: 9, 32: 15, 33: 17, 34: 122, 35: 75, 36: 109, 37: 19, 38: 98, 39: 105, 40: 93,
#              41: 96, 42: 117, 43: 80, 44: 39, 45: 51, 46: 73, 47: 87, 48: 37, 49: 1, 50: 26, 51: 6, 52: 62, 53: 77,
#              54: 130, 55: 79, 56: 142, 57: 143, 58: 70, 59: 112, 60: 121, 61: 21, 62: 97, 63: 104, 64: 65, 65: 7,
#              66: 125, 67: 106, 68: 48, 69: 129, 70: 111, 71: 24, 72: 114, 73: 40, 74: 27, 75: 58, 76: 92, 77: 49,
#              78: 108, 79: 72, 80: 44, 81: 5, 82: 101, 83: 59, 84: 74, 85: 11, 86: 85, 87: 28, 88: 45, 89: 60, 90: 126,
#              91: 25, 92: 144, 93: 30, 94: 68, 95: 13, 96: 76, 97: 22, 98: 52, 99: 84, 100: 34, 101: 64, 102: 29,
#              103: 32, 104: 50, 105: 33, 106: 41, 107: 128, 108: 14, 109: 102, 110: 123, 111: 16, 112: 67, 113: 88,
#              114: 54, 115: 43, 116: 145, 117: 135, 118: 150, 119: 71, 120: 148, 121: 10, 122: 42, 123: 20, 124: 31,
#              125: 82, 126: 124, 127: 132, 128: 147, 129: 120, 130: 138, 131: 137, 132: 107, 133: 140, 134: 158,
#              135: 154, 136: 160, 137: 153, 138: 134, 139: 146, 140: 36, 141: 46, 142: 155, 143: 131, 144: 113, 145: 157,
#              146: 81, 147: 78, 148: 35, 149: 149, 150: 66, 151: 115, 152: 53, 153: 156, 154: 90, 155: 89, 156: 159,
#              157: 116, 158: 133, 159: 139, 160: 152}

#v3 prioritize G @ 40
# card_rank = {151: 160, 62: 159, 116: 158, 80: 157, 114: 156, 110: 155, 112: 154, 111: 153, 61: 152, 105: 151, 103: 150,
#              115: 149, 106: 148, 108: 147, 74: 146, 100: 145, 79: 144, 87: 143, 99: 142, 104: 141, 23: 140, 101: 139,
#              55: 138, 113: 137, 98: 136, 77: 135, 94: 134, 46: 133, 107: 132, 102: 131, 97: 130, 63: 129, 59: 128,
#              40: 127, 60: 126, 95: 125, 81: 124, 122: 123, 37: 122, 96: 121, 58: 120, 44: 119, 57: 118, 45: 117,
#              49: 116, 75: 115, 109: 114, 19: 113, 82: 112, 68: 111, 56: 110, 76: 109, 22: 108, 78: 107, 93: 106,
#              21: 105, 64: 104, 67: 103, 43: 102, 90: 101, 135: 100, 18: 99, 92: 98, 91: 97, 15: 96, 17: 95, 34: 94,
#              51: 93, 73: 92, 69: 91, 130: 90, 127: 89, 70: 88, 12: 87, 129: 86, 88: 85, 138: 84, 36: 83, 72: 82, 47: 81,
#              86: 80, 4: 79, 9: 78, 20: 77, 13: 76, 52: 75, 132: 74, 35: 73, 33: 72, 128: 71, 14: 70, 125: 69, 16: 68,
#              11: 67, 71: 66, 85: 65, 8: 64, 126: 63, 42: 62, 30: 61, 38: 60, 32: 59, 50: 58, 26: 57, 6: 56, 66: 55,
#              41: 54, 121: 53, 118: 52, 65: 51, 7: 50, 134: 49, 54: 48, 152: 47, 146: 46, 27: 45, 3: 44, 145: 43, 89: 42,
#              5: 41, 131: 40, 28: 39, 2: 38, 119: 37, 10: 36, 25: 35, 31: 34, 117: 33, 39: 32, 124: 31, 84: 30, 29: 29,
#              1: 28, 133: 27, 53: 26, 123: 25, 158: 24, 83: 23, 48: 22, 24: 21, 141: 20, 136: 19, 159: 18, 155: 17,
#              150: 16, 148: 15, 144: 14, 157: 13, 147: 12, 120: 11, 149: 10, 139: 9, 142: 8, 143: 7, 137: 6, 140: 5,
#              154: 4, 156: 3, 160: 2, 153: 1}

# v3 prioritize G @ 10
card_rank = {151: 160, 55: 159, 100: 158, 110: 157, 118: 156, 94: 155, 99: 154, 103: 153, 63: 152, 47: 151, 57: 150,
             4: 149, 91: 148, 95: 147, 38: 146, 56: 145, 122: 144, 98: 143, 69: 142, 105: 141, 93: 140, 96: 139,
             80: 138, 127: 137, 87: 136, 83: 135, 12: 134, 62: 133, 141: 132, 136: 131, 3: 130, 112: 129, 97: 128,
             86: 127, 104: 126, 106: 125, 111: 124, 114: 123, 40: 122, 23: 121, 92: 120, 18: 119, 49: 118, 108: 117,
             2: 116, 119: 115, 61: 114, 8: 113, 9: 112, 101: 111, 15: 110, 17: 109, 74: 108, 75: 107, 109: 106, 19: 105,
             117: 104, 39: 103, 51: 102, 73: 101, 37: 100, 1: 99, 26: 98, 6: 97, 77: 96, 130: 95, 79: 94, 142: 93,
             143: 92, 70: 91, 121: 90, 21: 89, 64: 88, 65: 87, 7: 86, 125: 85, 48: 84, 129: 83, 24: 82, 27: 81, 58: 80,
             102: 79, 72: 78, 44: 77, 5: 76, 59: 75, 11: 74, 85: 73, 28: 72, 45: 71, 60: 70, 126: 69, 25: 68, 144: 67,
             30: 66, 68: 65, 13: 64, 76: 63, 22: 62, 52: 61, 84: 60, 34: 59, 29: 58, 32: 57, 50: 56, 33: 55, 41: 54,
             128: 53, 14: 52, 123: 51, 16: 50, 138: 49, 67: 48, 88: 47, 54: 46, 43: 45, 145: 44, 107: 43, 135: 42,
             150: 41, 71: 40, 148: 39, 10: 38, 42: 37, 20: 36, 31: 35, 82: 34, 124: 33, 113: 32, 132: 31, 147: 30,
             120: 29, 137: 28, 140: 27, 158: 26, 154: 25, 160: 24, 153: 23, 134: 22, 146: 21, 36: 20, 115: 19, 46: 18,
             155: 17, 131: 16, 116: 15, 157: 14, 81: 13, 78: 12, 35: 11, 149: 10, 66: 9, 53: 8, 156: 7, 90: 6, 89: 5,
             159: 4, 133: 3, 139: 2, 152: 1}

my_deck = {}

CARD_TYPE_CREATURE = 0
CARD_TYPE_ITEM_GREEN = 1
CARD_TYPE_ITEM_RED = 2
CARD_TYPE_ITEM_BLUE = 3

LOCATION_HAND = 0
LOCATION_BOARD = 1
LOCATION_OPP = 2

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

    my_hand = {}
    my_board = {}
    enemy_board = {}
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

        if mode == "DRAFT":
            debug("card %s, rank %s" % (card_number, card_rank[card_number]))
            cards[len(cards)] = Card(card_number, instance_id, location, card_type, cost, attack, defense, abilities,
                                     my_health_change, opponent_health_change, card_draw)
        else:
            if location == LOCATION_BOARD:
                my_board[instance_id] = Card(card_number, instance_id, location, card_type, cost, attack, defense,
                                             abilities,
                                             my_health_change, opponent_health_change, card_draw)
            elif location == LOCATION_HAND:
                my_hand[instance_id] = Card(card_number, instance_id, location, card_type, cost, attack, defense,
                                            abilities,
                                            my_health_change, opponent_health_change, card_draw)
            else:
                enemy_board[instance_id] = Card(card_number, instance_id, location, card_type, cost, attack, defense,
                                                abilities,
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
        target = -1

        my_board_by_attack = {}
        for card in my_board.values():
            if my_board_by_attack.get(card.attack):
                my_board_by_attack[card.attack + .1] = card
            else:
                my_board_by_attack[card.attack] = card

        sorted_by_attack = OrderedDict(sorted(my_board_by_attack.items(), key=lambda t: t[0]))

        debug("myboard %s, sorted %s" % (len(my_board), len(sorted_by_attack)))

        if len(enemy_board) > 0:
            debug("creatures")

            # get creatures with G
            target_creatures = {}
            for enemy in enemy_board.values():
                if "G" in enemy.abilities:
                    if target_creatures.get(enemy.defense):
                        target_creatures[enemy.defense + .1] = enemy
                    else:
                        target_creatures[enemy.defense] = enemy

            # if creatures_g, try to kill them without loss
            if len(target_creatures) > 0:
                debug("creatures with G exist, attempt positive trade")
                sorted_targets = OrderedDict(sorted(target_creatures.items(), key=lambda t: t[0]))
                for enemy in sorted_targets.values():
                    debug("target %s" % enemy.instance_id)

                    for card in sorted_by_attack.values():
                        if card.card_type != CARD_TYPE_CREATURE:
                            debug("skip %s" % card.instance_id)
                            continue

                        if str(card.instance_id) in battle_command:
                            debug("skip %s" % card.instance_id)
                            continue

                        if card.attack < 1:
                            debug("skip %s" % card.instance_id)
                            continue

                        if card.will_kill(enemy) and not card.will_be_killed(enemy):
                            target_creatures.pop(enemy.instance_id, None)
                            enemy_board.pop(enemy.instance_id, None)
                            card.defense -= enemy.attack
                            battle_command += "ATTACK %s %s;" % (card.instance_id, enemy.instance_id)
                            debug("ATTACK %s %s;" % (card.instance_id, enemy.instance_id))

            # creatures with G are still alive, try to trade
            if len(target_creatures) > 0:
                debug("creatures with G still exist, attempt even trade")
                sorted_targets = OrderedDict(sorted(target_creatures.items(), key=lambda t: t[0]))
                for enemy in sorted_targets.values():
                    debug("target %s" % enemy.instance_id)

                    for card in sorted_by_attack.values():
                        if card.card_type != CARD_TYPE_CREATURE:
                            debug("skip %s" % card.instance_id)
                            continue

                        if str(card.instance_id) in battle_command:
                            debug("skip %s" % card.instance_id)
                            continue

                        if "G" in card.abilities:
                            debug("skip %s" % card.instance_id)
                            continue

                        if card.attack < 1:
                            debug("skip %s" % card.instance_id)
                            continue

                        if card.will_kill(enemy):
                            target_creatures.pop(enemy.instance_id, None)
                            enemy_board.pop(enemy.instance_id, None)
                            my_board.pop(card.instance_id, None)
                            battle_command += "ATTACK %s %s;" % (card.instance_id, enemy.instance_id)
                            debug("ATTACK %s %s;" % (card.instance_id, enemy.instance_id))

            # creatures with G are still alive, attack them unless our card also has G
            if len(target_creatures) > 0:
                debug("creatures with G still exist, attempt negative trade")
                sorted_targets = OrderedDict(sorted(target_creatures.items(), key=lambda t: t[0]))
                for enemy in sorted_targets.values():
                    debug("target %s" % enemy.instance_id)
                    for card in sorted_by_attack.values():
                        if card.card_type != CARD_TYPE_CREATURE:
                            debug("skip %s" % card.instance_id)
                            continue

                        if str(card.instance_id) in battle_command:
                            debug("skip %s" % card.instance_id)
                            continue

                        if "G" in card.abilities:
                            debug("skip %s" % card.instance_id)
                            continue

                        if card.attack < 1:
                            debug("skip %s" % card.instance_id)
                            continue

                        battle_command += "ATTACK %s %s;" % (card.instance_id, enemy.instance_id)
                        debug("ATTACK %s %s;" % (card.instance_id, enemy.instance_id))

                        if enemy.will_kill(card):
                            my_board.pop(card.instance_id, None)
                        else:
                            card.defense -= enemy.attack

                        if card.will_kill(enemy):
                            target_creatures.pop(enemy.instance_id, None)
                            enemy_board.pop(enemy.instance_id, None)
                        else:
                            enemy.defense -= card.attack

            if len(enemy_board) > 0:
                target_creatures = {}
                for enemy in enemy_board.values():
                    if target_creatures.get(enemy.defense):
                        target_creatures[enemy.defense + .1] = enemy
                    else:
                        target_creatures[enemy.defense] = enemy

                sorted_targets = OrderedDict(sorted(target_creatures.items(), key=lambda t: t[0]))

                debug("enemy still has cards remaining, attempt positive trade")
                for enemy in sorted_targets.values():
                    debug("target %s" % enemy.instance_id)

                    for card in sorted_by_attack.values():
                        if card.card_type != CARD_TYPE_CREATURE:
                            debug("skip %s" % card.instance_id)
                            continue

                        if str(card.instance_id) in battle_command:
                            debug("skip %s" % card.instance_id)
                            continue

                        if card.will_kill(enemy) and not card.will_be_killed(enemy):
                            target_creatures.pop(enemy.instance_id, None)
                            enemy_board.pop(enemy.instance_id, None)
                            card.defense -= enemy.attack
                            battle_command += "ATTACK %s %s;" % (card.instance_id, enemy.instance_id)
                            debug("ATTACK %s %s;" % (card.instance_id, enemy.instance_id))

                # creatures are still alive, try to trade
                if len(target_creatures) > 0:
                    debug("creatures still exist, attempt even trade")
                    sorted_targets = OrderedDict(sorted(target_creatures.items(), key=lambda t: t[0]))
                    for enemy in sorted_targets.values():
                        debug("target %s" % enemy.instance_id)

                        for card in sorted_by_attack.values():
                            if card.card_type != CARD_TYPE_CREATURE:
                                debug("skip %s" % card.instance_id)
                                continue

                            if str(card.instance_id) in battle_command:
                                debug("skip %s" % card.instance_id)
                                continue

                            if "G" in card.abilities:
                                debug("skip %s" % card.instance_id)
                                continue

                            if card.attack < 1:
                                debug("skip %s" % card.instance_id)
                                continue

                            if card.will_kill(enemy):
                                target_creatures.pop(enemy.instance_id, None)
                                enemy_board.pop(enemy.instance_id, None)
                                my_board.pop(card.instance_id, None)
                                battle_command += "ATTACK %s %s;" % (card.instance_id, enemy.instance_id)
                                debug("ATTACK %s %s;" % (card.instance_id, enemy.instance_id))

                # creatures are still alive, attack them unless our card also has G
                if len(target_creatures) > 0:
                    debug("creatures still exist, attempt negative trade")
                    sorted_targets = OrderedDict(sorted(target_creatures.items(), key=lambda t: t[0]))
                    for enemy in sorted_targets.values():
                        debug("target %s" % enemy.instance_id)

                        for card in sorted_by_attack.values():
                            if card.card_type != CARD_TYPE_CREATURE:
                                debug("skip %s" % card.instance_id)
                                continue

                            if str(card.instance_id) in battle_command:
                                debug("skip %s" % card.instance_id)
                                continue

                            if "G" in card.abilities:
                                debug("skip %s" % card.instance_id)
                                continue

                            if card.attack < 1:
                                debug("skip %s" % card.instance_id)
                                continue

                            battle_command += "ATTACK %s %s;" % (card.instance_id, enemy.instance_id)
                            debug("ATTACK %s %s;" % (card.instance_id, enemy.instance_id))

                            if enemy.will_kill(card):
                                my_board.pop(card.instance_id, None)
                            else:
                                card.defense -= enemy.attack

                            if card.will_kill(enemy):
                                target_creatures.pop(enemy.instance_id, None)
                                enemy_board.pop(enemy.instance_id, None)
                            else:
                                enemy.defense -= card.attack

                # try to attack player, attempts will fail if the command is invalid
                debug("all cards that did not attack try to attack opponent")
                for card in my_board.values():
                    if card.card_type != CARD_TYPE_CREATURE:
                        debug("skip %s" % card.instance_id)
                        continue

                    if card.attack < 1:
                        debug("skip %s" % card.instance_id)
                        continue

                    if str(card.instance_id) in battle_command:
                        debug("skip %s" % card.instance_id)
                        continue

                    battle_command += "ATTACK %s %s;" % (card.instance_id, -1)
                    debug("ATTACK %s %s;" % (card.instance_id, -1))
            else:
                debug("enemy board is empty, attack player")
                # try to attack player, attempts will fail if the command is invalid
                for card in my_board.values():
                    if card.card_type != CARD_TYPE_CREATURE:
                        debug("skip %s" % card.instance_id)
                        continue

                    if str(card.instance_id) in battle_command:
                        debug("skip %s" % card.instance_id)
                        continue

                    battle_command += "ATTACK %s %s;" % (card.instance_id, -1)
                    debug("ATTACK %s %s;" % (card.instance_id, -1))

            # todo: look for items to play
        else:
            debug("Attack opp")
            # try to attack player, attempts will fail if the command is invalid
            for card in my_board.values():
                if card.card_type != CARD_TYPE_CREATURE:
                    debug("skip %s" % card.instance_id)
                    continue

                if card.attack < 1:
                    debug("skip %s" % card.instance_id)
                    continue

                if str(card.instance_id) in battle_command:
                    debug("skip %s" % card.instance_id)
                    continue

                battle_command += "ATTACK %s %s;" % (card.instance_id, -1)
                debug("ATTACK %s %s;" % (card.instance_id, -1))

        # summon more creatures
        if len(my_board) < 6 and len(my_hand) > 0:
            num_my_creatures = len(my_board)
            debug("look for creatures")
            # play cheapest cards available
            can_play_card = True
            while can_play_card:
                lowest_cost = 100
                cheapest_card = 100
                for card_no in my_hand.keys():
                    card = my_hand[card_no]
                    if card.location != 0:
                        continue

                    if card.card_type > 0:
                        continue

                    if my_hand[card_no].cost < lowest_cost:
                        lowest_cost = my_hand[card_no].cost
                        cheapest_card = card_no

                if cheapest_card < 100:
                    card_to_play = my_hand[cheapest_card]
                    if card_to_play.cost <= my_mana:
                        battle_command += "SUMMON %s;" % card_to_play.instance_id

                        if "C" in card_to_play.abilities:
                            battle_command += "ATTACK %s %s;" % (card_to_play.instance_id, -1)
                            debug("ATTACK %s %s;" % (card_to_play.instance_id, -1))

                        num_my_creatures += 1
                        my_mana -= card_to_play.cost
                        my_hand.pop(cheapest_card, None)
                    else:
                        can_play_card = False
                else:
                    can_play_card = False

                if num_my_creatures > 5:
                    can_play_card = False

        # todo: look for items to play

        # issue attack orders
        if len(battle_command) > 0:
            print(battle_command)
        else:
            print("PASS")
