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
    return math.degrees(math.atan2(unit.y - target.y, unit.x - target.x)) % 360


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
            if enemy_towers[key].param_2 > key: #+ enemy_towers[key].radius
                debug("tower %s range %s, site is unsafe" % (enemy_towers[key].site_id, enemy_towers[key].param_2))
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


def closest_point_to(unit, target, min_distance=5):
    angle = calculate_angle_between(unit, target)
    radius = target.radius + min_distance
    x = target.x + radius * math.cos(math.radians(angle))
    y = target.y + radius * math.sin(math.radians(angle))

    return x, y


def farthest_point_from(unit, target, min_distance=5):
    angle = calculate_angle_between(target, unit)
    radius = target.radius + min_distance
    x = target.x + radius * math.cos(math.radians(angle))
    y = target.y + radius * math.sin(math.radians(angle))

    return x, y


# called when threat level == 0, gets a safe empty site closest to queen
def get_new_goal(max_distance=1000):
    sorted_sites = find_sites_by_distance(queen, sites)
    for key in sorted_sites.keys():
        if key > max_distance:
            break

        eval_site = sorted_sites[key]
        if eval_site.is_empty():
            if site_is_safe(eval_site, enemy_units, sites):
                return eval_site.site_id

    return -1


# called when threat level == 1, gets a safe empty site closest to queen
def get_new_goal_1(safety_check=False):
    # if tower count < 1, find empty site closest to queen, build tower in queen commands
    # if tower count < 3, find empty site closest to existing towers, build tower in queen commands
    # - if > some max distance, find the closest empty space from retreat point

    if len(my_towers) < 1:
        return get_new_goal()
    elif len(my_towers) < 3:
        sites_near_towers = {}
        for site in neutral_sites:
            d = 0
            for tower in my_towers:
                d += distance(site.x, site.y, tower.x, tower.y)

            sites_near_towers[d] = site

        if len(sites_near_towers) < 1:
            debug("problem finding site near tower, sites_near_towers is empty")
        else:
            sorted_sites = OrderedDict(sorted(sites_near_towers.items(), key=lambda t: t[0]))
            for site in sorted_sites.values():
                if safety_check:
                    if site_is_safe(site, enemy_units, sites):
                        return site.site_id
                else:
                    return site.site_id

    # everything is OK for now, get threat 0 goal
    return get_new_goal(800)


# called when threat level == 2,
# if queen is close to an empty site, returns that site_id
# otherwise, returns the site_id of the friendly tower furthest away from the closest enemy
def get_new_goal_2():
    # if tower count < 1, find empty site closest to queen, build tower in queen commands
    # if tower count < 3, find empty site closest to existing tower(s) and retreat location, build tower
    # otherwise, find the friendly tower farthest from the closest knight, move to location in queen commands
    if len(my_towers) < 1:
        return get_new_goal(600)
    elif len(my_towers) < 3:
        return get_new_goal_1(safety_check=False)
    else:
        knights_near_queen = {}
        for knight in enemy_knights:
            d = distance(queen.x, queen.y, knight.x, knight.y)
            knights_near_queen[d] = knight

        closest_knight = knights_near_queen[min(knights_near_queen.keys())]
        towers_near_knight = {}
        for tower in my_towers:
            d = distance(closest_knight.x, closest_knight.y, tower.x, tower.y)
            towers_near_knight[d] = tower

        farthest_tower = towers_near_knight[max(towers_near_knight.keys())]
        return farthest_tower.site_id


def get_new_goal_3():
    knights_near_queen = {}
    for knight in enemy_knights:
        d = distance(queen.x, queen.y, knight.x, knight.y)
        knights_near_queen[d] = knight

    closest_knight = knights_near_queen[min(knights_near_queen.keys())]
    towers_near_knight = {}
    for tower in my_towers:
        d = distance(closest_knight.x, closest_knight.y, tower.x, tower.y)
        towers_near_knight[d] = tower

    farthest_tower = towers_near_knight[max(towers_near_knight.keys())]
    return farthest_tower.site_id


