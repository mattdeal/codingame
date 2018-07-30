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

    a = dx**2 + dy**2
    b = -2 * (start.x**2 - start.x*end.x - start.x*circle.x + end.x*circle.x +
              start.y**2 - start.y*end.y - start.y*circle.y + end.y*circle.y)
    c = (start.x - circle.x)**2 + (start.y - circle.y)**2

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
    entities = list(my_reapers.values()) + list(enemy_reapers.values()) + list(my_destroyers.values()) + \
               list(enemy_reapers.values()) + list(tankers.values()) + list(my_doofs.values()) + \
               list(enemy_doofs.values())
    for foreign_entity in entities:
        if foreign_entity.id == start.id:
            continue
        if intersect_segment_circle(start, end, foreign_entity):
            obstacles.append(foreign_entity)

    return obstacles


def destroyer_default():
    tankers_by_distance = {}
    for tanker in tankers.values():
        if tanker.water < 2:
            continue

        # ignore tankers that are outside of the bowl
        dist = tanker.calculate_distance_between(Point(0, 0))
        if dist > 6000:
            continue

        tankers_by_distance[destroyer.calculate_distance_between(tanker)] = tanker

    if len(tankers_by_distance) > 0:
        min_distance_to_tanker = min(tankers_by_distance.keys())
        closest_tanker = tankers_by_distance[min_distance_to_tanker]
        throttle = 300
        # todo determine if throttle needs adjustment
        print("%s %s %s" % (closest_tanker.x, closest_tanker.y, throttle))
    else:
        print("WAIT")


REAPER = 0
DESTROYER = 1
DOOF = 2
TANKER = 3
WRECK = 4

# todo: mass

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

# game loop
while True:
    my_reapers = {}
    enemy_reapers = {}
    my_destroyers = {}
    enemy_destroyers = {}
    my_doofs = {}
    enemy_doofs = {}

    wrecks = {}
    tankers = {}

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
                my_reapers[unit_id] = Reaper(unit_id, x, y, radius, vx, vy)
            else:
                enemy_reapers[unit_id] = Reaper(unit_id, x, y, radius, vx, vy)
        elif unit_type == DESTROYER:
            if player == 0:
                my_destroyers[unit_id] = Destroyer(unit_id, x, y, radius, vx, vy)
            else:
                enemy_destroyers[unit_id] = Destroyer(unit_id, x, y, radius, vx, vy)
        elif unit_type == DOOF:
            if player == 0:
                my_doofs[unit_id] = Doof(unit_id, x, y, radius, vx, vy)
            else:
                enemy_doofs[unit_id] = Doof(unit_id, x, y, radius, vx, vy)
        elif unit_type == WRECK and extra > 0:
            wrecks[unit_id] = Wreck(unit_id, x, y, radius, vx, vy, extra)
        elif unit_type == TANKER and extra > 0:
            tankers[unit_id] = Tanker(unit_id, x, y, radius, vx, vy, extra, extra_2)

    # todo: reaper v2
    # todo: destroyer v2
    # todo: doof v2

    # todo reaper default command
    # todo reaper skill command
    for reaper in my_reapers.values():
        # check for wrecks
        if len(wrecks) > 0:
            wrecks_by_value = {}
            for wreck in wrecks.values():
                nearby_enemies = 0

                for enemy in enemy_reapers.values():
                    if enemy.calculate_distance_between(wreck) < 300:
                        nearby_enemies += 1

                for enemy in enemy_doofs.values():
                    if enemy.calculate_distance_between(wreck) < 300:
                        nearby_enemies += 1

                for enemy in enemy_destroyers.values():
                    if enemy.calculate_distance_between(wreck) < 300:
                        nearby_enemies += 1

                enemies_between = obstacles_between(reaper, wreck)
                dist_to_wreck = reaper.calculate_distance_between(wreck)
                dist_from_destroyer = min(my_destroyers.values()).calculate_distance_between(wreck)
                water_value = wreck.water * 100
                enemy_value = (nearby_enemies + len(enemies_between)) * 100

                wreck_value = dist_to_wreck + dist_from_destroyer + enemy_value - water_value

                wrecks_by_value[wreck_value] = wreck

            best_wreck = min(wrecks_by_value.keys())
            closest_wreck = wrecks_by_value[best_wreck]
            distance_to_wreck = reaper.calculate_distance_between(closest_wreck)

            throttle = 300
            if throttle > distance_to_wreck:
                throttle = int(distance_to_wreck)

            if closest_wreck is not None:
                print("%s %s %s" % (closest_wreck.x, closest_wreck.y, throttle))
            else:
                print("WAIT")
        else:
            print("WAIT")

    #  destroyer command
    for destroyer in my_destroyers.values():
        # find grenade target
        if my_rage > 60 and len(wrecks) > 0:
            wrecks_by_value = {}
            for wreck in wrecks.values():
                # ignore wrecks out of range
                dist = destroyer.calculate_distance_between(wreck)
                if dist > 2000:
                    continue

                # ignore wrecks where my reaper is close
                dist = my_reapers[min(my_reapers.keys())].calculate_distance_between(wreck)
                if dist < 1000:
                    continue

                wrecks_by_value[dist] = wreck

            # find wreck within 2000
            if len(wrecks_by_value) > 0:
                grenade_targets = {}
                for wreck in wrecks_by_value.values():
                    # find reaper to bomb
                    for reaper in enemy_reapers.values():
                        dist = reaper.calculate_distance_between(wreck)
                        # ignore reapers outside of grenade radius
                        if dist > 1000:
                            continue

                        grenade_targets[dist] = reaper

                if len(grenade_targets) > 0:
                    target = grenade_targets[min(grenade_targets.keys())]
                    print("SKILL %s %s" % (target.x, target.y))
                    my_rage -= 60
                else:
                    destroyer_default()
            else:
                destroyer_default()
        elif len(tankers) > 0:
            destroyer_default()
        else:
            print("WAIT")

    # todo: doof default command
    # todo: doof skill command
    for doof in my_doofs.values():
        if len(enemy_reapers) > 0:
            reapers_by_distance = {}
            for reaper in enemy_reapers.values():
                reapers_by_distance[doof.calculate_distance_between(reaper)] = reaper

            min_distance_to_reaper = min(reapers_by_distance.keys())
            closest_reaper = reapers_by_distance[min_distance_to_reaper]

            throttle = 300
            #todo: determine if lower speed is necessary

            if closest_reaper is not None:
                print("%s %s %s" % (closest_reaper.x, closest_reaper.y, throttle))
            else:
                print("WAIT")
