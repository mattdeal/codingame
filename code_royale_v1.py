import sys
import math

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
from typing import List


class Site:
    def __init__(self, site_id, x, y, radius):
        self.site_id = site_id
        self.x = x
        self.y = y
        self.radius = radius
        self.ignore_1 = 0
        self.ignore_2 = 0
        self.structure_type = -1
        self.owner = -1
        self.param_1 = 0
        self.param_2 = 0

    def is_owned(self):
        return self.owner > -1

    def is_friendly(self):
        return self.owner == 0

    def is_barracks(self):
        return self.structure_type == 2


class Unit:
    def __init__(self, x, y, owner, unit_type, health):
        self.x = x
        self.y = y
        self.owner = owner
        self.unit_type = unit_type
        self.health = health

    def is_queen(self):
        return self.unit_type == -1


def debug(msg):
    print(str(msg), file=sys.stderr)


def distance(x1, y1, x2, y2):
    return math.sqrt(((x2 - x1)**2) + ((y2 - y1)**2))


def distance_to_closest_site(unit, sites):
    dist = {}
    for site in sites.values():
        if not site.is_owned():
            d = distance(unit.x, unit.y, site.x, site.y)
            dist[d] = site.site_id

    return min(dist.keys())


def find_move(unit, sites):
    dist = {}
    for site in sites.values():
        if not site.is_owned():
            d = distance(unit.x, unit.y, site.x, site.y)
            dist[d] = site.site_id

    debug(str(dist))

    min_d = min(dist.keys())
    debug("min_d = " + str(min_d) + ", site_id = " + str(dist[min_d]))
    target_site = sites[dist[min_d]]

    # todo: do something besides wait
    print("MOVE " + str(target_site.x) + " " + str(target_site.y))

# todo: turn number
# todo: unit/building costs

sites = {}
num_sites = int(input())
for i in range(num_sites):
    site_id, x, y, radius = [int(j) for j in input().split()]
    sites[site_id] = Site(site_id, x, y, radius)

x0 = -1
y0 = -1

# game loop
while True:
    my_units = []
    enemy_units = []
    my_sites = []

    # touched_site: -1 if none
    gold, touched_site = [int(i) for i in input().split()]
    for i in range(num_sites):
        # ignore_1: used in future leagues
        # ignore_2: used in future leagues
        # structure_type: -1 = No structure, 2 = Barracks
        # owner: -1 = No structure, 0 = Friendly, 1 = Enemy
        site_id, ignore_1, ignore_2, structure_type, owner, param_1, param_2 = [int(j) for j in input().split()]
        sites[site_id].ignore_1 = ignore_1
        sites[site_id].ignore_2 = ignore_2
        sites[site_id].structure_type = structure_type
        sites[site_id].owner = owner
        sites[site_id].param_1 = param_1
        sites[site_id].param_2 = param_2

        if owner == 0:
            my_sites.append(site_id)

    queen = None

    # info about units on the map
    num_units = int(input())
    for i in range(num_units):
        # unit_type: -1 = QUEEN, 0 = KNIGHT, 1 = ARCHER
        x, y, owner, unit_type, health = [int(j) for j in input().split()]
        if owner == 0:
            my_units.append(Unit(x, y, owner, unit_type, health))
            if unit_type == -1:
                queen = Unit(x, y, owner, unit_type, health)
        else:
            enemy_units.append(Unit(x, y, owner, unit_type, health))

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    num_my_units = len(my_units)
    num_my_sites = len(my_sites)
    build = True

    if num_my_sites > 4 and queen is not None and distance_to_closest_site(queen, sites) > 200:
        debug("retreat")
        if distance(x0, y0, 0, 0) < 500:
            print("MOVE 30 30")
        else:
            print("MOVE 1890 970")
    else:
        # tell queen to build if able or move
        for unit in my_units:
            # debug(unit.is_queen())
            if unit.is_queen():
                # set initial location, used to retreat
                if x0 == -1:
                    x0 = unit.x
                    y0 = unit.y

                if touched_site > -1:
                    # debug(touched_site)
                    for site in sites.values():
                        # debug(str(site.site_id) + " " + str(touched_site) + " " + str(site.is_owned()))
                        if site.site_id == touched_site:
                            if site.is_owned():
                                    find_move(unit, sites)

                                # debug("site id is owned")
                                # if num_my_units > 3 * num_my_sites:
                                # else:
                                #     print("WAIT")
                            else:
                                # debug("site id is touched")
                                if gold >= 80:
                                    if num_my_sites < 1:
                                        build = True
                                    elif num_my_units < 3 * num_my_sites:
                                        build = False

                                    if build:
                                        # debug("building")
                                        print("BUILD " + str(site.site_id) + " BARRACKS-KNIGHT")
                                        gold -= 80
                                    else:
                                        # debug("waiting")
                                        print("WAIT")
                                else:
                                    # debug("waiting for money")
                                    print("BUILD " + str(site.site_id) + " MINE")

                            # debug("breaking for site")
                            break
                else:
                    find_move(unit, sites)

                # debug("breaking for unit")
                break

    train_command = ""
    for site in sites.values():
        if site.is_barracks() and site.is_friendly() and gold >= 80:
            train_command += str(site.site_id) + " "
            gold -= 80

    if len(train_command) > 0:
        print("TRAIN " + train_command.strip())
    else:
        print("TRAIN")

    # First line: A valid queen action
    # Second line: A set of training instructions