def intersect_segment_circle(x0, y0, x1, y1, site, fudge=1):
    dx = x1 - x0
    dy = y1 - y0

    a = dx ** 2 + dy ** 2
    b = -2 * (x0 ** 2 - x0 * x1 - x0 * site.x + x1 * site.x +
              y0 ** 2 - y0 * y1 - y0 * site.y + y1 * site.y)
    c = (x0 - site.x) ** 2 + (y0 - site.y) ** 2

    if a == 0.0:
        # Start and end are the same point
        return distance(x0, y0, site.x, site.y) <= site.radius + fudge

    # Time along segment when closest to the circle (vertex of the quadratic)
    t = min(-b / (2 * a), 1.0)
    if t < 0:
        return False

    closest_x = x0 + dx * t
    closest_y = y0 + dy * t
    closest_distance = distance(closest_x, closest_y, site.x, site.y)

    return closest_distance <= site.radius + fudge


def sites_between(current_x, current_y, target_x, target_y):
    sites_between = []

    for site in sites.values():
        if -1 < goal_site != site.site_id:
            if intersect_segment_circle(current_x, current_y, target_x, target_y, site):
                sites_between.append(site)

    debug("sites between %s, %s and %s, %s = %s" % (current_x, current_y, target_x, target_y, len(sites_between)))
    return sites_between


def generate_queen_move(target_x, target_y, max_corrections=50, angular_step=5):
    if len(sites_between(queen.x, queen.y, target_x, target_y)) > 0:
        dist = distance(queen.x, queen.y, target_x, target_y)
        temp_site = Site(-1, target_x, target_y, 1)
        angle = calculate_angle_between(queen, temp_site)
        new_target_dx = math.cos(math.radians(angle + angular_step)) * dist
        new_target_dy = math.sin(math.radians(angle + angular_step)) * dist
        new_target_x = target_x + new_target_dx
        new_target_y = target_y + new_target_dy

        debug("dist = %s" % dist)
        debug("temp_site = %s" % temp_site)
        debug("angle = %s" % angle)
        debug("new_dx = %s" % new_target_dx)
        debug("new_dy = %s" % new_target_dy)
        debug("new_x = %s" % new_target_x)
        debug("new_y = %s" % new_target_y)

        return generate_queen_move(new_target_x, new_target_y, max_corrections - 1, angular_step * ANGULAR_STEP_MOD)

    return "MOVE %s %s" % (int(target_x), int(target_y))


# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
sites = {}

x0 = -1
y0 = -1
retreat_x = -1
retreat_y = -1
retreat_site = None

goal_site = -1

previous_threat_level = 0

ANGULAR_STEP_MOD = 1

num_sites = int(input())
for i in range(num_sites):
    site_id, x, y, radius = [int(j) for j in input().split()]
    sites[site_id] = Site(site_id, x, y, radius)

