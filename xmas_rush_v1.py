import sys
import math


class Tile:
    def __init__(self, x, y, vals):
        self.x = x
        self.y = y
        self.top = vals[0]
        self.right = vals[1]
        self.bottom = vals[2]
        self.left = vals[3]

    def __str__(self):
        return f"x={self.x},y={self.y},t={self.top},r={self.right},b={self.bottom},l={self.left}"


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "x=%s, y=%s" % (self.x, self.y)


def debug(msg):
    print(str(msg), file=sys.stderr)


# manhattan distance formula
def distance_between(p1, p2):
    return abs(p1.x - p2.x) + abs(p1.y - p2.y)


# Help the Christmas elves fetch presents in a magical labyrinth!
items = {}
player_location = None

MOVE = 1
PUSH = 0

# game loop
while True:
    turn_type = int(input())

    for i in range(7):
        for tile in input().split():
            # debug(tile)
            pass

    for i in range(2):
        # num_player_cards: the total number of quests for a player (hidden and revealed)
        num_player_cards, player_x, player_y, player_tile = input().split()
        num_player_cards = int(num_player_cards)
        player_x = int(player_x)
        player_y = int(player_y)

        if i == 0:
            player_location = Point(player_x, player_y)

    num_items = int(input())  # the total number of items available on board and on player tiles

    for i in range(num_items):
        item_name, item_x, item_y, item_player_id = input().split()
        item_x = int(item_x)
        item_y = int(item_y)
        item_location = Point(item_x, item_y)
        item_player_id = int(item_player_id)

        if item_player_id == 0:
            items[distance_between(player_location, item_location)] = item_location

    num_quests = int(input())  # the total number of revealed quests for both players

    for i in range(num_quests):
        quest_item_name, quest_player_id = input().split()
        quest_player_id = int(quest_player_id)

    debug(f"turn_type={turn_type}")
    debug(f"player_location={player_location}")

    closest_item = items[min(items.keys())]
    debug(f"closest_item={closest_item}")

    if turn_type == MOVE:
        if distance_between(player_location, closest_item) == 1:
            if player_location.x > closest_item.x:
                print("MOVE LEFT")
            elif player_location.x < closest_item.x:
                print("MOVE RIGHT")
            elif player_location.y > closest_item.y:
                print("MOVE DOWN")
            else:
                print("MOVE UP")
        else:
            print("PASS")
    else:
        debug(player_location)

        if player_location.x > closest_item.x:
            print(f"PUSH {player_location.y} LEFT")
        elif player_location.x < closest_item.x:
            print(f"PUSH {player_location.y} RIGHT")
        elif player_location.y > closest_item.y:
            print(f"PUSH {player_location.x} DOWN")
        elif player_location.y < closest_item.y:
            print(f"PUSH {player_location.x} UP")
        else:
            print(f"PUSH {player_x} RIGHT")
