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

# todo: snaffle x, y must be inside radius of wizard (consider radius = 0 on snaffle for pickup


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

    # todo: determine which wizard is closer to defend_goal, should only stop objects or push them away
    # todo: determine which wizard is closer to opponents goal, should use accio
    # todo: if distance to attack_goal is less than 1/2 of field width, that wizard is on offense
    wizard_on_offense = -1
    dist_to_attack_goal = {}
    for wizard in my_wizards.values():
        dist_to_attack_goal[wizard.calculate_distance_between(goal_attack)] = wizard

    wizard_on_offense = dist_to_attack_goal[min(dist_to_attack_goal.keys())]
    debug("offense %s" % wizard_on_offense)

    reserved_snaffles = {}
    for wizard in my_wizards.values():
        if wizard.has_snaffle():
            debug("wiz %s has snaffle" % wizard.id)
            print("THROW %s %s %s" % (goal_attack.x, goal_attack.y, 500))
        elif wizard.id == wizard_on_offense.id and my_magic > COST_ACCIO:
            debug("accio furthest snaffle")
            snaffles_by_distance = {}
            for snaffle in snaffles.values():
                snaffles_by_distance[goal_defend.calculate_distance_between(snaffle)] = snaffle

            far_snaffle = snaffles_by_distance[min(snaffles_by_distance.keys())]
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