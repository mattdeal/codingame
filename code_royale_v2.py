import sys
import math
from collections import OrderedDict


class Site:
    def __init__(self, site_id, x, y, radius):
        self.site_id = site_id
        self.x = x
        self.y = y
        self.radius = radius
        self.gold_remaining = 0
        self.max_mine_size = 0
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

    def is_tower(self):
        return self.structure_type == 1

    def is_mine(self):
        return self.structure_type == 0

    def is_empty(self):
        return self.structure_type == -1

    def __str__(self):
        return "id=%s, x=%s, y=%s, r=%s, type=%s, owner=%s, p1=%s, p2=%s, max_mine=%s" % (
            self.site_id, self.x, self.y, self.radius, self.structure_type, self.owner,
            self.param_1, self.param_2, self.max_mine_size)


class Unit:
    def __init__(self, x, y, owner, unit_type, health, radius=1):
        self.x = x
        self.y = y
        self.owner = owner
        self.unit_type = unit_type
        self.health = health
        self.radius = radius

    def is_queen(self):
        return self.unit_type == -1

    def is_knight(self):
        return self.unit_type == 0

    def is_archer(self):
        return self.unit_type == 1

    def is_giant(self):
        return self.unit_type == 2


# helper methods
def debug(msg):
    print(str(msg), file=sys.stderr)


def distance(x1, y1, x2, y2):
    return math.sqrt(((x2 - x1) ** 2) + ((y2 - y1) ** 2))


def calculate_angle_between(unit, target):
    """
    Calculates the angle between this object and the target in degrees.

    :param Entity target: The target to get the angle between.
    :return: Angle between entities in degrees
    :rtype: float
    """
    return math.degrees(math.atan2(target.y - unit.y, target.x - unit.x)) % 360


def find_sites_by_distance(unit, sites):
    dist = {}
    for site in sites.values():
        closest_point = closest_point_to(unit, site)
        d = distance(unit.x, unit.y, closest_point[0], closest_point[1])
        dist[d] = site

    return OrderedDict(sorted(dist.items(), key=lambda t: t[0]))


def find_sites_by_distance_reversed(unit, sites):
    dist = {}
    for site in sites.values():
        closest_point = closest_point_to(unit, site)
        d = -distance(unit.x, unit.y, closest_point[0], closest_point[1])
        dist[d] = site

    return OrderedDict(sorted(dist.items(), key=lambda t: t[0]))


def find_enemies_by_distance(unit, enemies, enemy_type):
    dist = {}
    for enemy in enemies:
        if enemy.unit_type == enemy_type:
            closest_point = closest_point_to(unit, enemy)
            d = distance(unit.x, unit.y, closest_point[0], closest_point[1])
            dist[d] = enemy

    return OrderedDict(sorted(dist.items(), key=lambda t: t[0]))


def site_is_safe(target_site, enemies, sites):
    enemy_towers = {}
    for site in sites.values():
        if site.site_id != target_site.site_id:
            if not site.is_friendly() and site.is_tower():
                dist = distance(target_site.x, target_site.y, site.x, site.y)
                enemy_towers[dist] = site

    if len(enemy_towers) > 0:
        for key in enemy_towers.keys():
            if enemy_towers[key].param_2 + 50 > key:
                debug("tower too close, site is unsafe")
                return False

        # closest_tower = min(enemy_towers.keys())
        # if closest_tower < 250:
        #     debug("tower too close, site is unsafe")
        #     return False

    enemy_knights = {}
    for enemy in enemies:
        if enemy.unit_type == 0:
            dist = distance(target_site.x, target_site.y, enemy.x, enemy.y)
            enemy_knights[dist] = enemy

    if len(enemy_knights) > 0:
        closest_knight = min(enemy_knights.keys())
        if closest_knight < 200:
            debug("enemy too close, site is unsafe")
            return False

    return True


def closest_point_to(unit, target, min_distance=0):
    """
    Find the closest point to the given ship near the given target, outside its given radius,
    with an added fudge of min_distance.

    :param Entity target: The target to compare against
    :param int min_distance: Minimum distance specified from the object's outer radius
    :return: The closest point's coordinates
    :rtype: Position
    """
    angle = calculate_angle_between(unit, target)
    radius = target.radius + min_distance
    x = target.x + radius * math.cos(math.radians(angle))
    y = target.y + radius * math.sin(math.radians(angle))

    return (x, y)


# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
sites = {}

x0 = -1
y0 = -1
retreat_x = -1
retreat_y = -1

focus_site_id = -1

num_sites = int(input())
for i in range(num_sites):
    site_id, x, y, radius = [int(j) for j in input().split()]
    sites[site_id] = Site(site_id, x, y, radius)

# todo: determine value of sites
# - if max_mine_size is high, do not build anything but a mine on it
# - once gold_remaining is 0, build a tower on it

