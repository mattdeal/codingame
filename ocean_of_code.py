import sys
import math
import random

class Pos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, pos):
        return abs(self.x - pos.x) + abs(self.y - pos.y)

    def __str__(self):
        return f'({self.x},{self.y})'


class Cell(Pos):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.land = False
        self.visited = False

    def is_land(self):
        return self.land == True

    def set_land(self):
        self.land = True

    def is_visited(self):
        return self.visited == True

    def set_visited(self):
        self.visited = True


class Grid:
    def __init__(self):
        self.cells = []
        for y in range(height):
            for x in range(width):
                self.cells.append(Cell(x, y))

    def get_cell(self, x, y):
        if width > x >= 0 and height > y >= 0:
            return self.cells[x + width * y]
        return None

    def __str__(self):
        output = ''
        for y in range(height):
            for x in range(width):
                output += 'x' if self.cells[x + width * y].is_land() else '.'

            output += '\n'
                
        return output.strip()


class Game:
    def __init__(self):
        self.turn = 0
        self.grid = Grid()
        self.x = 0
        self.y = 0
        self.my_life = 0
        self.opp_life = 0
        self.opp_life_p = 5
        self.torpedo_cooldown = 0
        self.sonar_cooldown = 0
        self.silence_cooldown = 0
        self.mine_cooldown = 0
        self.sonar_result = 0
        self.opponent_orders = 0
        self.opponent_orders_p = 0
        self.available_moves = []
        self.command_p = ''
        self.enemy_x = {
            0: True,
            1: True,
            2: True,
            3: True,
            4: True,
            5: True,
            6: True,
            7: True,
            8: True,
            9: True,
            10: True,
            11: True,
            12: True,
            13: True,
            14: True
        }
        self.enemy_y = {
            0: True,
            1: True,
            2: True,
            3: True,
            4: True,
            5: True,
            6: True,
            7: True,
            8: True,
            9: True,
            10: True,
            11: True,
            12: True,
            13: True,
            14: True
        }

    # todo: come up with a better way to find a starting spot
    # current iteration, find closest spot to 0,0
    def pick_starting_location(self):
        # spawn in random location
        while True:
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            if not self.grid.get_cell(x, y).is_land():
                self.grid.get_cell(x, y).set_visited()
                print(f'{x} {y}')
                return

        # spawn near top left corner
        # for i in range(height):
        #     for j in range(width):
        #         if not self.grid.get_cell(j, i).is_land():
        #             self.grid.get_cell(j, i).set_visited()
        #             print(f'{j} {i}')
        #             return

    def update(self):
        # cary over old values
        self.opponent_orders_p = self.opponent_orders
        self.opp_life_p = self.opp_life

        self.x, self.y, self.my_life, self.opp_life, self.torpedo_cooldown, self.sonar_cooldown, self.silence_cooldown, self.mine_cooldown = [int(i) for i in input().split()]
        self.sonar_result = input()
        self.opponent_orders = input()
        self.turn+=1
        
        debug(f'turn = {self.turn}')
        debug(f'x = {self.x}')
        debug(f'y = {self.y}')
        debug(f'my_life = {self.my_life}')
        debug(f'opp_life = {self.opp_life}')
        debug(f'torpedo_cooldown = {self.torpedo_cooldown}')
        debug(f'sonar_cooldown = {self.sonar_cooldown}')
        debug(f'silence_cooldown = {self.silence_cooldown}')
        debug(f'mine_cooldown = {self.mine_cooldown}')
        debug(f'sonar_result = {self.sonar_result}')
        debug(f'opponent_orders = {self.opponent_orders}')

        # see if sonar result was Y
        if self.sonar_result == 'Y':
            zone = int(self.command_p.split(' ')[1])
            debug(f'sonar result in {zone}')
            x_min = 0
            x_max = 0
            y_min = 0
            y_max = 0

            if zone == 1:
                x_min = 0
                x_max = 4
                y_min = 0
                y_max = 4
            elif zone == 2:
                x_min = 5
                x_max = 9
                y_min = 0
                y_max = 4
            elif zone == 3:
                x_min = 10
                x_max = 14
                y_min = 0
                y_max = 4
            elif zone == 4:
                x_min = 0
                x_max = 4
                y_min = 5
                y_max = 9
            elif zone == 5:
                x_min = 5
                x_max = 9
                y_min = 5
                y_max = 9
            elif zone == 6:
                x_min = 10
                x_max = 14
                y_min = 5
                y_max = 9
            elif zone == 7:
                x_min = 0
                x_max = 4
                y_min = 10
                y_max = 14
            elif zone == 8:
                x_min = 5
                x_max = 9
                y_min = 10
                y_max = 14
            else:
                x_min = 10
                x_max = 14
                y_min = 10
                y_max = 14

            # x_min = min(self.enemy_x.keys())
            # x_max = max(self.enemy_x.keys())
            # y_min = min(self.enemy_y.keys())
            # y_max = max(self.enemy_y.keys()) 
            debug('sonar restrict to')
            debug(f'x {x_min} - {x_max}')
            debug(f'y {y_min} - {y_max}')

            keys_to_delete = []
            for key in self.enemy_x.keys():
                if key < x_min or key > x_max:
                    keys_to_delete.append(key)

            debug('keys to delete x')
            debug(keys_to_delete)

            for key in keys_to_delete:
                del  self.enemy_x[key]
            
            keys_to_delete = []
            for key in self.enemy_y.keys():
                if key < y_min or key > y_max:
                    keys_to_delete.append(key)

            debug('keys to delete y')
            debug(keys_to_delete)

            for key in keys_to_delete:
                del self.enemy_y[key]

            x_min = min(self.enemy_x.keys())
            x_max = max(self.enemy_x.keys())
            y_min = min(self.enemy_y.keys())
            y_max = max(self.enemy_y.keys())
            debug(f'x {x_min} - {x_max}')
            debug(f'y {y_min} - {y_max}')
            debug('-- end sonar --')

        # todo: see if enemy health is lower
        if self.opp_life < self.opp_life_p:
            debug('enemy got hurt last turn.  prev command was ' + self.opponent_orders_p)
            # todo: did they lose 1 or 2 health
            # todo: make sure they lost health from a torpedo not a bad command
            if self.opponent_orders.find('SURFACE') > -1:
                debug('enemy surfaced and took damage')
            elif self.opponent_orders_p.find('TORPEDO') > -1:
                debug('enemy fired a torpedo, did they hit themselves?')
                if self.torpedo_cooldown == 3:
                    debug('I just fired a torpedo')
                else:
                    debug(f'my torpedo cooldown is {self.torpedo_cooldown}')
                    debug('enemy is in 3x3 square around torpedo location')
            elif self.torpedo_cooldown == 3 and self.command_p.find('TORPEDO') > -1:
                debug('i just fired a torpedo, they must be in the blast radius')
                command_parts = self.command_p.split(' ')
                torpedo_x = int(command_parts[1])
                torpedo_y = int(command_parts[2])

                x_min = min(self.enemy_x.keys())
                x_max = max(self.enemy_x.keys())
                y_min = min(self.enemy_y.keys())
                y_max = max(self.enemy_y.keys()) 

                debug(f'x {x_min} - {x_max}')
                debug(f'y {y_min} - {y_max}')

                keys_to_delete = []
                for key in self.enemy_x.keys():
                    if key < torpedo_x - 1 or key > torpedo_x + 1:
                        keys_to_delete.append(key)

                for key in keys_to_delete:
                    del  self.enemy_x[key]
                
                keys_to_delete = []
                for key in self.enemy_y.keys():
                    if key < torpedo_y - 1 or key > torpedo_y + 1:
                        keys_to_delete.append(key)

                for key in keys_to_delete:
                    del self.enemy_y[key]

                x_min = min(self.enemy_x.keys())
                x_max = max(self.enemy_x.keys())
                y_min = min(self.enemy_y.keys())
                y_max = max(self.enemy_y.keys()) 

                debug(f'x {x_min} - {x_max}')
                debug(f'y {y_min} - {y_max}')
                debug('-- end torpedo logic --')

                # todo: check damage, if it was 2 and they didnt shoot themselves or surface, it was a direct hit

                # todo: shrink area to the blast radius of the previous torpedo

        # if I fired a torpedo, and their health is lowered by 1, shrink enemy location to the area surrounding the explosion UNLESS they torpedoed themselves
        # if I fired a torpedo, and their health is lowered by 2, shrink enemy location to the cell I fired at UNLESS they torpedoed themselves

    # todo: make this handle a point and return moves for that point
    # this will allow it to be more useful for finding moves from an optional move
    def find_available_moves(self, x, y):
        available_moves = []

        # N = y-1
        if self.grid.get_cell(x, y-1):
            if self.grid.get_cell(x, y-1).is_land() or self.grid.get_cell(x, y-1).is_visited():
                debug('cannot go N')
            else:
                # debug('can go N')
                available_moves.append('N')
        else:
            debug('cannot go N')

        # S = y+1
        if self.grid.get_cell(x, y+1):
            if self.grid.get_cell(x, y+1).is_land() or self.grid.get_cell(x, y+1).is_visited():
                debug('cannot go S')
            else:
                # debug('can go S')
                available_moves.append('S')
        else:
            debug('cannot go S')

        # W = x-1
        if self.grid.get_cell(x-1, y):
            if self.grid.get_cell(x-1, y).is_land() or self.grid.get_cell(x-1, y).is_visited():
                debug('cannot go W')
            else:
                # debug('can go W')
                available_moves.append('W')
        else:
            debug('cannot go W')
        
        # E = x+1
        if self.grid.get_cell(x+1, y):
            if self.grid.get_cell(x+1, y).is_land() or self.grid.get_cell(x+1, y).is_visited():
                debug('cannot go E') 
            else:
                # debug('can go E')
                available_moves.append('E')
        else:
            debug('cannot go E')

        return available_moves

    def handle_enemy_move(self):
        # todo: get enemy move
        if self.opponent_orders == 'NA':
            debug(' no order')
        else:
            commands = self.opponent_orders.split('|')
            for command in commands:
                debug(command)
                command_parts = command.split(' ')
                if command_parts[0] == 'MOVE':
                    direction = command_parts[1]
                    x_min = min(self.enemy_x.keys())
                    x_max = max(self.enemy_x.keys())
                    y_min = min(self.enemy_y.keys())
                    y_max = max(self.enemy_y.keys()) 

                    # todo: add min - 1 (when min is > 0) back to list when moving left/up
                    # todo: add max + 1 (when max is < height) back to list when moving right/down

                    if direction == 'N':
                        del self.enemy_y[y_max]
                        if y_min > 0:
                            self.enemy_y[y_min - 1] = True
                    elif direction == 'S':
                        del self.enemy_y[y_min]
                        if y_max < height - 1:
                            self.enemy_y[y_max + 1] = True
                    elif direction == 'E':
                        del self.enemy_x[x_min]
                        if x_max < height - 1:
                            self.enemy_x[x_max + 1] = True
                    else:
                        del self.enemy_x[x_max]
                        if x_min > 0:
                            self.enemy_x[x_min - 1] = True

                    # x_min = min(self.enemy_x.keys())
                    # x_max = max(self.enemy_x.keys())
                    # y_min = min(self.enemy_y.keys())
                    # y_max = max(self.enemy_y.keys()) 

                    # debug(f'x {x_min}-{x_max}')
                    # debug(f'y {y_min}-{y_max}')

                    # enemy_area = (x_max - x_min) * (y_max - y_min)

                    # debug(f'area {enemy_area}')
                elif command_parts[0] == 'TORPEDO':
                    # get torpedo detonation point
                    t_x = int(command_parts[1])
                    t_y = int(command_parts[2])

                    # find firing range
                    x_min = t_x - 4
                    x_max = t_x + 4
                    y_min = t_y - 4
                    y_max = t_y + 4

                    if x_min < 0: x_min = 0
                    if y_min < 0: y_min = 0
                    if x_max > width - 1: x_max = width - 1
                    if y_max > height - 1: y_max = height - 1

                    # debug(f'x {x_min}-{x_max}')
                    # debug(f'y {y_min}-{y_max}')
                    # enemy_area = (x_max - x_min) * (y_max - y_min)
                    # debug(f'area {enemy_area}')

                    # remove areas outside torpedo range from possible locations
                    keys_to_delete = []
                    for key in self.enemy_x.keys():
                        if key < x_min or key > x_max:
                            keys_to_delete.append(key)

                    for key in keys_to_delete:
                        del  self.enemy_x[key]
                    
                    keys_to_delete = []
                    for key in self.enemy_y.keys():
                        if key < y_min or key > y_max:
                            keys_to_delete.append(key)

                    for key in keys_to_delete:
                        del self.enemy_y[key]
                elif command_parts[0] == 'SURFACE':
                    # SURFACE n - Enemy is in sector n, one of 25 squares, keep a list of previous enemy moves to determine where they might be
                    # if SURFACE in enemy command, update enemy_x/y to only contain the 5x5 area of that square
                    # 1 - x 0-4, y 0-4
                    # 2 - x 5-9, y 0-4
                    # 3 - x 10-14, y 0-4
                    # 4 - x 0-4, y 5-9
                    # 5 - x 5-9, y 5-9
                    # 6 - x 10-14, y 5-9
                    # 7 - x 0-4, y 10-14
                    # 8 - 5-9, y 10-14
                    # 9 - x 10-14, y 10-14

                    zone = int(command_parts[1])
                    debug(f'enemy surfaced in {zone}')
                    x_min = 0
                    x_max = 0
                    y_min = 0
                    y_max = 0

                    if zone == 1:
                        x_min = 0
                        x_max = 4
                        y_min = 0
                        y_max = 4
                    elif zone == 2:
                        x_min = 5
                        x_max = 9
                        y_min = 0
                        y_max = 4
                    elif zone == 3:
                        x_min = 10
                        x_max = 14
                        y_min = 0
                        y_max = 4
                    elif zone == 4:
                        x_min = 0
                        x_max = 4
                        y_min = 5
                        y_max = 9
                    elif zone == 5:
                        x_min = 5
                        x_max = 9
                        y_min = 5
                        y_max = 9
                    elif zone == 6:
                        x_min = 10
                        x_max = 14
                        y_min = 5
                        y_max = 9
                    elif zone == 7:
                        x_min = 0
                        x_max = 4
                        y_min = 10
                        y_max = 14
                    elif zone == 8:
                        x_min = 5
                        x_max = 9
                        y_min = 10
                        y_max = 14
                    else:
                        x_min = 10
                        x_max = 14
                        y_min = 10
                        y_max = 14

                    keys_to_delete = []
                    for key in self.enemy_x.keys():
                        if key < x_min or key > x_max:
                            keys_to_delete.append(key)

                    for key in keys_to_delete:
                        del  self.enemy_x[key]
                    
                    keys_to_delete = []
                    for key in self.enemy_y.keys():
                        if key < y_min or key > y_max:
                            keys_to_delete.append(key)

                    for key in keys_to_delete:
                        del self.enemy_y[key]
                elif command_parts[0] == 'SILENCE':
                    debug('enemy used silence')
                    # todo: add up to 4 on each side of enemy_x/y
                    x_min = min(self.enemy_x.keys())
                    x_max = max(self.enemy_x.keys())
                    y_min = min(self.enemy_y.keys())
                    y_max = max(self.enemy_y.keys()) 

                    debug(f'x {x_min} - {x_max}')
                    debug(f'y {y_min} - {y_max}')

                    for i in range(1, 4):
                        if x_min - i > -1:
                            self.enemy_x[x_min - i] = True

                        if x_max + i < width:
                            self.enemy_x[x_max + i] = True

                        if y_min - i > -1:
                            self.enemy_y[y_min - i] = True

                        if y_max + i < height:
                            self.enemy_y[y_max + i] = True

                    x_min = min(self.enemy_x.keys())
                    x_max = max(self.enemy_x.keys())
                    y_min = min(self.enemy_y.keys())
                    y_max = max(self.enemy_y.keys()) 

                    debug(f'x {x_min} - {x_max}')
                    debug(f'y {y_min} - {y_max}')

                else:
                    debug('todo handle weird command')

        # todo: determine if power can/should be used
        # note - you can move and use a power at the same time, so it should be possible to move for the third time and then immediately torpedo
        # if torpedo cooldown is max, and enemy hp is lower this round, -1 near hit, -2 clean hit, we now know their position, can track and fire

    # todo: self.build_output
    def build_output(self):
        # debug('thinking...')

        # set current cell visited
        self.grid.get_cell(self.x, self.y).set_visited()

        self.available_moves = self.find_available_moves(self.x, self.y)
        
        self.handle_enemy_move()

        # todo: get power cooldowns

    # big todos
    # make random moves better - tend towards open space
    # move towards enemy square
    def output(self):
        my_position = Cell(self.x, self.y)

        x_min = min(self.enemy_x.keys())
        x_max = max(self.enemy_x.keys())
        y_min = min(self.enemy_y.keys())
        y_max = max(self.enemy_y.keys()) 

        debug(f'x {x_min}-{x_max}')
        debug(f'y {y_min}-{y_max}')

        # needs +1 for single row width, area can't be 0
        enemy_area = (x_max - x_min + 1) * (y_max - y_min + 1)

        debug(f'area {enemy_area}')

        # todo: if enemy torpedoed me last turn, I need to move, use silence and move up to 4 squares in a single direction

        # todo: check size of enemy location, if it's small enough to torpedo and i am close enough, fire one
        if self.torpedo_cooldown == 0:
            debug('torpedo is ready')

            # ignores personal safety, any distance is valid
            if enemy_area < 25:
                debug('start shooting')

                for x in range(x_min, x_max + 1):
                    for y in range (y_min, y_max + 1):
                        # don't fire at land
                        if self.grid.get_cell(x, y).is_land():
                            continue

                        distance = my_position.distance(Cell(x, y))
                        debug(f'testing {x} {y}, distance {distance}')

                        if distance <= 4:
                            # todo: if tile beside me is land, reduce distance to 3
                            # trace tiles to target, increase distance by 1 for each land tile
                            # should help with issues where target is more than 4 squares away due to traveling around land
                            diff_x = self.x - x + 1
                            diff_y = self.y - y + 1

                            debug(f'diff_x {diff_x}, diff_y {diff_y}')

                            if diff_x == 0:
                                i = 0
                                debug('diff_x is 0, checking y')
                                for j in range(0 , diff_y):
                                    debug(f'j {j}')
                                    debug(f'testing for land tiles {x + i}, {y + j}')
                                    
                                    if self.grid.get_cell(x + i, y + j).is_land():
                                        debug('cell is land, increase firing distance')
                                        distance += 1

                                    debug(f'distance {distance}')

                                for j in range(diff_y, 0):
                                    debug(f'-j {j}')
                                    debug(f'-testing for land tiles {x + i}, {y + j}')
                                    
                                    if self.grid.get_cell(x + i, y + j).is_land():
                                        debug('-cell is land, increase firing distance')
                                        distance += 1

                                    debug(f'-distance {distance}')

                            for i in range(0, diff_x):
                                debug(f'i {i}')
                                for j in range(0 , diff_y):
                                    debug(f'j {j}')
                                    debug(f'testing for land tiles {x + i}, {y + j}')
                                    
                                    if self.grid.get_cell(x + i, y + j).is_land():
                                        debug('cell is land, increase firing distance')
                                        distance += 1

                                    debug(f'distance {distance}')

                                for j in range(diff_y, 0):
                                    debug(f'-j {j}')
                                    debug(f'-testing for land tiles {x + i}, {y + j}')
                                    
                                    if self.grid.get_cell(x + i, y + j).is_land():
                                        debug('-cell is land, increase firing distance')
                                        distance += 1

                                    debug(f'-distance {distance}')

                            # flip range to handle negatives
                            for i in range(diff_x, 0):
                                debug(f'-i {i}')

                                for j in range(0 , diff_y):
                                    debug(f'j {j}')
                                    debug(f'testing for land tiles {x + i}, {y + j}')
                                    
                                    if self.grid.get_cell(x + i, y + j).is_land():
                                        debug('cell is land, increase firing distance')
                                        distance += 1

                                    debug(f'distance {distance}')

                                for j in range(diff_y, 0):
                                    debug(f'-j {j}')
                                    debug(f'-testing for land tiles {x + i}, {y + j}')
                                    
                                    if self.grid.get_cell(x + i, y + j).is_land():
                                        debug('-cell is land, increase firing distance')
                                        distance += 1

                                    debug(f'-distance {distance}')

                            # test that distance is still under 4
                            if distance <= 4:
                                self.command_p = f'TORPEDO {x} {y}'
                                print(self.command_p)
                                return

            # torpedo is ready and the enemy is in a known 9x9 area
            # personal safety, only distance between 2 and 4 is valid
            if enemy_area < 81:
                debug('start shooting safely')

                # targets = [ [100] * height for _ in range(width)]
                
                # debug(targets)

                #increment x_max and y_max if necessary
                # if x_min == x_max:
                #     x_max += 1

                # if y_min == y_max:
                #     y_max += 1
                
                for x in range(x_min, x_max + 1):
                    for y in range (y_min, y_max + 1):
                        # don't fire at land
                        if self.grid.get_cell(x, y).is_land():
                            continue

                        distance = my_position.distance(Cell(x, y))
                        debug(f'testing {x} {y}, distance {distance}')

                        if distance <= 4:
                            # todo: if tile beside me is land, reduce distance to 3
                            # trace tiles to target, increase distance by 1 for each land tile
                            # should help with issues where target is more than 4 squares away due to traveling around land
                            diff_x = self.x - x + 1
                            diff_y = self.y - y + 1

                            debug(f'diff_x {diff_x}, diff_y {diff_y}')

                            if diff_x == 0:
                                i = 0
                                debug('diff_x is 0, checking y')
                                for j in range(0 , diff_y):
                                    debug(f'j {j}')
                                    debug(f'testing for land tiles {x + i}, {y + j}')
                                    
                                    if self.grid.get_cell(x + i, y + j).is_land():
                                        debug('cell is land, increase firing distance')
                                        distance += 1

                                    debug(f'distance {distance}')

                                for j in range(diff_y, 0):
                                    debug(f'-j {j}')
                                    debug(f'-testing for land tiles {x + i}, {y + j}')
                                    
                                    if self.grid.get_cell(x + i, y + j).is_land():
                                        debug('-cell is land, increase firing distance')
                                        distance += 1

                                    debug(f'-distance {distance}')

                            for i in range(0, diff_x):
                                debug(f'i {i}')
                                for j in range(0 , diff_y):
                                    debug(f'j {j}')
                                    debug(f'testing for land tiles {x + i}, {y + j}')
                                    
                                    if self.grid.get_cell(x + i, y + j).is_land():
                                        debug('cell is land, increase firing distance')
                                        distance += 1

                                    debug(f'distance {distance}')

                                for j in range(diff_y, 0):
                                    debug(f'-j {j}')
                                    debug(f'-testing for land tiles {x + i}, {y + j}')
                                    
                                    if self.grid.get_cell(x + i, y + j).is_land():
                                        debug('-cell is land, increase firing distance')
                                        distance += 1

                                    debug(f'-distance {distance}')

                            # flip range to handle negatives
                            for i in range(diff_x, 0):
                                debug(f'-i {i}')

                                for j in range(0 , diff_y):
                                    debug(f'j {j}')
                                    debug(f'testing for land tiles {x + i}, {y + j}')
                                    
                                    if self.grid.get_cell(x + i, y + j).is_land():
                                        debug('cell is land, increase firing distance')
                                        distance += 1

                                    debug(f'distance {distance}')
                                    
                                for j in range(diff_y, 0):
                                    debug(f'-j {j}')
                                    debug(f'-testing for land tiles {x + i}, {y + j}')
                                    
                                    if self.grid.get_cell(x + i, y + j).is_land():
                                        debug('-cell is land, increase firing distance')
                                        distance += 1

                                    debug(f'-distance {distance}')

                            # test that distance is still under 4
                            if 2 < distance <= 4:
                                self.command_p = f'TORPEDO {x} {y}'
                                print(self.command_p)
                                return
                
                # debug(targets)
           
           # todo: find the closest cell in the enemy's possible locations and fire a torpedo
            # todo: come up with some way to store the last time I fired at a cell, might not matter if the area is small enough
            # for x min to x max
            # for y min to y max

        if self.sonar_cooldown == 0 and enemy_area > 25:
            debug('should use sonar')
            zone = 0

            if self.x < 5:
                if self.y < 5:
                    zone = 1
                elif self.y < 10:
                    zone = 4
                else:
                    zone = 7
            elif self.x < 10:
                if self.y < 5:
                    zone = 2
                elif self.y < 10:
                    zone = 5
                else:
                    zone = 8
            else:
                if self.y < 5:
                    zone = 3
                elif self.y < 10:
                    zone = 6
                else:
                    zone = 9

            if zone > 0:
                self.command_p = f'SONAR {zone}'
                print(self.command_p)
                return

        # start silence logic
        # random int to see if I should silence, otherwise sonar is never used
        should_silence = random.randint(0, 3)
        if self.silence_cooldown == 0 and should_silence == 1:
            debug('should use silence')

            if len(self.available_moves) > 0:
                debug(f'len available moves {len(self.available_moves)}')

                index = random.randint(0, len(self.available_moves) - 1)
                move = self.available_moves[index]
                
                available_moves = {}
                best_option_len = 0
                best_move = move
                for i in range(0, len(self.available_moves)):
                    debug(f'{i}')
                    current_move = self.available_moves[i]
                    x = self.x
                    y = self.y

                    if current_move == 'N':
                        y -= 1
                    elif current_move == 'S':
                        y += 1
                    elif current_move == 'W':
                        x -= 1
                    else:
                        x += 1

                    # todo: test if adding more depth to this causes timeout issues
                    # for example, get sum of available moves from each option after this
                    available_moves[current_move] = len(self.find_available_moves(x, y)) + \
                        len(self.find_available_moves(x + 1, y)) + \
                        len(self.find_available_moves(x - 1, y)) + \
                        len(self.find_available_moves(x, y + 1)) + \
                        len(self.find_available_moves(x, y - 1))

                # todo: find len of available moves of all available moves
                
                for key in available_moves.keys():
                    if available_moves[key] > best_option_len:
                        best_move = key
                        best_option_len = available_moves[key]

                debug(f'best option {best_move}, options {available_moves[best_move]}')

                self.command_p = f'SILENCE {best_move} 1'
                print(self.command_p)
                return                    
            else:
                debug('ran out of moves, must use SURFACE')
                
                # clear visited value for all cells
                for y in range(height):
                    for x in range(width):
                        self.grid.get_cell(x, y).visited = False

                self.command_p = 'SURFACE'
                print(self.command_p)
                return

        # todo: check ahead when picking moves so I don't move into a corner
        # get available moves for each available move
        # - move to the one that has more options

        # todo: move towards enemy somehow
        # - whichever range is smaller of enemy_x or enemy_y, move to that x or y and then go random?

        # check cooldowns, if an ability is not charged, add it to the move command
        ability_to_charge = ''
        if self.torpedo_cooldown > 0:
            ability_to_charge = 'TORPEDO'
        elif self.silence_cooldown > 0:
            ability_to_charge = 'SILENCE'
        elif self.sonar_cooldown > 0:
            ability_to_charge = 'SONAR'

        # todo: if enemy area is under a certain size 100?
        # todo: get distance to 4 corners of enemy rectangle to find nearest corner
        # todo: get distance from all valid moves nearby to nearest corner
        # todo: move to tile closest to closest corner and use charge

        # pick a random direction in available directions
        debug('nothing to do, move and charge ' + ability_to_charge)
        if len(self.available_moves) > 0:
            debug(f'len available moves {len(self.available_moves)}')

            index = random.randint(0, len(self.available_moves) - 1)
            move = self.available_moves[index]
            
            available_moves = {}
            best_option_len = 0
            best_move = move
            for i in range(0, len(self.available_moves)):
                debug(f'{i}')
                current_move = self.available_moves[i]
                x = self.x
                y = self.y

                if current_move == 'N':
                    y -= 1
                elif current_move == 'S':
                    y += 1
                elif current_move == 'W':
                    x -= 1
                else:
                    x += 1

                # todo: test if adding more depth to this causes timeout issues
                # for example, get sum of available moves from each option after this
                available_moves[current_move] = len(self.find_available_moves(x, y)) + \
                    len(self.find_available_moves(x + 1, y)) + \
                    len(self.find_available_moves(x - 1, y)) + \
                    len(self.find_available_moves(x, y + 1)) + \
                    len(self.find_available_moves(x, y - 1))

            # todo: find len of available moves of all available moves
            
            for key in available_moves.keys():
                if available_moves[key] > best_option_len:
                    best_move = key
                    best_option_len = available_moves[key]

            debug(f'best option {best_move}, options {available_moves[best_move]}')

            if ability_to_charge:
                self.command_p = f'MOVE {best_move} {ability_to_charge}'
                print(self.command_p)
                return
            else:
                self.command_p = f'MOVE {best_move}'
                print(self.command_p)
                return
        else:
            debug('ran out of moves, must use SURFACE')
            
            # clear visited value for all cells
            for y in range(height):
                for x in range(width):
                    self.grid.get_cell(x, y).visited = False

            self.command_p = 'SURFACE'
            print(self.command_p)
            return


# helper methods
def debug(msg):
    print(str(msg), file=sys.stderr)
    
# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.
width, height, my_id = [int(i) for i in input().split()]
debug(f'width = {width}')
debug(f'height = {height}')
debug(f'my_id = {my_id}')

# start up game object
game = Game()

# store the map in game.grid
for i in range(height):
    line = input()
    for j in range(width):
        land = line[j] == 'x'
        if land:
            game.grid.get_cell(j, i).set_land()

# set starting location
game.pick_starting_location()

# game loop
while True:
    game.update()
    game.build_output()
    game.output()
