import sys
import math

# MAP SIZE
WIDTH = 12
HEIGHT = 12

# OWNER
ME = 0
OPPONENT = 1

# BUILDING TYPE
HQ = 0


# manhattan distance formula
def distance_between(p1, p2):
    return abs(p1.x - p2.x) + abs(p1.y - p2.y)


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Unit:
    def __init__(self, owner, id, level, x, y):
        self.owner = owner
        self.id = id
        self.level = level
        self.pos = Position(x, y)


class Building:
    def __init__(self, owner, type, x, y):
        self.owner = owner
        self.type = type
        self.pos = Position(x, y)


class Game:
    def __init__(self):
        self.buildings = []
        self.units = []
        self.actions = []
        self.gold = 0
        self.income = 0
        self.opponent_gold = 0
        self.opponent_income = 0
        self.turn = 0
        self.upkeep = 0
        self.tiles = []
        self.farthest_unit_position = None

    def get_my_HQ(self):
        for b in self.buildings:
            if b.type == HQ and b.owner == ME:
                return b

    def get_opponent_HQ(self):
        for b in self.buildings:
            if b.type == HQ and b.owner == OPPONENT:
                return b

    def move_units(self):
        target = Position(11, 11)
        hq = self.get_my_HQ()
        mod = -1

        if hq.pos.x > 0:
            target = Position(0, 0)
            mod = 1

        # todo: logic per level
        # todo: level 3, charge base
        # todo: level 2, defend base
        # todo: level 1, move to nearest unclaimed space
        # todo: track cells I am already moving towards

        for unit in self.units:
            if unit.owner == ME:
                # todo: lvl 3 units need to prioritize opposing player's active/occupied tiles
                # todo: check for enemy hq in positions, if we can move there, do it
                # todo: lvl 1 units need to avoid trying to move into active/occupied enemy tiles
                # todo: possibly move up and to the right first to counter the default movement patterns
                potential_targets = []
                potential_targets.append(Position(unit.pos.x, unit.pos.y + mod))
                potential_targets.append(Position(unit.pos.x + mod, unit.pos.y))
                potential_targets.append(Position(unit.pos.x - mod, unit.pos.y))
                potential_targets.append(Position(unit.pos.x, unit.pos.y - mod))

                for position in potential_targets:
                    if position.x < 0 or position.x > 11:
                        continue
                    if position.y < 0 or position.y > 11:
                        continue
                    if self.tiles[position.y][position.x] in ['.', 'x', 'o', 'X']:
                        target = position
                        break

                self.actions.append(f'MOVE {unit.id} {target.x} {target.y}')

    def get_train_position(self):
        # todo: make sure the position is valid, not #
        # todo: consider positions farther from home

        hq = self.get_my_HQ()

        if hq.pos.x == 0:
            return Position(0, 1)
        return Position(10, 10)

    def get_farthest_unit_position(self):
        if self.farthest_unit_position is None:
            return None

        farthest_unit_distance = 0
        hq = self.get_my_HQ()

        for unit in self.units:
            if unit.owner == ME:
                distance_from_hq = distance_between(hq.pos, unit.pos)
                if distance_from_hq > farthest_unit_distance:
                    farthest_unit_distance = distance_from_hq
                    self.farthest_unit_position = unit.pos

        return self.farthest_unit_position

    def train_units(self):
        while self.gold >= 10:
            print(f'gold = {self.gold}, upkeep={self.upkeep}, income={self.income}', file=sys.stderr)
            train_pos = self.get_train_position()
            mod = 1

            if train_pos.x > 0:
                mod = -1

            # find self.farthest_unit_position and spawn beside it
            # todo: self.get_farthest_unit_position()
            if self.get_farthest_unit_position():
                print(f'pos = {self.farthest_unit_position.x}, {self.farthest_unit_position.y}', file=sys.stderr)
                potential_targets = []
                potential_targets.append(Position(self.farthest_unit_position.x, self.farthest_unit_position.y + mod))
                potential_targets.append(Position(self.farthest_unit_position.x + mod, self.farthest_unit_position.y))
                potential_targets.append(Position(self.farthest_unit_position.x - mod, self.farthest_unit_position.y))
                potential_targets.append(Position(self.farthest_unit_position.x, self.farthest_unit_position.y - mod))

                for position in potential_targets:
                    if position.x < 0 or position.x > 11:
                        continue

                    if position.y < 0 or position.y > 11:
                        continue

                    # todo: handle condition where tile could be X build a more powerful unit on top of it
                    if self.tiles[position.y][position.x] in ['.', 'x', 'o']:
                        train_pos = position
                        print(f'train = {position.x},{position.y}', file=sys.stderr)
                        break

            if self.upkeep < self.income + 1:
                if self.gold >= 50:
                    self.actions.append(f'TRAIN 3 {train_pos.x} {train_pos.y}')
                    print(f'TRAIN 3 {train_pos.x} {train_pos.y}', file=sys.stderr)
                    self.gold -= 30
                    self.upkeep += 20
                    self.units.append(Unit(ME, 100, 3, train_pos.x, train_pos.y))
                    self.tiles[train_pos.y][train_pos.x] = 'O'
                elif self.gold >= 30:
                    self.actions.append(f'TRAIN 2 {train_pos.x} {train_pos.y}')
                    print(f'TRAIN 2 {train_pos.x} {train_pos.y}', file=sys.stderr)
                    self.gold -= 20
                    self.upkeep += 4
                    self.units.append(Unit(ME, 100, 2, train_pos.x, train_pos.y))
                    self.tiles[train_pos.y][train_pos.x] = 'O'
                elif self.gold >= 10:
                    self.actions.append(f'TRAIN 1 {train_pos.x} {train_pos.y}')
                    print(f'TRAIN 1 {train_pos.x} {train_pos.y}', file=sys.stderr)
                    self.gold -= 10
                    self.upkeep += 1
                    self.units.append(Unit(ME, 100, 1, train_pos.x, train_pos.y))
                    self.tiles[train_pos.y][train_pos.x] = 'O'
                else:
                    print('stop building', file=sys.stderr)
                    break
            else:
                break

    def init(self):
        number_mine_spots = int(input())
        for i in range(number_mine_spots):
            x, y = [int(j) for j in input().split()]
            # todo: deal with mines

    def update(self):
        self.units.clear()
        self.buildings.clear()
        self.actions.clear()

        self.tiles.clear()
        self.turn += 1
        self.upkeep = 0
        self.farthest_unit_position = None

        self.gold = int(input())
        self.income = int(input())
        self.gold -= self.income
        self.opponent_gold = int(input())
        self.opponent_income = int(input())

        for i in range(12):
            line = input()
            # print(line, file=sys.stderr)
            self.tiles.append(list(line))

        # print(self.tiles, file=sys.stderr)

        building_count = int(input())
        for i in range(building_count):
            owner, building_type, x, y = [int(j) for j in input().split()]
            self.buildings.append(Building(owner, building_type, x, y))

        farthest_unit_distance = 0
        hq = self.get_my_HQ()

        unit_count = int(input())
        for i in range(unit_count):
            owner, unit_id, level, x, y = [int(j) for j in input().split()]
            self.units.append(Unit(owner, unit_id, level, x, y))
            if owner == ME:
                if level == 1:
                    self.upkeep += 1
                elif level == 2:
                    self.upkeep += 4
                elif level == 3:
                    self.upkeep += 20

                test_position = Position(x, y)
                distance_from_hq = distance_between(hq.pos, test_position)
                if distance_from_hq > farthest_unit_distance:
                    self.farthest_unit_position = test_position

    def build_output(self):
        # TODO "core" of the AI
        self.train_units()
        self.move_units()

    def output(self):
        if self.actions:
            print(';'.join(self.actions))
        else:
            print('WAIT')


g = Game()

g.init()
while True:
    g.update()
    g.build_output()
    g.output()