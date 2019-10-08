import sys
import math
import random

# Deliver more amadeusium to hq (left side of the map) than your opponent. Use radars to find amadeusium but beware of traps!

# helper methods
def debug(msg):
    print(str(msg), file=sys.stderr)

# height: size of the map
width, height = [int(i) for i in input().split()]

NONE = -1
ROBOT_ALLY = 0
ROBOT_ENEMY = 1
HOLE = 1
RADAR = 2
TRAP = 3
AMADEUSIUM = 4


class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, pos):
        return abs(self.x - pos.x) + abs(self.y - pos.y)

    def __str__(self):
        return f'({self.x},{self.y})'


class Entity(Pos):
    def __init__(self, x, y, type, id):
        super().__init__(x, y)
        self.type = type
        self.id = id


class Robot(Entity):
    def __init__(self, x, y, type, id, item):
        super().__init__(x, y, type, id)
        self.item = item

    def is_dead(self):
        return self.x == -1 and self.y == -1

    @staticmethod
    def move(x, y, message=""):
        print(f"MOVE {x} {y} {message}")

    @staticmethod
    def wait(message=""):
        print(f"WAIT {message}")

    @staticmethod
    def dig(x, y, message=""):
        print(f"DIG {x} {y} {message}")

    @staticmethod
    def request(requested_item, message=""):
        if requested_item == RADAR:
            print(f"REQUEST RADAR {message}")
        elif requested_item == TRAP:
            print(f"REQUEST TRAP {message}")
        else:
            raise Exception(f"Unknown item {requested_item}")


class Cell(Pos):
    def __init__(self, x, y, amadeusium, hole):
        super().__init__(x, y)
        self.amadeusium = amadeusium
        self.hole = hole

    def has_hole(self):
        return self.hole == HOLE

    def update(self, amadeusium, hole):
        self.amadeusium = amadeusium
        self.hole = hole


class Grid:
    def __init__(self):
        self.cells = []
        for y in range(height):
            for x in range(width):
                self.cells.append(Cell(x, y, 0, 0))

    def get_cell(self, x, y):
        if width > x >= 0 and height > y >= 0:
            return self.cells[x + width * y]
        return None


