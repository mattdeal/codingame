import sys
import math
from collections import OrderedDict


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


class Wizard(Point):
    def __init__(self, id, x, y, vx, vy, state):
        Point.__init__(self, x, y, 400)
        self.id = id
        self.vx = vx
        self.vy = vy
        self.state = state

    def has_snaffle(self):
        return self.state == 1


class Snaffle(Point):
    def __init__(self, id, x, y, vx, vy):
        Point.__init__(self, x, y, 150)
        self.id = id
        self.vx = vx
        self.vy = vy


class Bludger(Point):
    def __init__(self, id, x, y, vx, vy):
        Point.__init__(self, x, y, 200)
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
    entities = list(my_wizards.values()) + list(enemy_wizards.values())
    for foreign_entity in entities:
        if foreign_entity.id == start.id:
            continue
        if intersect_segment_circle(start, end, foreign_entity):
            obstacles.append(foreign_entity)

    for foreign_entity in snaffles.values():
        if foreign_entity.id == start.id:
            continue
        if intersect_segment_circle(start, end, foreign_entity):
            obstacles.append(foreign_entity)

    for foreign_entity in bludgers.values():
        if foreign_entity.id == start.id:
            continue
        if intersect_segment_circle(start, end, foreign_entity):
            obstacles.append(foreign_entity)

    return obstacles


# Grab Snaffles and try to throw them through the opponent's goal!
# Move towards a Snaffle and use your team id to determine where you need to throw it.

my_team_id = int(input())  # if 0 you need to score on the right of the map, if 1 you need to score on the left

# setup goals
goal_attack = None
goal_defend = None
goal_left = Point(0, 3750)
goal_right = Point(16000, 3750)

if my_team_id == 0:
    goal_attack = goal_right
    goal_defend = goal_left
else:
    goal_attack = goal_left
    goal_defend = goal_right

WIZARD = "WIZARD"
OPPONENT_WIZARD = "OPPONENT_WIZARD"
SNAFFLE = "SNAFFLE"
BLUDGER = "BLUDGER"

COST_OBLIVIATE = 5
COST_PETRIFICUS = 10
COST_ACCIO = 15
COST_FLIPENDO = 20