# game loop
while True:
    my_units = []
    my_knights = []
    my_archers = []
    my_giants = []

    enemy_units = []
    enemy_knights = []
    enemy_archers = []
    enemy_giants = []

    my_sites = []
    my_barracks = []
    my_mines = []
    my_towers = []

    enemy_sites = []
    enemy_barracks = []
    enemy_mines = []
    enemy_towers = []

    neutral_sites = []

    my_income = 0
    enemy_income = 0

    queen = None
    enemy_queen = None

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

        # determine site ownership
        tmp_site = sites[site_id]
        if owner == 0:
            my_sites.append(tmp_site)

            if tmp_site.is_barracks():
                my_barracks.append(tmp_site)
            elif tmp_site.is_tower():
                my_towers.append(tmp_site)
            elif tmp_site.is_mine():
                my_mines.append(tmp_site)
                my_income += tmp_site.param_1
        elif owner == 1:
            enemy_sites.append(tmp_site)
            if tmp_site.is_barracks():
                enemy_barracks.append(tmp_site)
            elif tmp_site.is_tower():
                enemy_towers.append(tmp_site)
            elif tmp_site.is_mine():
                enemy_mines.append(tmp_site)
                enemy_income += tmp_site.param_1
        else:
            neutral_sites.append(tmp_site)

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
            elif unit_type == 0:
                my_knights.append(Unit(x, y, owner, unit_type, health, 20))
            elif unit_type == 1:
                my_archers.append(Unit(x, y, owner, unit_type, health, 25))
            elif unit_type == 2:
                my_giants.append(Unit(x, y, owner, unit_type, health, 40))
        else:
            enemy_units.append(Unit(x, y, owner, unit_type, health))
            if unit_type == -1:
                enemy_queen = Unit(x, y, owner, unit_type, health, 30)
            elif unit_type == 0:
                enemy_knights.append(Unit(x, y, owner, unit_type, health, 20))
            elif unit_type == 1:
                enemy_archers.append(Unit(x, y, owner, unit_type, health, 25))
            elif unit_type == 2:
                enemy_giants.append(Unit(x, y, owner, unit_type, health, 40))

    # set starting location and retreat point
    if x0 == -1:
        x0 = queen.x
        y0 = queen.y
        dist_0 = distance(x0, y0, 0, 0)
        dist_max = distance(x0, y0, 1920, 1000)

        if dist_0 < dist_max:
            retreat_x = 30
            retreat_y = 30
            ANGULAR_STEP_MOD = -1
        else:
            retreat_x = 1890
            retreat_y = 970

        retreat_site = Site(100, retreat_x, retreat_y, 0)

    queen_command = "WAIT"
    move_found = False
    t_site = None

    if touched_site > -1:
        t_site = sites[touched_site]

    # determine threat level
    threat_level = 0
    closest_enemy_knight = None
    if len(enemy_knights) > 0:
        closest_enemy_knight = find_enemies_by_distance(queen, enemy_knights, 0)
        if len(closest_enemy_knight) > 0:
            d = min(closest_enemy_knight.keys())
            if d < 350:
                threat_level = 3
            elif d < 600:
                threat_level = 2
            else:
                threat_level = 1

    #  handle threat level change
    if threat_level > previous_threat_level:
        debug("threat level increased")

        if threat_level > 2:
            goal_site = get_new_goal_3()
        elif threat_level > 1:
            goal_site = get_new_goal_2()
        elif threat_level > 0:
            goal_site = get_new_goal_1()

        debug("new goal set site_id = %s" % goal_site)
        debug("touched_site = %s" % touched_site)

    previous_threat_level = threat_level

    debug("touching = %s" % touched_site)
    debug("goal = %s" % goal_site)

    # determine what the queen should do based on threat level
    if threat_level == 3:
        debug("threat level %s" % threat_level)

        if goal_site == -1:
            debug("no goal set, setting goal")
            goal_site = get_new_goal_3()
            if goal_site > -1:
                debug("new goal set")
            else:
                debug("error: could not set goal 31")

        if touched_site > -1 and touched_site == goal_site:
            debug("touching goal")
            if t_site.is_empty():
                queen_command = "BUILD %s %s" % (touched_site, "TOWER")
            else:
                debug("touched goal site is not empty, run in circles")
                g_site = sites[goal_site]
                # safe_spot = closest_point_to(retreat_site, g_site)
                safe_spot = farthest_point_from(closest_enemy_knight[min(closest_enemy_knight.keys())], g_site)
                debug("goal_site = %s" % g_site)
                debug("retreat_site = %s" % retreat_site)
                debug("safe spot %s, %s" % (safe_spot[0], safe_spot[1]))
                # queen_command = "MOVE %s %s" % (int(safe_spot[0]), int(safe_spot[1]))
                queen_command = generate_queen_move(int(safe_spot[0]), int(safe_spot[1]))
        elif touched_site > -1:
            if sites[touched_site].is_empty():
                queen_command = "BUILD %s %s" % (touched_site, "TOWER")
            else:
                debug("touched site (not goal) is not empty")
                g_site = sites[goal_site]
                # safe_spot = closest_point_to(retreat_site, g_site)
                safe_spot = farthest_point_from(closest_enemy_knight[min(closest_enemy_knight.keys())], g_site)
                debug("goal_site = %s" % g_site)
                debug("retreat_site = %s" % retreat_site)
                debug("safe spot %s, %s" % (safe_spot[0], safe_spot[1]))
                # queen_command = "MOVE %s %s" % (int(safe_spot[0]), int(safe_spot[1]))
                queen_command = generate_queen_move(int(safe_spot[0]), int(safe_spot[1]))
        elif goal_site > -1:
            debug("has goal, not touching")
            g_site = sites[goal_site]
            # safe_spot = closest_point_to(retreat_site, g_site)
            safe_spot = farthest_point_from(closest_enemy_knight[min(closest_enemy_knight.keys())], g_site)
            debug("safe spot %s, %s" % (safe_spot[0], safe_spot[1]))
            # queen_command = "MOVE %s %s" % (int(safe_spot[0]), int(safe_spot[1]))
            queen_command = generate_queen_move(int(safe_spot[0]), int(safe_spot[1]))
        else:
            debug("needs goal")
            goal_site = get_new_goal_3()
            if goal_site > -1:
                debug("new goal set")
                g_site = sites[goal_site]
                # safe_spot = closest_point_to(retreat_site, g_site)
                safe_spot = farthest_point_from(closest_enemy_knight[min(closest_enemy_knight.keys())], g_site)
                # queen_command = "MOVE %s %s" % (int(safe_spot[0]), int(safe_spot[1]))
                queen_command = generate_queen_move(int(safe_spot[0]), int(safe_spot[1]))
            else:
                debug("error: could not set goal 33")
    elif threat_level == 2:
        debug("threat level %s" % threat_level)

        if goal_site == -1:
            debug("no goal set, setting goal")
            goal_site = get_new_goal_2()
            if goal_site > -1:
                debug("new goal set")
            else:
                debug("error: could not set goal 21")

        if touched_site > -1 and touched_site == goal_site:
            debug("touching goal")
            if t_site.is_empty():
                queen_command = "BUILD %s %s" % (touched_site, "TOWER")
            else:
                debug("touched goal site is not empty")
                if t_site.is_friendly() and t_site.is_tower() and t_site.param_1 < 400:
                    debug("upgrading tower")
                    queen_command = "BUILD %s %s" % (touched_site, "TOWER")
                else:
                    debug("cannot upgrade goal site, looking for new hiding spot")
                    goal_site = get_new_goal_2()
                    if goal_site > -1:
                        debug("new goal set")
                        g_site = sites[goal_site]
                        # safe_spot = closest_point_to(retreat_site, g_site)
                        safe_spot = farthest_point_from(closest_enemy_knight[min(closest_enemy_knight.keys())], g_site)
                        # queen_command = "MOVE %s %s" % (int(safe_spot[0]), int(safe_spot[1]))
                        queen_command = generate_queen_move(int(safe_spot[0]), int(safe_spot[1]))
                    else:
                        debug("error: could not set goal 22")
        elif touched_site > -1:
            debug("touched site (not goal)")
            if t_site.is_friendly() and t_site.is_tower() and t_site.param_1 < 400:
                debug("upgrading tower")
                queen_command = "BUILD %s %s" % (touched_site, "TOWER")
            elif t_site.is_empty():
                debug("building tower")
                queen_command = "BUILD %s %s" % (touched_site, "TOWER")
            else:
                debug("cannot upgrade touched (non goal) site, moving on")
                g_site = sites[goal_site]
                # safe_spot = closest_point_to(retreat_site, g_site)
                safe_spot = farthest_point_from(closest_enemy_knight[min(closest_enemy_knight.keys())], g_site)
                # queen_command = "MOVE %s %s" % (int(safe_spot[0]), int(safe_spot[1]))
                queen_command = generate_queen_move(int(safe_spot[0]), int(safe_spot[1]))
        elif goal_site > -1:
            debug("has goal, not touching")
            g_site = sites[goal_site]
            # safe_spot = closest_point_to(retreat_site, g_site)
            safe_spot = farthest_point_from(closest_enemy_knight[min(closest_enemy_knight.keys())], g_site)

            # queen_command = "MOVE %s %s" % (int(safe_spot[0]), int(safe_spot[1]))
            queen_command = generate_queen_move(int(safe_spot[0]), int(safe_spot[1]))
        else:
            debug("needs goal")
            goal_site = get_new_goal_2()
            if goal_site > -1:
                debug("new goal set")
                g_site = sites[goal_site]
                # safe_spot = closest_point_to(retreat_site, g_site)
                safe_spot = farthest_point_from(closest_enemy_knight[min(closest_enemy_knight.keys())], g_site)
                # queen_command = "MOVE %s %s" % (int(safe_spot[0]), int(safe_spot[1]))
                queen_command = generate_queen_move(int(safe_spot[0]), int(safe_spot[1]))
            else:
                debug("error: could not set goal 23")
    elif threat_level == 1:
        debug("threat level 1")

        if goal_site == -1:
            debug("no goal set, setting goal")
            goal_site = get_new_goal_1()
            if goal_site > -1:
                debug("new goal set")
            else:
                debug("error: could not set goal 11")

        if touched_site > -1 and touched_site == goal_site:
            debug("touching goal")
            if t_site.is_empty():
                debug("touched goal site empty, build")
                if len(my_towers) < 3:
                    queen_command = "BUILD %s %s" % (touched_site, "TOWER")
                elif len(my_towers) < 2:
                    queen_command = "BUILD %s %s" % (touched_site, "TOWER")
                elif len(my_mines) < 2 and t_site.gold_remaining > 0:
                    queen_command = "BUILD %s %s" % (touched_site, "MINE")
                elif len(my_barracks) < 1 or my_income > 10:
                    queen_command = "BUILD %s %s" % (touched_site, "BARRACKS-KNIGHT")
                elif len(my_towers) < 3:
                    queen_command = "BUILD %s %s" % (touched_site, "TOWER")
                elif t_site.gold_remaining > 0:
                    queen_command = "BUILD %s %s" % (touched_site, "MINE")
                else:
                    queen_command = "BUILD %s %s" % (touched_site, "TOWER")
            else:
                debug("touched goal site is not empty")
                if t_site.is_friendly() and t_site.is_mine() and t_site.max_mine_size > t_site.param_1:
                    debug("upgrading mine")
                    queen_command = "BUILD %s %s" % (touched_site, "MINE")
                elif t_site.is_friendly() and t_site.is_tower() and t_site.param_1 < 250:
                    debug("upgrading tower")
                    queen_command = "BUILD %s %s" % (touched_site, "TOWER")
                else:
                    debug("cannot upgrade goal site, need new goal")
                    goal_site = get_new_goal_1()
                    if goal_site > -1:
                        debug("new goal set")
                        debug("goal_site = %s" % goal_site)
                        g_site = sites[goal_site]
                        # queen_command = "MOVE %s %s" % (g_site.x, g_site.y)
                        queen_command = generate_queen_move(g_site.x, g_site.y)
        elif touched_site > -1:
            debug("touched site (not goal) is not empty")
            if t_site.is_friendly() and t_site.is_mine() and t_site.max_mine_size > t_site.param_1:
                debug("upgrading mine")
                queen_command = "BUILD %s %s" % (touched_site, "MINE")
            elif t_site.is_friendly() and t_site.is_tower() and t_site.param_1 < 250:
                debug("upgrading tower")
                queen_command = "BUILD %s %s" % (touched_site, "TOWER")
            elif t_site.is_empty():
                debug("building tower")
                queen_command = "BUILD %s %s" % (touched_site, "TOWER")
            else:
                debug("cannot upgrade touched (non goal) site, moving on")
                if goal_site > -1:
                    g_site = sites[goal_site]
                    # queen_command = "MOVE %s %s" % (g_site.x, g_site.y)
                    queen_command = generate_queen_move(g_site.x, g_site.y)
        elif goal_site > -1:
            debug("has goal, not touching")
            g_site = sites[goal_site]
            # queen_command = "MOVE %s %s" % (g_site.x, g_site.y)
            queen_command = generate_queen_move(g_site.x, g_site.y)
        else:
            debug("needs goal")
            goal_site = get_new_goal_1()
            if goal_site > -1:
                debug("new goal set")
                g_site = sites[goal_site]
                # queen_command = "MOVE %s %s" % (g_site.x, g_site.y)
                queen_command = generate_queen_move(g_site.x, g_site.y)
            else:
                debug("error: could not set goal 12")
    else:
        debug("threat level 0")

        # todo: detect turtle - no other buildings but towers
        # - I have 2 barracks, and high income or the enemy has many towers
        # - check code from v2

        if goal_site == -1:
            debug("no goal set, setting goal")
            goal_site = get_new_goal()
            if goal_site > -1:
                debug("new goal set")
            else:
                debug("error: could not set goal 1")

        if touched_site > -1 and touched_site == goal_site:
            debug("touching goal")
            if t_site.is_empty():
                debug("touched goal site empty, build")
                if len(my_mines) < 2 and t_site.gold_remaining > 0:
                    queen_command = "BUILD %s %s" % (touched_site, "MINE")
                elif len(my_barracks) < 1 or (my_income > 10 and len(my_barracks) < 2):
                    queen_command = "BUILD %s %s" % (touched_site, "BARRACKS-KNIGHT")
                elif len(my_towers) < 3 and len(enemy_barracks) > 0:
                    queen_command = "BUILD %s %s" % (touched_site, "TOWER")
                elif t_site.gold_remaining > 0:
                    queen_command = "BUILD %s %s" % (touched_site, "MINE")
                else:
                    queen_command = "BUILD %s %s" % (touched_site, "TOWER")
            else:
                debug("touched goal site is not empty")
                if t_site.is_friendly() and t_site.is_mine() and t_site.max_mine_size > t_site.param_1:
                    debug("upgrading mine")
                    queen_command = "BUILD %s %s" % (touched_site, "MINE")
                elif t_site.is_friendly() and t_site.is_tower() and t_site.param_1 < 300:
                    debug("upgrading tower")
                    queen_command = "BUILD %s %s" % (touched_site, "TOWER")
                else:
                    debug("cannot upgrade goal site, need new goal")
                    goal_site = get_new_goal()
                    if goal_site > -1:
                        debug("new goal set %s" % goal_site)
                        g_site = sites[goal_site]
                        # queen_command = "MOVE %s %s" % (g_site.x, g_site.y)
                        queen_command = generate_queen_move(g_site.x, g_site.y)
        elif touched_site > -1:
            debug("touched site (not goal)")
            if t_site.is_friendly() and t_site.is_mine() and t_site.max_mine_size > t_site.param_1:
                debug("upgrading mine")
                queen_command = "BUILD %s %s" % (touched_site, "MINE")
            elif t_site.is_friendly() and t_site.is_tower() and t_site.param_1 < 300:
                debug("upgrading tower")
                queen_command = "BUILD %s %s" % (touched_site, "TOWER")
            elif t_site.is_empty():
                queen_command = "BUILD %s %s" % (touched_site, "TOWER")
            else:
                debug("cannot upgrade touched (non goal) site, moving on")
                if goal_site > -1:
                    g_site = sites[goal_site]
                    # queen_command = "MOVE %s %s" % (g_site.x, g_site.y)
                    queen_command = generate_queen_move(g_site.x, g_site.y)
        elif goal_site > -1:
            debug("has goal, not touching")
            g_site = sites[goal_site]
            # queen_command = "MOVE %s %s" % (g_site.x, g_site.y)
            queen_command = generate_queen_move(g_site.x, g_site.y)
        else:
            debug("needs goal")
            goal_site = get_new_goal()
            if goal_site > -1:
                debug("new goal set")
                g_site = sites[goal_site]
                # queen_command = "MOVE %s %s" % (g_site.x, g_site.y)
                queen_command = generate_queen_move(g_site.x, g_site.y)
            else:
                debug("error: could not set goal 2")

    # determine training commands, build from barracks closest to enemy first
    train_command = ""
    if len(my_barracks) > 0 and gold > len(my_barracks) * 80:
        barracks_near_enemy = {}
        for barracks in my_barracks:
            d = distance(enemy_queen.x, enemy_queen.y, barracks.x, barracks.y)
            barracks_near_enemy[d] = barracks

        sorted_barracks = OrderedDict(sorted(barracks_near_enemy.items(), key=lambda t: t[0]))

        for barracks in sorted_barracks.values():
            if barracks.param_2 == 2 and len(enemy_towers) > 0 and gold >= 140:
                train_command += str(barracks.site_id) + " "
                gold -= 140
            elif barracks.param_2 == 1 and len(enemy_units) > 1 and gold >= 100:
                train_command += str(barracks.site_id) + " "
                gold -= 100
            elif barracks.param_2 == 0 and gold >= 80: #and len(enemy_towers) < 3
                train_command += str(barracks.site_id) + " "
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
