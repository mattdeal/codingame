import sys
import math


class Point:
    def __init__(self, x, y, r=1):
        self.x = x
        self.y = y
        self.radius = r

    def __str__(self):
        return "x=%s, y=%s, r=%s" % (self.x, self.y, self.radius)

    def calculate_distance_between(self, target):
        """
        Calculates the distance between this object and the target.

        :param Entity target: The target to get distance to.
        :return: distance
        :rtype: float
        """
        return math.sqrt((target.x - self.x) ** 2 + (target.y - self.y) ** 2)

    def calculate_angle_between(self, target):
        """
        Calculates the angle between this object and the target in degrees.

        :param Entity target: The target to get the angle between.
        :return: Angle between entities in degrees
        :rtype: float
        """
        return math.degrees(math.atan2(target.y - self.y, target.x - self.x)) % 360

    def closest_point_to(self, target, min_distance=0):
        """
        Find the closest point to the given ship near the given target, outside its given radius,
        with an added fudge of min_distance.

        :param Entity target: The target to compare against
        :param int min_distance: Minimum distance specified from the object's outer radius
        :return: The closest point's coordinates
        :rtype: Position
        """
        angle = target.calculate_angle_between(self)
        radius = target.radius + min_distance
        x = target.x + radius * math.cos(math.radians(angle))
        y = target.y + radius * math.sin(math.radians(angle))

        return Point(x, y)

    def closest_point_inside_target(self, target):
        return self.closest_point_to(target, -self.radius)


class Reaper(Point):
    def __init__(self, id, x, y, radius, vx, vy):
        Point.__init__(self, x, y, radius)
        self.id = id
        self.vx = vx
        self.vy = vy


class Doof(Point):
    def __init__(self, id, x, y, radius, vx, vy):
        Point.__init__(self, x, y, radius)
        self.id = id
        self.vx = vx
        self.vy = vy


class Wreck(Point):
    def __init__(self, id, x, y, radius, vx, vy, water):
        Point.__init__(self, x, y, radius)
        self.id = id
        self.vx = vx
        self.vy = vy
        self.water = water


class Hazard(Point):
    def __init__(self, id, x, y, radius, vx, vy, time_remaining):
        Point.__init__(self, x, y, radius)
        self.id = id
        self.vx = vx
        self.vy = vy
        self.time_remaining = time_remaining


class Tanker(Point):
    def __init__(self, id, x, y, radius, vx, vy, water, capacity):
        Point.__init__(self, x, y, radius)
        self.id = id
        self.vx = vx
        self.vy = vy
        self.water = water
        self.capacity = capacity


class Destroyer(Point):
    def __init__(self, id, x, y, radius, vx, vy):
        Point.__init__(self, x, y, radius)
        self.id = id
        self.vx = vx
        self.vy = vy


# helper methods
def debug(msg):
    print(str(msg), file=sys.stderr)


def intersect_segment_circle(start, end, circle, *, fudge=0.5):
    """
    Test whether a line segment and circle intersect.

    :param Entity start: The start of the line segment. (Needs x, y attributes)
    :param Entity end: The end of the line segment. (Needs x, y attributes)
    :param Entity circle: The circle to test against. (Needs x, y, r attributes)
    :param float fudge: A fudge factor; additional distance to leave between the segment and circle. (Probably set this to the ship radius, 0.5.)
    :return: True if intersects, False otherwise
    :rtype: bool
    """
    # Derived with SymPy
    # Parameterize the segment as start + t * (end - start),
    # and substitute into the equation of a circle
    # Solve for t
    dx = end.x - start.x
    dy = end.y - start.y

    a = dx ** 2 + dy ** 2
    b = -2 * (start.x ** 2 - start.x * end.x - start.x * circle.x + end.x * circle.x +
              start.y ** 2 - start.y * end.y - start.y * circle.y + end.y * circle.y)
    c = (start.x - circle.x) ** 2 + (start.y - circle.y) ** 2

    if a == 0.0:
        # Start and end are the same point
        return start.calculate_distance_between(circle) <= circle.radius + fudge

    # Time along segment when closest to the circle (vertex of the quadratic)
    t = min(-b / (2 * a), 1.0)
    if t < 0:
        return False

    closest_x = start.x + dx * t
    closest_y = start.y + dy * t
    closest_distance = Point(closest_x, closest_y).calculate_distance_between(circle)

    return closest_distance <= circle.radius + fudge