# game loop
while True:
    my_score, my_magic = [int(i) for i in input().split()]
    opponent_score, opponent_magic = [int(i) for i in input().split()]
    entities = int(input())  # number of entities still in game

    snaffles = {}
    my_wizards = {}
    enemy_wizards = {}
    bludgers = {}

    for i in range(entities):
        # entity_id: entity identifier
        # entity_type: "WIZARD", "OPPONENT_WIZARD" or "SNAFFLE" (or "BLUDGER" after first league)
        # x: position
        # y: position
        # vx: velocity
        # vy: velocity
        # state: 1 if the wizard is holding a Snaffle, 0 otherwise
        entity_id, entity_type, x, y, vx, vy, state = input().split()
        entity_id = int(entity_id)
        x = int(x)
        y = int(y)
        vx = int(vx)
        vy = int(vy)
        state = int(state)

        if entity_type == WIZARD:
            my_wizards[entity_id] = Wizard(entity_id, x, y, vx, vy, state)
        elif entity_type == OPPONENT_WIZARD:
            enemy_wizards[entity_id] = Wizard(entity_id, x, y, vx, vy, state)
        elif entity_type == SNAFFLE:
            snaffles[entity_id] = Snaffle(entity_id, x, y, vx, vy)
        elif entity_type == BLUDGER:
            bludgers[entity_id] = Bludger(entity_id, x, y, vx, vy)

    debug("magic %s" % my_magic)
    debug("my_score %s" % my_score)

    # todo: use flipendo if there is a line between wizard and goal with 0 objects in the way
    # todo: use petrificus if vx is high and the snaffle is headed towards our goal

    wizard_on_offense = -1
    dist_to_attack_goal = {}
    for wizard in my_wizards.values():
        dist_to_attack_goal[wizard.calculate_distance_between(goal_attack)] = wizard

    wizard_on_offense = dist_to_attack_goal[min(dist_to_attack_goal.keys())]
    debug("offense %s" % wizard_on_offense)

    flipendo_snaffle_id = -1
    snaffles_near_goal = {}
    for snaffle in snaffles.values():
        snaffles_near_goal[snaffle.calculate_distance_between(goal_attack)] = snaffle

    dist_to_goal_snaffle = OrderedDict(sorted(snaffles_near_goal.items(), key=lambda t: t[0]))
    for dist in dist_to_goal_snaffle.keys():
        if dist > 2000:
            t_snaffle = dist_to_goal_snaffle[dist]
            obstacles = obstacles_between(wizard_on_offense, goal_attack)
            if len(obstacles) == 1 and obstacles[0].id == t_snaffle.id:
                flipendo_snaffle_id = t_snaffle.id
                break

    # todo: stop snaffle about to enter our goal
    # todo: make sure it's going to go in the goal
    snaffles_to_stop = {}
    for snaffle in snaffles.values():
        if snaffle.calculate_distance_between(goal_defend) < abs(snaffle.vx) and len(obstacles_between(snaffle, goal_defend)) < 1:
            snaffles_to_stop[snaffle.id] = snaffle

    reserved_snaffles = {}
    for wizard in my_wizards.values():
        if 0 < len(snaffles_to_stop) > len(reserved_snaffles.keys()) and my_magic >= COST_PETRIFICUS:
            for snaffle in snaffles_to_stop.values():
                if snaffle.id not in reserved_snaffles.keys():
                    if len(snaffles) > 1:
                        reserved_snaffles[snaffle.id] = snaffle

                    debug("stopping shot %s %s %s %s" % (snaffle.x, snaffle.y, snaffle.vx, snaffle.vy))
                    my_magic -= COST_PETRIFICUS
                    print("PETRIFICUS %s" % snaffle.id)
                    break
        elif wizard.has_snaffle():
            debug("wiz %s has snaffle" % wizard.id)
            print("THROW %s %s %s" % (goal_attack.x, goal_attack.y, 500))
        elif wizard.id == wizard_on_offense.id and my_magic >= COST_FLIPENDO and flipendo_snaffle_id > -1:
            debug("take a shot")
            reserved_snaffles[flipendo_snaffle_id] = snaffles[flipendo_snaffle_id]
            my_magic -= COST_FLIPENDO
            print("FLIPENDO %s" % flipendo_snaffle_id)
        elif wizard.id == wizard_on_offense.id and my_magic >= COST_FLIPENDO + COST_ACCIO:
            snaffles_by_distance = {}
            for snaffle in snaffles.values():
                dist_to_def_goal = goal_defend.calculate_distance_between(snaffle)
                velocity_x = abs(snaffle.vx)
                if velocity_x > 500 and snaffle.id not in reserved_snaffles.keys():
                    dist_to_def_goal = -1000

                snaffles_by_distance[dist_to_def_goal] = snaffle

            far_snaffle = snaffles_by_distance[min(snaffles_by_distance.keys())]

            if abs(far_snaffle.vx) > 500:
                debug("stopping snaffle")
                reserved_snaffles[far_snaffle.id] = far_snaffle
                my_magic -= COST_PETRIFICUS
                print("PETRIFICUS %s" % far_snaffle.id)
            else:
                debug("accio furthest snaffle")
                reserved_snaffles[far_snaffle.id] = far_snaffle
                my_magic -= COST_ACCIO
                print("ACCIO %s" % far_snaffle.id)
        else:
            debug("wiz %s no snaffle" % wizard.id)
            play_d = True

            if len(snaffles) > 0:
                snaffles_by_distance = {}
                for snaffle in snaffles.values():
                    ignore_snaffle = False
                    if snaffle.id in reserved_snaffles.keys():
                        ignore_snaffle = True

                    if not ignore_snaffle:
                        for enemy in enemy_wizards.values():
                            if enemy.has_snaffle() and enemy.calculate_distance_between(snaffle) < wizard.radius:
                                debug("enemy %s has snaffle" % enemy.id)
                                ignore_snaffle = True
                                break

                    if not ignore_snaffle:
                        snaffles_by_distance[wizard.calculate_distance_between(snaffle)] = snaffle

                if len(snaffles_by_distance) > 0:
                    debug("snaffles exist")
                    dist_to_snaffle = min(snaffles_by_distance.keys())
                    closes_snaffle = snaffles_by_distance[dist_to_snaffle]
                    speed = 150
                    if dist_to_snaffle < 150:
                        speed = int(dist_to_snaffle) + 1

                    if len(snaffles) > 1:
                        reserved_snaffles[closes_snaffle.id] = closes_snaffle

                    print("MOVE %s %s %s" % (closes_snaffle.x, closes_snaffle.y, speed))
                    play_d = False

            if play_d:
                debug("play D")
                speed = 150
                distance_to_goal = wizard.calculate_distance_between(goal_defend)
                if distance_to_goal < 150:
                    speed = int(distance_to_goal) + 1

                print("MOVE %s %s %s" % (goal_defend.x, goal_defend.y, speed))


            # todo: find snaffles by distance that another wizard is not holding
            # todo: move to the nearest snaffle
            # todo: steal snaffle from other player?
            # todo: wizard stuff?

    # for i in range(2):

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)


        # Edit this line to indicate the action for each wizard (0 ≤ thrust ≤ 150, 0 ≤ power ≤ 500)
        # i.e.: "MOVE x y thrust" or "THROW x y power"
        # print("MOVE 8000 3750 100")