class Game:
    def __init__(self):
        self.grid = Grid()
        self.my_score = 0
        self.enemy_score = 0
        self.radar_cooldown = 0
        self.trap_cooldown = 0
        self.radars = []
        self.traps = []
        self.my_robots = []
        self.enemy_robots = []
        self.assignments = {}
        self.destinations = {}
        self.turn_number = 0

    def update(self):
        # my_score: Players score
        self.my_score, self.enemy_score = [int(i) for i in input().split()]

        # increment turn number
        self.turn_number+=1

        # debug(f'my_score {game.my_score}, opp_score {game.enemy_score}')

        for i in range(height):
            inputs = input().split()
            for j in range(width):
                # amadeusium: amount of amadeusium or "?" if unknown
                # hole: 1 if cell has a hole
                amadeusium = inputs[2 * j]
                hole = int(inputs[2 * j + 1])
                self.grid.get_cell(j, i).update(amadeusium, hole)

        # debug(game.grid)

        # entity_count: number of entities visible to you
        # radar_cooldown: turns left until a new radar can be requested
        # trap_cooldown: turns left until a new trap can be requested
        entity_count, self.radar_cooldown, self.trap_cooldown = [int(i) for i in input().split()]

        debug(f'ent_count {entity_count}, rad_cd {self.radar_cooldown}, trap_cd {self.trap_cooldown}')

        self.reset()

        for i in range(entity_count):
            # id: unique id of the entity
            # type: 0 for your robot, 1 for other robot, 2 for radar, 3 for trap
            # y: position of the entity
            # item: if this entity is a robot, the item it is carrying (-1 for NONE, 2 for RADAR, 3 for TRAP, 4 for AMADEUSIUM)
            id, type, x, y, item = [int(j) for j in input().split()]

            # debug(f'id {id}, type {type}, x {x}, y {y}, item {item}')

            if type == ROBOT_ALLY:
                self.my_robots.append(Robot(x, y, type, id, item))
            elif type == ROBOT_ENEMY:
                self.enemy_robots.append(Robot(x, y, type, id, item))
            elif type == TRAP:
                self.traps.append(Entity(x, y, type, id))
                debug(f'TRAP at {x}, {y}')
            elif type == RADAR:
                self.radars.append(Entity(x, y, type, id))

    def reset(self):
        self.radars = []
        self.traps = []
        self.my_robots = []
        self.enemy_robots = []

    def output(self):
        for robot in self.my_robots:
            assignment = self.assignments.get(robot.id)
            if assignment is None:
                robot.wait(f'no assignment {robot.id}')
            elif assignment == 'RADAR_GET':
                robot.request(RADAR, 'gimme dat')
            elif assignment == 'TRAP_GET':
                robot.request(TRAP, 'gimme dat')
            elif assignment == 'RADAR_USE':
                if robot.distance(self.destinations.get(robot.id)) < 1:
                    robot.dig(robot.x, robot.y, 'deploy!')
                    self.assignments[robot.id] = None
                    self.destinations[robot.id] = None
                else:
                    robot.move(self.destinations.get(robot.id).x, self.destinations.get(robot.id).y, 'omw to rad loc')
            elif assignment == 'TRAP_USE':
                if robot.distance(self.destinations.get(robot.id)) < 1:
                    robot.dig(robot.x, robot.y, 'deploy!')
                    self.assignments[robot.id] = None
                    self.destinations[robot.id] = None
                else:
                    robot.move(self.destinations.get(robot.id).x, self.destinations.get(robot.id).y, 'omw to trap loc')
            elif assignment == 'COLLECT':
                dest = self.destinations[robot.id]
                dist = robot.distance(dest)
                if dist < 2:
                    robot.dig(dest.x, dest.y, 'diggy diggy hole')
                    self.destinations[robot.id] = None
                    self.assignments[robot.id] = None
                else:
                    robot.move(dest.x, dest.y, 'omw to dig')
            elif assignment == 'RETURN':
                robot.move(self.destinations.get(robot.id).x, self.destinations.get(robot.id).y, 'omw home')
            else:
                robot.wait(f'wait {robot.id}')

    def build_output(self):
        self.job_clear_complete()

        self.job_radar_get()
        self.job_radar_use()

        self.job_trap_get()
        self.job_trap_use()

        self.job_return()
        self.job_collect()

    # request a trap
    def job_trap_get(self):
        if self.trap_cooldown > 0:
            debug('trap not available')
            return

        if self.get_trap_position() is None:
            debug('no valid trap positions found')
            return

        debug('trap available')
        for robot in self.my_robots:
            if self.assignments.get(robot.id) is None and robot.x == 0:
                debug(f'{robot.id} claimed trap')
                self.assignments[robot.id] = 'TRAP_GET'
                self.trap_cooldown = 4;
                return

    # find a location with ore and plant a bomb there
    def job_trap_use(self):
        for robot in self.my_robots:
            if robot.item == TRAP:
                debug(f'robot {robot.id} has trap')
                if robot.x == 0:
                    debug(f'robot {robot.id} at base')
                    self.assignments[robot.id] = 'TRAP_USE'
                    self.destinations[robot.id] = self.get_trap_position()
                else:
                    debug(f'robot {robot.id} moving to {self.destinations.get(robot.id)}')
                return

    # clear jobs for robots at base
    # todo: clear jobs for robots that can no longer harvest
    def job_clear_complete(self):
        for robot in self.my_robots:
            if robot.x == 0:
                self.assignments[robot.id] = None
                self.destinations[robot.id] = None
                continue

            job = self.assignments[robot.id]
            if job is None:
                continue

            dest = self.destinations[robot.id]
            if dest is None:
                continue

            if job == 'COLLECT':
                if self.grid.get_cell(dest.x, dest.y).amadeusium in ['0', '?']:
                    debug(f'robot {robot.id} cannot complete job, clearing')
                    self.assignments[robot.id] = None
                    self.destinations[robot.id] = None
                    continue

    # Direct robot carrying radar to a valid location
    def job_radar_use(self):
        for robot in self.my_robots:
            if robot.item == RADAR:
                debug(f'robot {robot.id} has radar')
                if robot.x == 0:
                    debug(f'robot {robot.id} at base')
                    self.assignments[robot.id] = 'RADAR_USE'
                    self.destinations[robot.id] = self.get_radar_position()
                else:
                    debug(f'robot {robot.id} moving to {self.destinations.get(robot.id)}')
                return

    # Get a position for radar
    def get_radar_position(self):
        if self.radars is None or len(self.radars) == 0:
            debug('no radars')
            return radar_locations[0]

        for location in radar_locations:
            debug(f'location {location.x}, {location.y}')
            valid = True

            for radar in self.radars:
                debug(f' - eval radar {radar.x}, {radar.y}')
                if radar.x == location.x and radar.y == location.y:
                    valid = False
                    break

            if valid:
                debug(f'radar location {location.x}, {location.y}')
                return location

    # Get a position for trap
    def get_trap_position(self):
        if self.traps is None or len(self.traps) == 0:
            debug('no traps')
            return Pos(15, 7)

        ore_by_distance = {}
        trap_bot = None

        for y in range(height):
            for x in range(width):
                cell = self.grid.get_cell(x, y)
                if cell.amadeusium == '?' or cell.amadeusium == '0':
                    continue

                # debug(cell.amadeusium)

                for robot in self.my_robots:
                    if robot.item != TRAP:
                        continue

                    trap_bot = robot.id

                    dist = cell.distance(robot)
                    if ore_by_distance.get(robot.id) is None:
                        ore_by_distance[robot.id] = {}

                    ore_by_distance[robot.id][dist] = cell

        debug(f'trap calc ore_by_distance {len(ore_by_distance)}')

        trap_pos = Pos(random.randint(5, 25), random.randint(5, 10))

        if len(ore_by_distance) > 0:
            trap_pos = ore_by_distance[trap_bot][max(ore_by_distance[trap_bot].keys())]

        while True:
            valid = True
            for trap in self.traps:
                if trap.x == trap_pos.x and trap.y == trap_pos.y:
                    debug(f'invalid trap position, recalculating')
                    valid = False
                    break

            if valid:
                break
            else:
                trap_pos = Pos(random.randint(5, 25), random.randint(5, 10))

        debug(f'trap_pos {trap_pos}')
        return trap_pos

    # Find robots with ore, and order them home
    def job_return(self):
        for robot in self.my_robots:
            if robot.item == AMADEUSIUM:
                self.assignments[robot.id] = 'RETURN'
                self.destinations[robot.id] = Pos(0, robot.y)

    # todo: collect job
    # - iterate through grid
    # - if ore, find distance to all bots with gather
    # - store min distance per bot to ore
    # - assign bot to closest ore that is not claimed
    def job_collect(self):
        ore_by_distance = {}

        for y in range(height):
            for x in range(width):
                cell = self.grid.get_cell(x, y)
                if cell.amadeusium == '?' or cell.amadeusium == '0':
                    continue

                # debug(cell.amadeusium)

                for robot in self.my_robots:
                    if self.assignments.get(robot.id) is not None:
                        continue

                    # todo: find closest robot to this cell
                    dist = cell.distance(robot)
                    if ore_by_distance.get(robot.id) is None:
                        ore_by_distance[robot.id] = {}

                    ore_by_distance[robot.id][dist] = cell

        debug(ore_by_distance)

        for robot in self.my_robots:
            # if robot.item is not None and robot.item > -1:
            #     debug(f'robot {robot.id} is carying {robot.item}')
            #     continue

            if self.assignments[robot.id] in ['RADAR_GET', 'RADAR_USE']:
                debug(f'robot {robot.id} already has job')
                continue

            if ore_by_distance.get(robot.id) is None:
                if self.turn_number < 2:
                    debug(f'eval robot {robot.id}, no moves found, moving to middle of field')
                    self.destinations[robot.id] = Pos(robot.x + 10, robot.y)
                    self.assignments[robot.id] = 'COLLECT'

                continue

            debug(f'eval robot {robot.id}')

            options = ore_by_distance[robot.id]

            for d in sorted(options.keys()):
                cell = options[d]
                for trap in self.traps:
                    if cell.x == trap.x and cell.y == trap.y:
                        debug(f'cell {cell.x}, {cell.y} is trap, ignoring')
                        continue

                debug(f'dist {d}, cell {cell.x}, {cell.y}')
                valid_destination = True

                for destination in self.destinations.values():
                    if destination is None:
                        continue

                    if cell.x == destination.x and cell.y == destination.y:
                        valid_destination = False
                        break

                if not valid_destination:
                    debug('- invalid, already assigned')
                    continue

                debug(f'assigned robot {robot.id} collect {cell.x}, {cell.y}')
                self.destinations[robot.id] = Pos(cell.x, cell.y)
                self.assignments[robot.id] = 'COLLECT'
                break

        # If radar is available, assign the first available robot at base to request a radar

    def job_radar_get(self):
        if self.radar_cooldown > 0:
            debug('radar not available')
            return

        if self.get_radar_position() is None:
            debug('no valid radar positions found')
            return

        # if len(self.radars) > 9:
        #     debug('radars are not needed')
        #     return

        debug('radar available')
        for robot in self.my_robots:
            if self.assignments.get(robot.id) is None and robot.x == 0:
                debug(f'{robot.id} claimed radar')
                self.assignments[robot.id] = 'RADAR_GET'
                self.radar_cooldown = 4;
                return

game = Game()

radar_locations = [
    Pos(9, 7),
    Pos(5, 3),
    Pos(5, 11),
    Pos(13, 3),
    Pos(13, 11),
    Pos(17, 7),
    Pos(21, 3),
    Pos(21, 11),
    Pos(25, 7),
    Pos(29, 3),
    Pos(29, 11)
]

# game loop
while True:
    game.update()
    game.build_output()
    game.output()