def obstacles_between(start, end):
    """
    Check whether there is a straight-line path to the given point, without planetary obstacles in between.

    :param entity.Ship ship: Source entity
    :param entity.Entity target: Target entity
    :param entity.Entity ignore: Which entity type to ignore
    :return: The list of obstacles between the ship and target
    :rtype: list[entity.Entity]
    """
    obstacles = []
    entities = list(enemy_reapers.values()) +  \
               list(enemy_destroyers.values()) + list(tankers.values()) + \
               list(enemy_doofs.values())
    for foreign_entity in entities:
        if foreign_entity.id == start.id:
            continue
        if intersect_segment_circle(start, end, foreign_entity):
            obstacles.append(foreign_entity)

    return obstacles


def reaper_v2():
    if my_rage > 30:
        debug("reaper skill")
    else:
        debug("reaper default")


def destroyer_v2():
    if my_rage > 60:
        debug("destroyer skill")
    else:
        debug("destroyer default")


def doof_v2():
    if my_rage > 30:
        debug("doof skill")
    else:
        debug("doof default")


REAPER = 0
DESTROYER = 1
DOOF = 2
TANKER = 3
WRECK = 4
TAR = 5
OIL = 6

# todo: mass

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

# game loop
while True:
    enemy_reapers = {}
    enemy_destroyers = {}
    enemy_doofs = {}

    wrecks = {}
    tankers = {}
    oils = {}
    tars = {}

    my_reaper = None
    my_destroyer = None
    my_doof = None

    my_score = int(input())
    enemy_score_1 = int(input())
    enemy_score_2 = int(input())
    my_rage = int(input())
    enemy_rage_1 = int(input())
    enemy_rage_2 = int(input())
    unit_count = int(input())
    for i in range(unit_count):
        unit_id, unit_type, player, mass, radius, x, y, vx, vy, extra, extra_2 = input().split()
        unit_id = int(unit_id)
        unit_type = int(unit_type)
        player = int(player)
        mass = float(mass)
        radius = int(radius)
        x = int(x)
        y = int(y)
        vx = int(vx)
        vy = int(vy)
        extra = int(extra)
        extra_2 = int(extra_2)

        if unit_type == REAPER:
            if player == 0:
                my_reaper = Reaper(unit_id, x, y, radius, vx, vy)
            else:
                enemy_reapers[unit_id] = Reaper(unit_id, x, y, radius, vx, vy)
        elif unit_type == DESTROYER:
            if player == 0:
                my_destroyer = Destroyer(unit_id, x, y, radius, vx, vy)
            else:
                enemy_destroyers[unit_id] = Destroyer(unit_id, x, y, radius, vx, vy)
        elif unit_type == DOOF:
            if player == 0:
                my_doof = Doof(unit_id, x, y, radius, vx, vy)
            else:
                enemy_doofs[unit_id] = Doof(unit_id, x, y, radius, vx, vy)
        elif unit_type == WRECK and extra > 0:
            wrecks[unit_id] = Wreck(unit_id, x, y, radius, vx, vy, extra)
        elif unit_type == TANKER and extra > 0:
            tankers[unit_id] = Tanker(unit_id, x, y, radius, vx, vy, extra, extra_2)
        elif unit_type == TAR:
            tars[unit_id] = Hazard(unit_id, x, y, radius, vx, vy, extra)
        elif unit_type == OIL:
            oils[unit_id] = Hazard(unit_id, x, y, radius, vx, vy, extra)

    # calculate values of all wrecks
    wrecks_by_value = {}
    for wreck in wrecks.values():
        # water value
        water_value = wreck.water

        # water value nearby
        # todo: combine overlaping areas into higher value targets
        # If two wrecks are covering each other, remove them and create a new one whose content is their sum. Place the new wreck in the merging area. This makes the reaper goes on areas where he might be able to fetch 2 of water at once.
        for wreck_nearby in wrecks.values():
            if wreck.id == wreck_nearby.id:
                continue

            if wreck.calculate_distance_between(wreck_nearby) < 100:
                water_value += wreck_nearby.water

        # distance to my_reaper
        dist_to_reaper = my_reaper.calculate_distance_between(wreck)

        # closest reaper
        my_reaper_closest = True
        for reaper in enemy_reapers.values():
            if reaper.calculate_distance_between(wreck) < dist_to_reaper:
                my_reaper_closest = False

        # objects between
        # todo: possibly change this to check for a larger vehicle inside the wreck
        objects_between = obstacles_between(my_reaper, wreck)

        # check for oil
        is_in_oil = False
        for oil in oils.values():
            if wreck.calculate_distance_between(wreck.closest_point_to(oil)) < wreck.radius:
                is_in_oil = True

        # calculate wreck value
        wreck_value = water_value * 1000
        wreck_value -= dist_to_reaper

        if len(objects_between) > 0:
            wreck_value -= 10000

        if my_reaper_closest:
            wreck_value += 5000
        else:
            wreck_value -= 5000

        if is_in_oil:
            wreck_value -= 50000

        wrecks_by_value[wreck_value] = wreck
        debug("wreck %s : value %s" % (wreck.id, wreck_value))

    # get target wreck
    target_wreck = None
    if len(wrecks_by_value) > 0:
        target_wreck = wrecks_by_value[max(wrecks_by_value.keys())]

    #  calculate values of all tankers
    tankers_by_value = {}
    for tanker in tankers.values():
        # distance to center
        dist_from_center = tanker.calculate_distance_between(Point(0, 0))
        if dist_from_center > 6000:
            continue

        # water value
        water_value = tanker.water
        for tanker_nearby in tankers.values():
            if tanker.id == tanker_nearby.id:
                continue

            if tanker.calculate_distance_between(tanker_nearby) < 500:
                water_value += tanker_nearby.water

        # distance to my_reaper
        dist_to_reaper = my_reaper.calculate_distance_between(tanker)

        # closest reaper
        my_reaper_closest = True
        for reaper in enemy_reapers.values():
            if reaper.calculate_distance_between(tanker) < dist_to_reaper:
                my_reaper_closest = False

        tanker_value = water_value * 1000
        tanker_value -= dist_to_reaper

        if my_reaper_closest:
            tanker_value += 5000
        else:
            tanker_value -= 5000

        tankers_by_value[tanker_value] = tanker
        debug("tanker %s : value %s" % (tanker.id, tanker_value))

    target_tanker = None
    if len(tankers_by_value) > 0:
        target_tanker = tankers_by_value[max(tankers_by_value.keys())]

    # calculate targets for skills
    # oil target
    oil_target = None
    if len(wrecks_by_value) > 2:
        oil_target = wrecks_by_value[min(wrecks_by_value.keys())]
        for oil in oils.values():
            if oil.calculate_distance_between(oil_target.closest_point_to(oil)) < oil_target.radius:
                oil_target = None

    # grenade target
    grenade_target = None
    if len(wrecks_by_value) > 2:
        grenade_targets = {}
        for wreck in wrecks_by_value.values():
            dist_to_enemy_reaper = 0
            for reaper in enemy_reapers.values():
                dist_to_enemy_reaper += reaper.calculate_distance_between(wreck)

            if dist_to_enemy_reaper < 2000:
                grenade_targets[dist_to_enemy_reaper] = wreck

        if len(grenade_targets) > 0:
            grenade_target = grenade_targets[min(grenade_targets.keys())]

    # todo: temporary commands

    # reaper
    if target_wreck is not None:
        distance_to_wreck = my_reaper.calculate_distance_between(target_wreck)
        throttle = 300
        if distance_to_wreck < throttle:
            throttle = int(distance_to_wreck)
        print("%s %s %s" % (target_wreck.x, target_wreck.y, throttle))
    else:
        print("WAIT")

    # destroyer
    if grenade_target is not None and my_rage > 60 and my_destroyer.calculate_distance_between(grenade_target) < 2000:
        print("SKILL %s %s GRENAAAAADE" % (grenade_target.x, grenade_target.y))
        my_rage -= 60
    elif target_tanker is not None:
        distance_to_tanker = my_destroyer.calculate_distance_between(target_tanker)
        throttle = 300
        print("%s %s %s" % (target_tanker.x, target_tanker.y, throttle))
    else:
        print("WAIT")

    # doof
    if oil_target is not None and my_rage > 30 and my_doof.calculate_distance_between(oil_target) < 2000:
        print("SKILL %s %s OILLLLLL" % (oil_target.x, oil_target.y))
        my_rage -= 30
    elif enemy_score_1 > enemy_score_2:
        target_enemy = enemy_reapers[min(enemy_reapers.keys())]
        distance_to_target = my_doof.calculate_distance_between(target_enemy)
        throttle = 300
        print("%s %s %s" % (target_enemy.x, target_enemy.y, throttle))
    else:
        target_enemy = enemy_reapers[max(enemy_reapers.keys())]
        distance_to_target = my_doof.calculate_distance_between(target_enemy)
        throttle = 300
        print("%s %s %s" % (target_enemy.x, target_enemy.y, throttle))

    # todo: determine the order of these commands
    # reaper_command = reaper_v2()
    # destroyer_command = destroyer_v2()
    # doof_command = doof_v2()
    #
    # print(reaper_command)
    # print(destroyer_command)
    # print(doof_command)