# game loop
while True:
    my_units = []
    enemy_units = []
    my_sites = []
    my_barracks = []
    my_mines = []
    my_towers = []
    queen = None

    # touched_site: -1 if none
    gold, touched_site = [int(i) for i in input().split()]

    for i in range(num_sites):
        # gold_remaining: -1 if unknown
        # max_mine_size: -1 if unknown
        # structure_type: -1 = No structure, 0 = Goldmine, 1 = Tower, 2 = Barracks
        # owner: -1 = No structure, 0 = Friendly, 1 = Enemy
        site_id, gold_remaining, max_mine_size, structure_type, owner, param_1, param_2 = [int(j) for j in
                                                                                           input().split()]
        sites[site_id].gold_remaining = gold_remaining
        sites[site_id].max_mine_size = max_mine_size
        sites[site_id].structure_type = structure_type
        sites[site_id].owner = owner
        sites[site_id].param_1 = param_1
        sites[site_id].param_2 = param_2

        # get my owned sites
        if owner == 0:
            my_sites.append(site_id)

            if structure_type == 2:
                my_barracks.append(site_id)
            elif structure_type == 1:
                my_towers.append(site_id)
            elif structure_type == 0:
                my_mines.append(site_id)

    # debug(my_mines)
    # if len(my_mines) > 0:
    #     debug(sites[my_mines[0]])

    num_units = int(input())
    for i in range(num_units):
        # unit_type: -1 = QUEEN, 0 = KNIGHT, 1 = ARCHER, 2 = GIANT
        x, y, owner, unit_type, health = [int(j) for j in input().split()]
        if owner == 0:
            my_units.append(Unit(x, y, owner, unit_type, health))
            if unit_type == -1:
                queen = Unit(x, y, owner, unit_type, health, 30)
        else:
            enemy_units.append(Unit(x, y, owner, unit_type, health))

    # set starting location and retreat point
    if x0 == -1:
        x0 = queen.x
        y0 = queen.y
        dist_0 = distance(x0, y0, 0, 0)
        dist_max = distance(x0, y0, 1920, 1000)

        if dist_0 < dist_max:
            retreat_x = 30
            retreat_y = 30
        else:
            retreat_x = 1890
            retreat_y = 970

    num_my_units = len(my_units)
    num_my_sites = len(my_sites)
    num_my_barracks = len(my_barracks)
    num_my_towers = len(my_towers)
    num_my_mines = len(my_mines)
    nearby_knights = find_enemies_by_distance(queen, enemy_units, 0)

    queen_command = "WAIT"
    move_found = False

    if touched_site > -1 and not sites[touched_site].is_owned():
        debug("touching and no owner")
        # debug(str(sites[touched_site]))

        build_site = sites[touched_site]
        reserved_for_mine = build_site.max_mine_size > 3 and build_site.gold_remaining > 0

        focus_site_id = -1

        if len(nearby_knights) > 0:
            debug("enemies nearby")

            for key in nearby_knights.keys():
                if key < 400:
                    queen_command = "BUILD " + str(touched_site) + " TOWER"
                    move_found = True
                    break

        # no high priority tasks, build something
        if not move_found:
            if num_my_barracks < 1 and not reserved_for_mine:
                queen_command = "BUILD " + str(touched_site) + " BARRACKS-ARCHER"
            elif num_my_mines < 2 and reserved_for_mine:
                queen_command = "BUILD " + str(touched_site) + " MINE"
            elif len(enemy_units) > 1 and num_my_towers < num_my_mines:
                queen_command = "BUILD " + str(touched_site) + " TOWER"
            elif num_my_barracks < 2 and not reserved_for_mine:
                queen_command = "BUILD " + str(touched_site) + " BARRACKS-KNIGHT"
            elif num_my_mines > 3 > num_my_barracks and not reserved_for_mine:
                queen_command = "BUILD " + str(touched_site) + " BARRACKS-GIANT"
            elif sites[touched_site].gold_remaining > 0:
                queen_command = "BUILD " + str(touched_site) + " MINE"
            else:
                queen_command = "BUILD " + str(touched_site) + " BARRACKS-KNIGHT"
    elif touched_site > -1 and sites[touched_site].is_owned() and not sites[touched_site].is_barracks():
        debug("touching, is owned, is not barracks")
        t = sites[touched_site]

        if len(nearby_knights) > 0:
            debug("enemies on board, upgrade tower?")

            # upgrade a tower if you're near it
            for key in nearby_knights.keys():
                if key < 300 and t.is_tower() and t.param_1 < 300:
                    debug("upgrading tower " + str(t))
                    queen_command = "BUILD " + str(touched_site) + " TOWER"
                    move_found = True
                    break

            # could not upgrade tower, move somewhere else
            if not move_found:
                debug("running away 1")
                for key in nearby_knights.keys():
                    if key < 300:
                        if queen.health > 30:
                            if num_my_towers > 1:
                                sorted_sites = find_sites_by_distance_reversed(queen, sites)
                                for site in sorted_sites.values():
                                    if site.is_tower() and site.is_friendly():
                                        debug("run to far away friendly tower")
                                        queen_command = "MOVE " + str(site.x) + " " + str(site.y)
                                        move_found = True
                                        break

                        if move_found:
                            break

                        debug("retreat")
                        queen_command = "MOVE " + str(retreat_x) + " " + str(retreat_y)
                        move_found = True
                        break
        if not move_found:
            if t.is_friendly() and t.is_tower() and t.param_1 < 500:
                debug("upgrade tower " + str(t))
                queen_command = "BUILD " + str(touched_site) + " TOWER"
                move_found = True
            elif t.is_friendly() and t.is_mine() and t.param_1 < t.max_mine_size:
                debug("upgrade mine " + str(t))
                queen_command = "BUILD " + str(touched_site) + " MINE"
                move_found = True

        # no upgrades available for this site, find a new one that is safe
        if not move_found:
            if focus_site_id > -1 and not sites[focus_site_id].is_owned():
                if site_is_safe(sites[focus_site_id], enemy_units, sites):
                    focus = sites[focus_site_id]
                    queen_command = "MOVE " + str(focus.x) + " " + str(focus.y)
            else:
                focus_site_id = -1
                sorted_sites = find_sites_by_distance(queen, sites)

                for site in sorted_sites.values():
                    if site.is_empty():
                        if site_is_safe(site, enemy_units, sites):
                            focus_site_id = site.site_id
                            queen_command = "MOVE " + str(site.x) + " " + str(site.y)
                            break
    else:
        debug("not touching")

        if len(nearby_knights) > 0:
            debug("run away 2")

            for key in nearby_knights.keys():
                if key < 200:
                    if queen.health > 30:
                        if num_my_towers > 1:
                            sorted_sites = find_sites_by_distance_reversed(queen, sites)
                            for site in sorted_sites.values():
                                if site.is_tower() and site.is_friendly():
                                    debug("run to far away friendly tower")
                                    queen_command = "MOVE " + str(site.x) + " " + str(site.y)
                                    move_found = True
                                    break

                    if move_found:
                        break

                    debug("retreat")
                    queen_command = "MOVE " + str(retreat_x) + " " + str(retreat_y)
                    move_found = True
                    break
        if not move_found:
            if focus_site_id > -1 and not sites[focus_site_id].is_owned():
                focus = sites[focus_site_id]
                queen_command = "MOVE " + str(focus.x) + " " + str(focus.y)
            else:
                focus_site_id = -1
                sorted_sites = find_sites_by_distance(queen, sites)

                # todo: add logic to make sites that are far away from enemies more attractive
                # - should reduce the number of times we leave resources in the corners

                for site in sorted_sites.values():
                    if site.is_empty():
                        if site_is_safe(site, enemy_units, sites):
                            focus_site_id = site.site_id
                            queen_command = "MOVE " + str(site.x) + " " + str(site.y)
                            break

        # todo: if no move, go do tower maintenance

    my_knights =[]
    my_archers = []
    my_giants = []
    enemy_knights = []
    enemy_archers = []
    enemy_giants = []
    enemy_towers = []

    for unit in my_units:
        if unit.unit_type == 0:
            my_knights.append(unit)
        elif unit.unit_type == 1:
            my_archers.append(unit)
        elif unit.unit_type == 2:
            my_giants.append(unit)

    for unit in enemy_units:
        if unit.unit_type == 0:
            enemy_knights.append(unit)
        elif unit.unit_type == 1:
            enemy_archers.append(unit)
        elif unit.unit_type == 2:
            enemy_giants.append(unit)

    for site in sites.values():
        if site.is_tower() and not site.is_friendly():
            enemy_towers.append(site)

    train_command = ""
    for site in sites.values():
        if site.is_barracks():
            # debug("barracks debug")
            # debug(site)
            if site.is_friendly():
                if site.param_2 == 2 and len(enemy_towers) > 0 and gold >= 140:
                    train_command += str(site.site_id) + " "
                    gold -= 140
                elif site.param_2 == 1 and len(enemy_knights) > 0 and gold >= 100:
                    train_command += str(site.site_id) + " "
                    gold -= 100
                elif site.param_2 == 0 and gold >= 80: # and len(my_knights) < 2
                    train_command += str(site.site_id) + " "
                    gold -= 80

    # print commands
    print(queen_command)

    if len(train_command) > 0:
        print("TRAIN " + train_command.strip())
    else:
        print("TRAIN")

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    # First line: A valid queen action
    # Second line: A set of training instructions
