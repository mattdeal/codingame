import sys
import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "x=%s, y=%s" % (self.x, self.y)


class Explorer(Point):
    def __init__(self, id, x, y, p_0, p_1, p_2):
        Point.__init__(self, x, y)
        self.id = id
        self.sanity = p_0
        self.param_1 = p_1
        self.param_2 = p_2


class Wanderer(Point):
    def __init__(self, id, x, y, p_0, p_1, p_2):
        Point.__init__(self, x, y)
        self.id = id
        self.time_remaining = p_0
        self.param_1 = p_1
        self.target = p_2


class Minion(Point):
    def __init__(self, id, x, y, p_0, p_1, p_2):
        Point.__init__(self, x, y)
        self.id = id
        self.time_until_spawn = p_0
        self.current_state = p_1
        self.target = p_2


class Effect:
    def __init__(self, p_0, p_1, p_2):
        self.time_remaining = p_0
        self.owner = p_1
        self.target = p_2

# helper methods
def debug(msg):
    print(str(msg), file=sys.stderr)


# manhattan distance formula
def distance_between(p1, p2):
    return abs(p1.x - p2.x) + abs(p1.y - p2.y)


# Survive the wrath of Kutulu
# Coded fearlessly by JohnnyYuge & nmahoude (ok we might have been a bit scared by the old god...but don't say anything)

spawn_locations = []
open_space = []

width = int(input())
height = int(input())
for i in range(height):
    line = input()
    debug(line)
    j = 0
    for letter in line:
        if letter == 'w':
            spawn_locations.append(Point(j, i))
        elif letter == '.':
            open_space.append(Point(j, i))

        j += 1

debug("spawn locations:")
for location in spawn_locations:
    debug(location)

debug("open space:")
for location in open_space:
    debug(location)

# sanity_loss_lonely: how much sanity you lose every turn when alone, always 3 until wood 1
# sanity_loss_group: how much sanity you lose every turn when near another player, always 1 until wood 1
# wanderer_spawn_time: how many turns the wanderer take to spawn, always 3 until wood 1
# wanderer_life_time: how many turns the wanderer is on map after spawning, always 40 until wood 1
sanity_loss_lonely, sanity_loss_group, wanderer_spawn_time, wanderer_life_time = [int(i) for i in input().split()]

my_id = -1

plan_count = 2
plan_turns_remaining = 0
light_count = 3
light_turns_remaining = 0

# game loop
while True:
    explorers = {}
    wanderers = {}
    effects = {}
    entity_count = int(input())  # the first given entity corresponds to your explorer
    for i in range(entity_count):
        entity_type, id, x, y, param_0, param_1, param_2 = input().split()
        id = int(id)
        x = int(x)
        y = int(y)
        param_0 = int(param_0)
        param_1 = int(param_1)
        param_2 = int(param_2)

        if my_id < 0:
            my_id = id

        if entity_type == "EXPLORER":
            # debug("exp")
            explorers[id] = (Explorer(id, x, y, param_0, param_1, param_2))
        elif entity_type == "WANDERER":
            # debug("wan")
            wanderers[id] = (Wanderer(id, x, y, param_0, param_1, param_2))
        elif entity_type == "SLASHER":
            # debug("wan")
            # todo: treat slashers differently than wanderers
            wanderers[id] = (Wanderer(id, x, y, param_0, param_1, param_2))
        elif entity_type == "EFFECT_PLAN":
            debug("plan")
        elif entity_type == "EFFECT_YELL":
            debug("yell")
        elif entity_type == "EFFECT_LIGHT":
            debug("light")
        elif entity_type == "EFFECT_SHELTER":
            debug("shelter")
        else:
            debug(entity_type)

    my_exp = explorers[my_id]
    wanderers_chasing_me = 0

    # find closest wanderer to my explorer
    dist_from_wanderers = {}
    for wanderer in wanderers.values():
        dist = distance_between(my_exp, wanderer)
        dist_from_wanderers[dist] = wanderer
        if wanderer.target == my_id:
            wanderers_chasing_me += 1

    # find farthest explorer from spawn
    dist_from_spawn = {}
    for explorer in explorers.values():
        if explorer.id == my_id:
            continue

        for spawn_location in spawn_locations:
            dist = distance_between(explorer, spawn_location)
            dist_from_spawn[dist] = explorer

    plan_turns_remaining -= 1
    light_turns_remaining -= 1

    # todo: if wanderer is near by, move away from it
    if len(dist_from_wanderers) > 0 and min(dist_from_wanderers.keys()) < 2:
        debug("run")
        # todo: for x -1 to x + 1
        # todo: for y -1 to y + 1
        # todo: where x != myexp.x and y != myexp.y
        # todo: find max distance from closest wanderer
        closest_wanderer = dist_from_wanderers[min(dist_from_wanderers.keys())]
        debug("closest wanderer " + str(closest_wanderer))
        safe_spots = {}
        for x in range(my_exp.x - 1, my_exp.x + 2):
            debug(x)
            for y in range(my_exp.y - 1, my_exp.y + 2):
                debug(y)
                if x == my_exp.x and y == my_exp.y:
                    continue

                temp = Point(x, y)
                debug(temp)
                if any(z for z in open_space if z.x == x and z.y == y):
                    dist = distance_between(closest_wanderer, temp)
                    safe_spots[dist] = temp
                else:
                    debug("temp not found")

        debug("safe spots " + str(len(safe_spots)))
        if len(safe_spots) > 0:
            safe_spot = safe_spots[max(safe_spots.keys())]
            print("MOVE %s %s" % (safe_spot.x, safe_spot.y))
        else:
            print("WAIT")
    elif light_count > 0 and light_turns_remaining < 1 and wanderers_chasing_me > 0:
        print("LIGHT")
        light_count -= 1
        light_turns_remaining = 4
    elif plan_count > 0 and plan_turns_remaining < 1 and my_exp.sanity < 210:
        print("PLAN")
        plan_count -= 1
        plan_turns_remaining = 6
    elif len(dist_from_spawn) > 0:
        safest_explorer = dist_from_spawn[min(dist_from_spawn.keys())]
        print("MOVE %s %s" % (safest_explorer.x, safest_explorer.y))
    else:
        print("WAIT")
