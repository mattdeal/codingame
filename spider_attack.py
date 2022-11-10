import math
import sys
from collections import namedtuple

# Helpful stats
# - distance from threat_for
# - turns from threat_for

# Other
# - store target/job per hero - partially done, current_targets
# - consider how close the monster is to our base in prioritizing targets
# - consider how much health the monster has in prioritizing targets (or allowing double ups)

# Notes
# - heroes get mana per attack, so stacking 2 heroes on the same monster gives double mana?
# - as enemy hp gets higher, need more than 1 dude to kill it once it gets to base, need to lower max distance over time
# - look at threat_for and near_base combination
# - instead of heading to base with no target, head to a predefined location near the edge of base
# - in higher tiers, one offensive unit and 2 more defensive units
# - shield units in the enemy base and blow them towards their corner
# - deflect large enemies towards enemy base on defense instead of fighting them (red guys)

# targeting priority - defenders
# - near_base = 1, threat_for = 1
# - near_base = 0, threat_for = 1
# - rank by distance from base low to high, can target the same unit
# 
# spell casting
# - distance to base > 5k, but less than 7k and hp above X, control towards enemy base
# - distance < 5k and len dangerous enemies > 1, wind towards enemy base


# targeting priority - offense
# - near_base = 0, threat_for = 1 or 0
# - no distance ranking, but may need to swap to enemies near the opponent's base after certain number of turns
# 
# spell casting
# - near_base = 0, threat_for = 2, shield = 0, control
# - near_base = 1, threat_for = 2, shield = 0, is_controlled = 1, shield
# - distance from enemy base < wind.distance and len dangerous_enemies > 1, wind towards enemy base

# helper methods
def debug(msg):
    print(str(msg), file=sys.stderr)

def distance_between(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def defense_strategy(g, hero_id):
    hero = [hero for hero in g['my_heroes'] if hero.id == hero_id][0]
    
    # one of these will be defined
    target = None
    spell = None

    threat_critical = {}
    threat_high = {}
    threat_medium = {}
    threat_low = {}
    enemy_heroes = {}

    DISTANCE_THREAT_HIGH = 4000
    DISTANCE_THREAT_MEDIUM = 6000
    HP_MIN_CONTROL = 15

    # waiting spots
    WAITING_SPOTS = {
        17630: [
            (17630 - 2500, 9000 - 2500),
            (17630 - 6000, 9000 - 4000),
        ],
        0: [
            (2500, 2500),
            (6000, 4000),
        ]
    }

    for enemy in g['opp_heroes']:
        distance = distance_between(hero.x, hero.y, enemy.x, enemy.y)
        if distance > RANGE_WIND:
            continue

        enemy_heroes[distance] = enemy

    for monster in g['monsters']:
        # ignore monsters outside this strategy radius from base
        distance_from_base = distance_between(base_x, base_y, monster.x, monster.y)
        if distance_from_base > DISTANCE_THREAT_MEDIUM:
            continue

        # distance = distance_between(hero.x, hero.y, monster.x, monster.y)

        # targeting priority - defenders
        # - near_base = 1, threat_for = 1
        # - near_base = 0, threat_for = 1

        if monster.threat_for == 1 and monster.near_base == 1:
            threat_high[distance_from_base] = monster

            if monster.shield_life > 0:
                threat_critical[distance_from_base] = monster

        if monster.threat_for == 1 and monster.near_base == 0:
            threat_medium[distance_from_base] = monster

        if monster.threat_for == 0:
            threat_low[distance_from_base] = monster

    if g['my_mana'] >= COST_SPELL:
        # spell casting
        # - distance to base > 5k, but less than 7k and hp above X, control towards enemy base
        # - distance < 5k and len dangerous enemies > 1, wind towards enemy base
        
        # blow away enemy heroes if there is danger in the base
        if len(threat_high.keys()) > 0 and len(enemy_heroes.keys()) > 0:
            distance_from_base = min(enemy_heroes.keys())
            target = enemy_heroes[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if distance_from_hero < RANGE_WIND:
                if base_x == 0:
                    return f'SPELL WIND 17630 9000 woosh!'
                else:
                    return f'SPELL WIND 0 0 woosh!'

        # blow away monsters if more than 1 are in the base
        if len(threat_high.keys()) > 1:
            distance_from_base = min(threat_high.keys())
            target = threat_high[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if distance_from_hero < RANGE_WIND:
                if base_x == 0:
                    return f'SPELL WIND 17630 9000 woosh!'
                else:
                    return f'SPELL WIND 0 0 woosh!'

        # control monsters near the base that will eventually be a problem
        if len(threat_medium.keys()) > 0:
            distance_from_base = min(threat_medium.keys())
            target = threat_medium[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)
            if not target.id in CONTROL_IDS:
                if distance_from_hero < RANGE_CONTROL:
                    if target.health > HP_MIN_CONTROL:
                        if target.is_controlled == 0:
                            if target.shield_life == 0:
                                CONTROL_IDS.append(target.id)
                                if base_x == 0:
                                    debug(target)
                                    return f'SPELL CONTROL {target.id} 17630 9000 that way!'
                                else:
                                    return f'SPELL CONTROL {target.id} 0 0 that way!'

        # control monsters near the base
        if len(threat_low.keys()) > 1:
            distance_from_base = min(threat_low.keys())
            target = threat_low[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if not target.id in CONTROL_IDS:
                if distance_from_hero < RANGE_CONTROL:
                    if target.health > HP_MIN_CONTROL:
                        if target.is_controlled == 0:
                            if target.shield_life == 0:
                                CONTROL_IDS.append(target.id)

                                if base_x == 0:
                                    return f'SPELL CONTROL {target.id} 17630 9000 that way!'
                                else:
                                    return f'SPELL CONTROL {target.id} 0 0 that way!'

    # attacking
    # - attack threat_high, threat_medium, threat_low
    # - if no defined target, move to waiting spot
    
    # high threat targets
    if len(threat_high.keys()) > 0:
        for id in sorted(threat_high.keys()):
            target = threat_high[id]
            debug(f'Hero {hero.id} targeting high threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # shielded enemy in the base, have to fight it
    # if len(threat_critical.keys()) > 0:
    #     for id in sorted(threat_critical.keys()):
    #         target = threat_critical[id]
    #         debug(f'Hero {hero.id} targeting critical threat enemy {target.id} at {target.x}, {target.y}')
    #         return f'MOVE {target.x} {target.y} attack {target.id}'

    # medium threat targets
    if len(threat_medium.keys()) > 0:
        for id in sorted(threat_medium.keys()):
            target = threat_medium[id]
            debug(f'Hero {hero.id} targeting medium threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # low threat targets
    if len(threat_low.keys()) > 0:
        for id in sorted(threat_low.keys()):
            target = threat_low[id]
            debug(f'Hero {hero.id} targeting low threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # default location
    if NEXT_LOCATION.get(hero.id, None) is None:
        NEXT_LOCATION[hero.id] = 0
    
    target_location = WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]]
    distance_to_target = distance_between(hero.x, hero.y, target_location[0], target_location[1])

    # set next location
    if distance_to_target < 100:
        NEXT_LOCATION[hero.id] += 1

        # wrap around to starting location
        if NEXT_LOCATION[hero.id] >= len(WAITING_SPOTS[base_x]):
            NEXT_LOCATION[hero.id] = 0

    return f'MOVE {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][0]} {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][1]} patrol'

def defense_strategy_1(g, hero_id):
    hero = [hero for hero in g['my_heroes'] if hero.id == hero_id][0]
    
    # one of these will be defined
    target = None
    spell = None

    threat_critical = {}
    threat_high = {}
    threat_medium = {}
    threat_low = {}
    enemy_heroes = {}

    DISTANCE_THREAT_HIGH = 4000
    DISTANCE_THREAT_MEDIUM = 8000
    HP_MIN_CONTROL = 17

    # waiting spots
    WAITING_SPOTS = {
        17630: [
            (17630 - 2000, 9000 - 6000),
            (17630 - 5000, 9000 - 4000),
            # (17630 - 6000, 9000 - 2000),
            # (17630 - 2500, 9000 - 2500),
            # (14000, 4000),
            # (20000, 3500)
        ],
        0: [
            (2000, 6000),
            (5000, 4000),
            # (6000, 2000),
            # (2500, 2500),
            # (6000, 4000),
            # (7500, 1000)
        ]
    }

    for enemy in g['opp_heroes']:
        distance = distance_between(hero.x, hero.y, enemy.x, enemy.y)
        if distance > RANGE_WIND:
            continue

        enemy_heroes[distance] = enemy

    for monster in g['monsters']:
        # ignore monsters outside this strategy radius from base
        distance_from_base = distance_between(base_x, base_y, monster.x, monster.y)
        if distance_from_base > DISTANCE_THREAT_MEDIUM:
            continue

        # distance = distance_between(hero.x, hero.y, monster.x, monster.y)

        # targeting priority - defenders
        # - near_base = 1, threat_for = 1
        # - near_base = 0, threat_for = 1

        if monster.threat_for == 1 and monster.near_base == 1:
            threat_high[distance_from_base] = monster

            if monster.shield_life > 0:
                threat_critical[distance_from_base] = monster

        if monster.threat_for == 1 and monster.near_base == 0:
            threat_medium[distance_from_base] = monster

        if monster.threat_for == 0:
            threat_low[distance_from_base] = monster

    if g['my_mana'] >= COST_SPELL:
        # spell casting
        # - distance to base > 5k, but less than 7k and hp above X, control towards enemy base
        # - distance < 5k and len dangerous enemies > 1, wind towards enemy base
        
        # blow away enemy heroes if there is danger in the base
        if len(threat_high.keys()) > 0 and len(enemy_heroes.keys()) > 0:
            distance_from_base = min(enemy_heroes.keys())
            target = enemy_heroes[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if distance_from_hero < RANGE_WIND:
                if base_x == 0:
                    return f'SPELL WIND 17630 9000 woosh!'
                else:
                    return f'SPELL WIND 0 0 woosh!'

        # blow away monsters if more than 1 are in the base
        if len(threat_high.keys()) > 1:
            distance_from_base = min(threat_high.keys())
            target = threat_high[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if distance_from_hero < RANGE_WIND:
                if base_x == 0:
                    return f'SPELL WIND 17630 9000 woosh!'
                else:
                    return f'SPELL WIND 0 0 woosh!'

        # control monsters near the base that will eventually be a problem
        if len(threat_medium.keys()) > 0:
            distance_from_base = min(threat_medium.keys())
            target = threat_medium[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)
            if not target.id in CONTROL_IDS:
                if distance_from_hero < RANGE_CONTROL:
                    if target.health > HP_MIN_CONTROL:
                        if target.is_controlled == 0:
                            if target.shield_life == 0:
                                CONTROL_IDS.append(target.id)
                                if base_x == 0:
                                    debug(target)
                                    return f'SPELL CONTROL {target.id} 17630 9000 that way!'
                                else:
                                    return f'SPELL CONTROL {target.id} 0 0 that way!'

        # control monsters near the base
        if len(threat_low.keys()) > 1:
            distance_from_base = min(threat_low.keys())
            target = threat_low[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if not target.id in CONTROL_IDS:
                if distance_from_hero < RANGE_CONTROL:
                    if target.health > HP_MIN_CONTROL:
                        if target.is_controlled == 0:
                            if target.shield_life == 0:
                                CONTROL_IDS.append(target.id)

                                if base_x == 0:
                                    return f'SPELL CONTROL {target.id} 17630 9000 that way!'
                                else:
                                    return f'SPELL CONTROL {target.id} 0 0 that way!'

    # attacking
    # - attack threat_high, threat_medium, threat_low
    # - if no defined target, move to waiting spot
    
    # high threat targets
    if len(threat_high.keys()) > 0:
        for id in sorted(threat_high.keys()):
            target = threat_high[id]
            debug(f'Hero {hero.id} targeting high threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # shielded enemy in the base, have to fight it
    # if len(threat_critical.keys()) > 0:
    #     for id in sorted(threat_critical.keys()):
    #         target = threat_critical[id]
    #         debug(f'Hero {hero.id} targeting critical threat enemy {target.id} at {target.x}, {target.y}')
    #         return f'MOVE {target.x} {target.y} attack {target.id}'

    # medium threat targets
    if len(threat_medium.keys()) > 0:
        for id in sorted(threat_medium.keys()):
            target = threat_medium[id]
            debug(f'Hero {hero.id} targeting medium threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # low threat targets
    if len(threat_low.keys()) > 0:
        for id in sorted(threat_low.keys()):
            target = threat_low[id]
            debug(f'Hero {hero.id} targeting low threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # default location
    if NEXT_LOCATION.get(hero.id, None) is None:
        NEXT_LOCATION[hero.id] = 0
    
    target_location = WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]]
    distance_to_target = distance_between(hero.x, hero.y, target_location[0], target_location[1])

    # set next location
    if distance_to_target < 100:
        NEXT_LOCATION[hero.id] += 1

        # wrap around to starting location
        if NEXT_LOCATION[hero.id] >= len(WAITING_SPOTS[base_x]):
            NEXT_LOCATION[hero.id] = 0

    return f'MOVE {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][0]} {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][1]} patrol'

def defense_strategy_2(g, hero_id):
    hero = [hero for hero in g['my_heroes'] if hero.id == hero_id][0]
    
    # one of these will be defined
    target = None
    spell = None

    threat_critical = {}
    threat_high = {}
    threat_medium = {}
    threat_low = {}
    enemy_heroes = {}

    DISTANCE_THREAT_HIGH = 4000
    DISTANCE_THREAT_MEDIUM = 8000
    HP_MIN_CONTROL = 17

    # waiting spots
    WAITING_SPOTS = {
        17630: [
            # (17630 - 2000, 9000 - 6000),
            (17630 - 5000, 9000 - 4000),
            (17630 - 6000, 9000 - 2000),
            # (17630 - 2500, 9000 - 2500),
            # (14000, 4000),
            # (20000, 3500)
        ],
        0: [
            # (2000, 6000),
            (5000, 4000),
            (6000, 2000),
            # (2500, 2500),
            # (6000, 4000),
            # (7500, 1000)
        ]
    }

    for enemy in g['opp_heroes']:
        distance = distance_between(hero.x, hero.y, enemy.x, enemy.y)
        if distance > RANGE_WIND:
            continue

        enemy_heroes[distance] = enemy

    for monster in g['monsters']:
        # ignore monsters outside this strategy radius from base
        distance_from_base = distance_between(base_x, base_y, monster.x, monster.y)
        if distance_from_base > DISTANCE_THREAT_MEDIUM:
            continue

        # distance = distance_between(hero.x, hero.y, monster.x, monster.y)

        # targeting priority - defenders
        # - near_base = 1, threat_for = 1
        # - near_base = 0, threat_for = 1

        if monster.threat_for == 1 and monster.near_base == 1:
            threat_high[distance_from_base] = monster

            if monster.shield_life > 0:
                threat_critical[distance_from_base] = monster

        if monster.threat_for == 1 and monster.near_base == 0:
            threat_medium[distance_from_base] = monster

        if monster.threat_for == 0:
            threat_low[distance_from_base] = monster

    # shielded enemy in the base, have to fight it
    if len(threat_critical.keys()) > 0:
        for id in sorted(threat_critical.keys()):
            target = threat_critical[id]
            debug(f'Hero {hero.id} targeting critical threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x} {target.y} attack {target.id}'

    if g['my_mana'] >= COST_SPELL:
        # spell casting
        # - distance to base > 5k, but less than 7k and hp above X, control towards enemy base
        # - distance < 5k and len dangerous enemies > 1, wind towards enemy base
        
        # blow away enemy heroes if there is danger in the base
        if len(threat_high.keys()) > 0 and len(enemy_heroes.keys()) > 0:
            distance_from_base = min(enemy_heroes.keys())
            target = enemy_heroes[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if distance_from_hero < RANGE_WIND:
                if base_x == 0:
                    return f'SPELL WIND 17630 9000 woosh!'
                else:
                    return f'SPELL WIND 0 0 woosh!'

        # blow away monsters if more than 1 are in the base
        if len(threat_high.keys()) > 1:
            distance_from_base = min(threat_high.keys())
            target = threat_high[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if distance_from_hero < RANGE_WIND:
                if base_x == 0:
                    return f'SPELL WIND 17630 9000 woosh!'
                else:
                    return f'SPELL WIND 0 0 woosh!'

        # control monsters near the base that will eventually be a problem
        if len(threat_medium.keys()) > 0:
            distance_from_base = min(threat_medium.keys())
            target = threat_medium[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)
            if not target.id in CONTROL_IDS:
                if distance_from_hero < RANGE_CONTROL:
                    if target.health > HP_MIN_CONTROL:
                        if target.is_controlled == 0:
                            if target.shield_life == 0:
                                CONTROL_IDS.append(target.id)
                                if base_x == 0:
                                    debug(target)
                                    return f'SPELL CONTROL {target.id} 17630 9000 that way!'
                                else:
                                    return f'SPELL CONTROL {target.id} 0 0 that way!'

        # control monsters near the base
        if len(threat_low.keys()) > 1:
            distance_from_base = min(threat_low.keys())
            target = threat_low[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if not target.id in CONTROL_IDS:
                if distance_from_hero < RANGE_CONTROL:
                    if target.health > HP_MIN_CONTROL:
                        if target.is_controlled == 0:
                            if target.shield_life == 0:
                                CONTROL_IDS.append(target.id)

                                if base_x == 0:
                                    return f'SPELL CONTROL {target.id} 17630 9000 that way!'
                                else:
                                    return f'SPELL CONTROL {target.id} 0 0 that way!'

    # attacking
    # - attack threat_high, threat_medium, threat_low
    # - if no defined target, move to waiting spot
    
    # high threat targets
    if len(threat_high.keys()) > 0:
        for id in sorted(threat_high.keys()):
            target = threat_high[id]
            debug(f'Hero {hero.id} targeting high threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # medium threat targets
    if len(threat_medium.keys()) > 0:
        for id in sorted(threat_medium.keys()):
            target = threat_medium[id]
            debug(f'Hero {hero.id} targeting medium threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # low threat targets
    if len(threat_low.keys()) > 0:
        for id in sorted(threat_low.keys()):
            target = threat_low[id]
            debug(f'Hero {hero.id} targeting low threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # default location
    if NEXT_LOCATION.get(hero.id, None) is None:
        NEXT_LOCATION[hero.id] = 0
    
    target_location = WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]]
    distance_to_target = distance_between(hero.x, hero.y, target_location[0], target_location[1])

    # set next location
    if distance_to_target < 100:
        NEXT_LOCATION[hero.id] += 1

        # wrap around to starting location
        if NEXT_LOCATION[hero.id] >= len(WAITING_SPOTS[base_x]):
            NEXT_LOCATION[hero.id] = 0

    return f'MOVE {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][0]} {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][1]} patrol'

def mixed_strategy(g, hero_id):
    hero = [hero for hero in g['my_heroes'] if hero.id == hero_id][0]
    
    # one of these will be defined
    target = None
    spell = None

    threat_high = {}
    threat_medium = {}
    threat_low = {}
    enemy_heroes = {}

    DISTANCE_THREAT_HIGH = 4000
    DISTANCE_THREAT_MEDIUM = 9000
    HP_MIN_CONTROL = 15
    HP_MIN_SHIELD = 20
    MANA_MIN_SPELL = 29

    # waiting spots
    WAITING_SPOTS = {
        17630: [
            (17630 - 1800, 9000 - 7000),
            (17630 - 4000, 9000 - 3000),
            (17630 - 7000, 9000 - 1800),
            (17630 - 2500, 9000 - 2500),
            # (14000, 4000),
            # (18000, 3500)
        ],
        0: [
            (1800, 7000),
            (4000, 3000),
            (7000, 1800),
            (2500, 2500),
            # (6000, 4000),
            # (7500, 1000)
        ]
    }

    enemy_base_x = 0
    enemy_base_y = 0
    if base_x == 0:
        enemy_base_x = 17630
        enemy_base_y = 9000

    for enemy in g['opp_heroes']:
        distance = distance_between(hero.x, hero.y, enemy.x, enemy.y)
        if distance > RANGE_CONTROL:
            continue

        enemy_heroes[distance] = enemy

    for monster in g['monsters']:
        # ignore monsters outside this strategy radius from base
        distance_from_base = distance_between(base_x, base_y, monster.x, monster.y)
        if distance_from_base > DISTANCE_THREAT_MEDIUM:
            continue

        # targeting priority - mixed
        # - near_base = 1, threat_for = 2
        # - near_base = 0, threat_for = 2

        if monster.threat_for == 1 and monster.near_base == 1:
            threat_high[distance_from_base] = monster

        if monster.threat_for == 1 and monster.near_base == 0:
            threat_medium[distance_from_base] = monster

        if monster.threat_for == 0 and not monster.is_controlled:
            threat_low[distance_from_base] = monster

    if g['my_mana'] >= COST_SPELL:
        # spell casting
        # - distance to base > 5k, but less than 7k and hp above X, control towards enemy base
        # - distance < 5k and len dangerous enemies > 1, wind towards enemy base
        
        # blow away enemy heroes if there is danger in the base
        if len(threat_high.keys()) > 1 and len(enemy_heroes.keys()) > 0:
            distance_from_base = min(enemy_heroes.keys())
            target = enemy_heroes[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if distance_from_hero < RANGE_WIND:
                if base_x == 0:
                    return f'SPELL WIND 17630 9000 woosh!'
                else:
                    return f'SPELL WIND 0 0 woosh!'

        # blow away monsters if more than 1 are in the base
        if len(threat_high.keys()) > 1:
            distance_from_base = min(threat_high.keys())
            target = threat_high[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if distance_from_hero < RANGE_WIND:
                if base_x == 0:
                    return f'SPELL WIND 17630 9000 woosh!'
                else:
                    return f'SPELL WIND 0 0 woosh!'

        # control monsters near the base that will eventually be a problem
        if len(threat_medium.keys()) > 0:
            distance_from_base = min(threat_medium.keys())
            target = threat_medium[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if not target.id in CONTROL_IDS:
                if distance_from_hero < RANGE_CONTROL:
                    if target.health > HP_MIN_CONTROL:
                        if target.is_controlled == 0:
                            if target.shield_life == 0:
                                CONTROL_IDS.append(target.id)

                                if base_x == 0:
                                    debug(target)
                                    return f'SPELL CONTROL {target.id} 17630 9000 that way!'
                                else:
                                    return f'SPELL CONTROL {target.id} 0 0 that way!'

        # control monsters near the base
        if len(threat_low.keys()) > 1:
            distance_from_base = min(threat_low.keys())
            target = threat_low[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if not target.id in CONTROL_IDS:
                if distance_from_hero < RANGE_CONTROL:
                    if target.health > HP_MIN_CONTROL:
                        if target.shield_life == 0:
                            CONTROL_IDS.append(target.id)

                            if base_x == 0:
                                return f'SPELL CONTROL {target.id} 17630 9000 that way!'
                            else:
                                return f'SPELL CONTROL {target.id} 0 0 that way!'

    # attacking
    # - attack threat_high, threat_medium, threat_low
    # - if no defined target, move to waiting spot
    
    # high threat targets
    if len(threat_high.keys()) > 0:
        for id in sorted(threat_high.keys()):
            target = threat_high[id]
            debug(f'Hero {hero.id} targeting high threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # medium threat targets
    if len(threat_medium.keys()) > 0:
        for id in sorted(threat_medium.keys()):
            target = threat_medium[id]
            debug(f'Hero {hero.id} targeting medium threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # low threat targets
    if len(threat_low.keys()) > 0:
        for id in sorted(threat_low.keys()):
            target = threat_low[id]
            debug(f'Hero {hero.id} targeting low threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # default location
    if NEXT_LOCATION.get(hero.id, None) is None:
        NEXT_LOCATION[hero.id] = 0
    
    target_location = WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]]
    distance_to_target = distance_between(hero.x, hero.y, target_location[0], target_location[1])

    # set next location
    if distance_to_target < 100:
        NEXT_LOCATION[hero.id] += 1

        # wrap around to starting location
        if NEXT_LOCATION[hero.id] >= len(WAITING_SPOTS[base_x]):
            NEXT_LOCATION[hero.id] = 0

    return f'MOVE {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][0]} {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][1]} patrol'

def mixed_strategy_1(g, hero_id):
    hero = [hero for hero in g['my_heroes'] if hero.id == hero_id][0]
    
    # one of these will be defined
    target = None
    spell = None

    threat_high = {}
    threat_medium = {}
    threat_low = {}
    enemy_heroes = {}

    DISTANCE_THREAT_HIGH = 4000
    DISTANCE_THREAT_MEDIUM = 9000
    HP_MIN_CONTROL = 15
    HP_MIN_SHIELD = 20
    MANA_MIN_SPELL = 29

    # waiting spots
    WAITING_SPOTS = {
        17630: [
            (17630 - 2000, 9000 - 6000),
            (17630 - 5000, 9000 - 4000),
            (17630 - 6000, 9000 - 2000),
            # (17630 - 2500, 9000 - 2500),
            # (14000, 4000),
            # (20000, 3500)
        ],
        0: [
            (2000, 6000),
            (5000, 4000),
            (6000, 2000),
            # (2500, 2500),
            # (6000, 4000),
            # (7500, 1000)
        ]
    }

    enemy_base_x = 0
    enemy_base_y = 0
    if base_x == 0:
        enemy_base_x = 17630
        enemy_base_y = 9000

    for enemy in g['opp_heroes']:
        distance = distance_between(hero.x, hero.y, enemy.x, enemy.y)
        if distance > RANGE_CONTROL:
            continue

        enemy_heroes[distance] = enemy

    for monster in g['monsters']:
        # ignore monsters outside this strategy radius from base
        distance_from_base = distance_between(base_x, base_y, monster.x, monster.y)
        if distance_from_base > DISTANCE_THREAT_MEDIUM:
            continue

        # targeting priority - mixed
        # - near_base = 1, threat_for = 2
        # - near_base = 0, threat_for = 2

        if monster.threat_for == 1 and monster.near_base == 1:
            threat_high[distance_from_base] = monster

        if monster.threat_for == 1 and monster.near_base == 0:
            threat_medium[distance_from_base] = monster

        if monster.threat_for == 0 and monster.is_controlled == 0:
            threat_low[distance_from_base] = monster

    if g['my_mana'] >= COST_SPELL:
        # spell casting
        # - distance to base > 5k, but less than 7k and hp above X, control towards enemy base
        # - distance < 5k and len dangerous enemies > 1, wind towards enemy base
        
        # blow away enemy heroes if there is danger in the base
        if len(threat_high.keys()) > 1 and len(enemy_heroes.keys()) > 0:
            distance_from_base = min(enemy_heroes.keys())
            target = enemy_heroes[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if distance_from_hero < RANGE_WIND:
                if base_x == 0:
                    return f'SPELL WIND 17630 9000 woosh!'
                else:
                    return f'SPELL WIND 0 0 woosh!'

        # blow away monsters if more than 1 are in the base
        if len(threat_high.keys()) > 1:
            distance_from_base = min(threat_high.keys())
            target = threat_high[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if distance_from_hero < RANGE_WIND:
                if base_x == 0:
                    return f'SPELL WIND 17630 9000 woosh!'
                else:
                    return f'SPELL WIND 0 0 woosh!'

        # control monsters near the base that will eventually be a problem
        if len(threat_medium.keys()) > 0:
            distance_from_base = min(threat_medium.keys())
            target = threat_medium[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if not target.id in CONTROL_IDS:
                if distance_from_hero < RANGE_CONTROL:
                    if target.health > HP_MIN_CONTROL:
                        if target.is_controlled == 0:
                            if target.shield_life == 0:
                                CONTROL_IDS.append(target.id)

                                if base_x == 0:
                                    debug(target)
                                    return f'SPELL CONTROL {target.id} 17630 9000 that way!'
                                else:
                                    return f'SPELL CONTROL {target.id} 0 0 that way!'

        # control monsters near the base
        if len(threat_low.keys()) > 1:
            distance_from_base = min(threat_low.keys())
            target = threat_low[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if not target.id in CONTROL_IDS:
                if distance_from_hero < RANGE_CONTROL:
                    if target.health > HP_MIN_CONTROL:
                        if target.shield_life == 0:
                            CONTROL_IDS.append(target.id)

                            if base_x == 0:
                                return f'SPELL CONTROL {target.id} 17630 9000 that way!'
                            else:
                                return f'SPELL CONTROL {target.id} 0 0 that way!'

    # attacking
    # - attack threat_high, threat_medium, threat_low
    # - if no defined target, move to waiting spot
    
    # high threat targets
    if len(threat_high.keys()) > 0:
        for id in sorted(threat_high.keys()):
            target = threat_high[id]
            debug(f'Hero {hero.id} targeting high threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # medium threat targets
    if len(threat_medium.keys()) > 0:
        for id in sorted(threat_medium.keys()):
            target = threat_medium[id]
            debug(f'Hero {hero.id} targeting medium threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # low threat targets
    if len(threat_low.keys()) > 0:
        for id in sorted(threat_low.keys()):
            target = threat_low[id]
            debug(f'Hero {hero.id} targeting low threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # default location
    if NEXT_LOCATION.get(hero.id, None) is None:
        NEXT_LOCATION[hero.id] = 0
    
    target_location = WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]]
    distance_to_target = distance_between(hero.x, hero.y, target_location[0], target_location[1])

    # set next location
    if distance_to_target < 100:
        NEXT_LOCATION[hero.id] += 1

        # wrap around to starting location
        if NEXT_LOCATION[hero.id] >= len(WAITING_SPOTS[base_x]):
            NEXT_LOCATION[hero.id] = 0

    return f'MOVE {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][0]} {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][1]} patrol'

def offense_strategy(g, hero_id):
    hero = [hero for hero in g['my_heroes'] if hero.id == hero_id][0]
    
    # one of these will be defined
    target = None
    spell = None

    threat_high = {}
    threat_medium = {}
    threat_low = {}
    enemy_heroes = {}

    DISTANCE_THREAT_HIGH = 4000
    DISTANCE_THREAT_MEDIUM = 9000
    HP_MIN_CONTROL = 12
    HP_MIN_SHIELD = 20
    MANA_MIN_SPELL = 29

    # waiting spots
    WAITING_SPOTS = {
        0: [
            (17630 - 1800, 9000 - 7000),
            (17630 - 6000, 9000 - 4000),
            (17630 - 7000, 9000 - 1800),
            (17630 - 2200, 9000 - 2200),
            # (16000, 6000),
            # (18000, 3500)
        ],
        17630: [
            (1800, 7000),
            (6000, 4000),
            (7000, 1800),
            (2200, 2200),
            # (6000, 4000),
            # (7500, 1000)
        ]
    }

    enemy_base_x = 0
    enemy_base_y = 0
    if base_x == 0:
        enemy_base_x = 17630
        enemy_base_y = 9000

    for enemy in g['opp_heroes']:
        distance = distance_between(hero.x, hero.y, enemy.x, enemy.y)
        if distance > RANGE_CONTROL:
            continue

        enemy_heroes[distance] = enemy

    for monster in g['monsters']:
        # ignore monsters outside this strategy radius from base
        distance_from_base = distance_between(enemy_base_x, enemy_base_y, monster.x, monster.y)
        if distance_from_base > DISTANCE_THREAT_MEDIUM:
            continue

        # targeting priority - offense
        # - near_base = 1, threat_for = 2
        # - near_base = 0, threat_for = 2

        if monster.threat_for == 2 and monster.near_base == 1:
            threat_high[distance_from_base] = monster

        if monster.threat_for == 2 and monster.near_base == 0:
            threat_medium[distance_from_base] = monster

        if monster.threat_for == 0 and not monster.is_controlled:
            threat_low[distance_from_base] = monster

    if g['my_mana'] > MANA_MIN_SPELL:
        # spell casting
        # - near_base = 0, threat_for = 2, shield = 0, hp > x, control
        # - near_base = 1, threat_for = 2, shield = 0, is_controlled = 1, shield
        # - distance from enemy base < wind.distance and len dangerous_enemies > 1, wind towards enemy base

        # blast monster into enemy base if they'll go in
        if len(threat_high.keys()) > 0:
            distance_from_base = min(threat_high.keys())
            target = threat_high[distance_from_base]
            distance = distance_between(hero.x, hero.y, target.x, target.y)
            if distance_from_base < 2200:
                if distance < RANGE_WIND:
                    if base_x == 0:
                        return f'SPELL WIND 17630 9000 big woosh!'
                    else:
                        return f'SPELL WIND 0 0 big woosh!'

        # throw shields on a monster if there's a crowd
        if len(threat_high.keys()) > 1:
            distance_from_base = min(threat_high.keys())
            target = threat_high[distance_from_base]
            distance = distance_between(hero.x, hero.y, target.x, target.y)

            if distance < RANGE_SHIELD:
                if target.health > HP_MIN_SHIELD:
                    if target.shield_life == 0:
                        return f'SPELL SHIELD {target.id} boop'

        # blast things towards enemy base if there's a crowd
        if len(threat_high.keys()) > 1:
            distance_from_base = min(threat_high.keys())
            target = threat_high[distance_from_base]
            distance = distance_between(hero.x, hero.y, target.x, target.y)

            if distance < RANGE_WIND:
                if base_x == 0:
                    return f'SPELL WIND 17630 9000 woosh!'
                else:
                    return f'SPELL WIND 0 0 woosh!'

        # control enemy heroes if there are monsters in the base
        if len(threat_high.keys()) > 1 and len(enemy_heroes.keys()) > 0:
            distance_from_base = min(enemy_heroes.keys())
            target = enemy_heroes[distance_from_base]
            distance = distance_between(hero.x, hero.y, target.x, target.y)

            if distance < RANGE_CONTROL:
                if target.shield_life == 0:
                    if base_x == 0:
                        return f'SPELL CONTROL {target.id} 0 0 that way!'
                    else:
                        return f'SPELL CONTROL {target.id} 17630 9000 that way!'
        
        # control low threat targets to move towards enemy base
        if len(threat_low.keys()) > 0:
            distance_from_base = min(threat_low.keys())
            target = threat_low[distance_from_base]
            distance = distance_between(hero.x, hero.y, target.x, target.y)

            if distance < RANGE_CONTROL:
                if target.health > HP_MIN_CONTROL:
                    if target.is_controlled == 0:
                        if base_x == 0:
                            debug(target)
                            return f'SPELL CONTROL {target.id} 17630 9000 that way!'
                        else:
                            return f'SPELL CONTROL {target.id} 0 0 that way!'

    # low threat targets
    if len(threat_low.keys()) > 0:
        for id in sorted(threat_low.keys()):
            target = threat_low[id]
            debug(f'Hero {hero.id} targeting low threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x} {target.y} attack {target.id}'

    # default location
    if NEXT_LOCATION.get(hero.id, None) is None:
        NEXT_LOCATION[hero.id] = 0
    
    target_location = WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]]
    distance_to_target = distance_between(hero.x, hero.y, target_location[0], target_location[1])

    # set next location
    if distance_to_target < 100:
        NEXT_LOCATION[hero.id] += 1

        # wrap around to starting location
        if NEXT_LOCATION[hero.id] >= len(WAITING_SPOTS[base_x]):
            NEXT_LOCATION[hero.id] = 0

    return f'MOVE {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][0]} {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][1]} patrol'

def offense_strategy_1(g, hero_id):
    hero = [hero for hero in g['my_heroes'] if hero.id == hero_id][0]
    
    # one of these will be defined
    target = None
    spell = None

    threat_high = {}
    threat_medium = {}
    threat_low = {}
    enemy_heroes = {}
    monsters_in_wind_range = 0

    DISTANCE_THREAT_HIGH = 4000
    DISTANCE_THREAT_MEDIUM = 9000
    HP_MIN_CONTROL = 17
    HP_MIN_SHIELD = 20
    MANA_MIN_SPELL = 29

    # waiting spots
    WAITING_SPOTS = {
        0: [
            (17630 - 1800, 9000 - 7000),
            (17630 - 6000, 9000 - 4000),
            (17630 - 7000, 9000 - 1800),
            (17630 - 2200, 9000 - 2200),
            # (16000, 6000),
            # (18000, 3500)
        ],
        17630: [
            (1800, 7000),
            (6000, 4000),
            (7000, 1800),
            (2200, 2200),
            # (6000, 4000),
            # (7500, 1000)
        ]
    }

    enemy_base_x = 0
    enemy_base_y = 0
    if base_x == 0:
        enemy_base_x = 17630
        enemy_base_y = 9000

    for enemy in g['opp_heroes']:
        distance = distance_between(hero.x, hero.y, enemy.x, enemy.y)
        if distance > RANGE_CONTROL:
            continue

        enemy_heroes[distance] = enemy

    for monster in g['monsters']:
        # ignore monsters outside this strategy radius from base
        distance_from_base = distance_between(enemy_base_x, enemy_base_y, monster.x, monster.y)
        distance_from_hero = distance_between(hero.x, hero.y, monster.x, monster.y)

        # count the number of monsters in wind range
        if distance_from_hero <= RANGE_WIND:
            monsters_in_wind_range += 1

        if distance_from_base > DISTANCE_THREAT_MEDIUM:
            continue

        # targeting priority - offense
        # - near_base = 1, threat_for = 2
        # - near_base = 0, threat_for = 2

        if monster.threat_for == 2 and monster.near_base == 1:
            threat_high[distance_from_base] = monster

        if monster.threat_for == 2 and monster.near_base == 0:
            threat_medium[distance_from_base] = monster

        if monster.threat_for == 0 and not monster.is_controlled:
            threat_low[distance_from_base] = monster

    if g['my_mana'] > MANA_MIN_SPELL:
        # spell casting
        # - near_base = 0, threat_for = 2, shield = 0, hp > x, control
        # - near_base = 1, threat_for = 2, shield = 0, is_controlled = 1, shield
        # - distance from enemy base < wind.distance and len dangerous_enemies > 1, wind towards enemy base

        # blast monster into enemy base if they'll go in
        if len(threat_high.keys()) > 0:
            distance_from_base = min(threat_high.keys())
            target = threat_high[distance_from_base]
            distance = distance_between(hero.x, hero.y, target.x, target.y)
            if distance_from_base < 2500:
                if distance < RANGE_WIND:
                    if base_x == 0:
                        return f'SPELL WIND 17630 9000 big woosh!'
                    else:
                        return f'SPELL WIND 0 0 big woosh!'

        # throw shields on a monster if there's a crowd
        if len(threat_high.keys()) > 1:
            distance_from_base = min(threat_high.keys())
            target = threat_high[distance_from_base]
            distance = distance_between(hero.x, hero.y, target.x, target.y)

            if distance < RANGE_SHIELD:
                if target.health > HP_MIN_SHIELD:
                    if target.shield_life == 0:
                        return f'SPELL SHIELD {target.id} boop'

        # blast things towards enemy base if there's a crowd
        if monsters_in_wind_range > 2:
            if base_x == 0:
                return f'SPELL WIND 17630 9000 herding spiders!'
            else:
                return f'SPELL WIND 0 0 herding spiders!'

        # if len(threat_high.keys()) > 1:
        #     distance_from_base = min(threat_high.keys())
        #     target = threat_high[distance_from_base]
        #     distance = distance_between(hero.x, hero.y, target.x, target.y)

        #     if distance < RANGE_WIND:
        #         if base_x == 0:
        #             return f'SPELL WIND 17630 9000 woosh!'
        #         else:
        #             return f'SPELL WIND 0 0 woosh!'

        # control enemy heroes if there are monsters in the base
        if len(threat_high.keys()) > 1 and len(enemy_heroes.keys()) > 0:
            distance_from_base = min(enemy_heroes.keys())
            target = enemy_heroes[distance_from_base]
            distance = distance_between(hero.x, hero.y, target.x, target.y)

            if distance < RANGE_CONTROL:
                if target.shield_life == 0:
                    if base_x == 0:
                        return f'SPELL CONTROL {target.id} 0 0 that way!'
                    else:
                        return f'SPELL CONTROL {target.id} 17630 9000 that way!'

        # blast monster into enemy base if they'll go in
        if len(threat_medium.keys()) > 1:
            distance_from_base = min(threat_medium.keys())
            target = threat_medium[distance_from_base]
            distance = distance_between(hero.x, hero.y, target.x, target.y)
            if distance_from_base < 5000:
                if distance < RANGE_WIND:
                    if base_x == 0:
                        return f'SPELL WIND 17630 9000 medium woosh!'
                    else:
                        return f'SPELL WIND 0 0 medium woosh!'

        # blast monster into enemy base if they'll go in
        if len(threat_low.keys()) > 1:
            distance_from_base = min(threat_low.keys())
            target = threat_low[distance_from_base]
            distance = distance_between(hero.x, hero.y, target.x, target.y)
            if distance_from_base < 5000:
                if distance < RANGE_WIND:
                    if base_x == 0:
                        return f'SPELL WIND 17630 9000 smol woosh!'
                    else:
                        return f'SPELL WIND 0 0 smol woosh!'
        
        # control low threat targets to move towards enemy base
        if len(threat_low.keys()) > 0:
            distance_from_base = min(threat_low.keys())
            target = threat_low[distance_from_base]
            distance = distance_between(hero.x, hero.y, target.x, target.y)

            if distance < RANGE_CONTROL:
                if target.health > HP_MIN_CONTROL:
                    if target.is_controlled == 0:
                        if base_x == 0:
                            debug(target)
                            return f'SPELL CONTROL {target.id} 17630 9000 that way!'
                        else:
                            return f'SPELL CONTROL {target.id} 0 0 that way!'

    # low threat targets
    if len(threat_low.keys()) > 0:
        for id in sorted(threat_low.keys()):
            target = threat_low[id]
            debug(f'Hero {hero.id} targeting low threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x} {target.y} attack {target.id}'

    # default location
    if NEXT_LOCATION.get(hero.id, None) is None:
        NEXT_LOCATION[hero.id] = 0
    
    target_location = WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]]
    distance_to_target = distance_between(hero.x, hero.y, target_location[0], target_location[1])

    # set next location
    if distance_to_target < 100:
        NEXT_LOCATION[hero.id] += 1

        # wrap around to starting location
        if NEXT_LOCATION[hero.id] >= len(WAITING_SPOTS[base_x]):
            NEXT_LOCATION[hero.id] = 0

    return f'MOVE {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][0]} {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][1]} patrol'
        
# fights monsters near the base
# doesn't care about using spells
# doesn't care about enemy heroes
# TODO: determine if tank should use WIND
def tank_strat_1(g, hero_id):
    hero = [hero for hero in g['my_heroes'] if hero.id == hero_id][0]
    
    # one of these will be defined
    target = None
    spell = None

    threat_critical = {}
    threat_high = {}
    threat_medium = {}
    threat_low = {}
    enemy_heroes = {}

    DISTANCE_THREAT_HIGH = 4000
    DISTANCE_THREAT_MEDIUM = 8500
    HP_MIN_CONTROL = 17

    # waiting spots
    WAITING_SPOTS = {
        17630: [
            (17630 - 2200, 9000 - 6300),
            (17630 - 4500, 9000 - 4500),
        ],
        0: [
            (2200, 6300),
            (4500, 4500),
        ]
    }

    for enemy in g['opp_heroes']:
        distance = distance_between(hero.x, hero.y, enemy.x, enemy.y)
        if distance > RANGE_CONTROL:
            continue

        enemy_heroes[distance] = enemy

    for monster in g['monsters']:
        # ignore monsters outside this strategy radius from base
        distance_from_base = distance_between(base_x, base_y, monster.x, monster.y)
        if distance_from_base > DISTANCE_THREAT_MEDIUM:
            continue

        # distance = distance_between(hero.x, hero.y, monster.x, monster.y)

        # targeting priority - defenders
        # - near_base = 1, threat_for = 1
        # - near_base = 0, threat_for = 1

        if monster.threat_for == 1 and monster.near_base == 1:
            threat_high[distance_from_base] = monster

            if monster.shield_life > 0:
                threat_critical[distance_from_base] = monster

        if monster.threat_for == 1 and monster.near_base == 0:
            threat_medium[distance_from_base] = monster

        if monster.threat_for == 0:
            threat_low[distance_from_base] = monster

    if g['my_mana'] >= COST_SPELL:
        # if there are critical threats and an enemy hero present, shield the support
        if len(threat_critical.keys()) > 0 and len(enemy_heroes.keys()) > 0:
            support = [hero for hero in g['my_heroes'] if hero.id in [2, 5]][0]
            if support.shield_life == 0:
                distance_from_support = distance_between(hero.x, hero.y, support.x, support.y)
                if distance_from_support < RANGE_SHIELD:
                    return f'SPELL SHIELD {support.id} bubble'

        # if there are critical threats and an enemy hero present, shield yourself
        if len(threat_critical.keys()) > 0 and len(enemy_heroes.keys()) > 0:
            if hero.shield_life == 0:
                return f'SPELL SHIELD {hero.id} bubble'

        # blow away monsters and enemy heroes if there is danger in the base - don't let them dunk on us
        if len(threat_high.keys()) > 0 and len(enemy_heroes.keys()) > 0:
            distance_from_base = min(threat_high.keys())
            target = threat_high[distance_from_base]
            if target.shield_life == 0:
                distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)
                if distance_from_base < 2600:
                    if distance_from_hero < RANGE_WIND:
                        if base_x == 0:
                            return f'SPELL WIND 17630 9000 woosh!'
                        else:
                            return f'SPELL WIND 0 0 woosh!'

        # blow away monsters and enemy heroes if there is danger in the base
        if len(threat_high.keys()) > 0:
            distance_from_base = min(threat_high.keys())
            target = threat_high[distance_from_base]
            if target.shield_life == 0:
                distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)
                if distance_from_base < 1000:
                    if distance_from_hero < RANGE_WIND:
                        if base_x == 0:
                            return f'SPELL WIND 17630 9000 woosh!'
                        else:
                            return f'SPELL WIND 0 0 woosh!'

    # # shielded enemy in the base, have to fight it - not always true, needs to fight the closest to base
    # if len(threat_critical.keys()) > 0 and len(threat_critical.keys()) == len(threat_high.keys()):
    #     for id in sorted(threat_critical.keys()):
    #         target = threat_critical[id]
    #         distance = distance_between(hero.x, hero.y, target.x, target.y)
    #         distance_to_base = id - 300
    #         turns_to_base = math.floor(distance_to_base / 400)
    #         turns_to_engage = math.ceil(distance / 800)
    #         turns_to_kill = target.health / 2
    #         can_kill_alone = False
    #         if turns_to_engage + turns_to_kill < turns_to_base:
    #             can_kill_alone = True

    #         debug(f'Hero {hero.id} targeting critical threat enemy {target.id} at {target.x}, {target.y}, can_kill_alone = {can_kill_alone}')
    #         return f'MOVE {target.x} {target.y} attack {target.id}'

    # high threat targets
    if len(threat_high.keys()) > 0:
        for id in sorted(threat_high.keys()):
            target = threat_high[id]
            distance = distance_between(hero.x, hero.y, target.x, target.y)
            distance_to_base = id - 300
            turns_to_base = math.floor(distance_to_base / 400)
            turns_to_engage = math.ceil(distance / 800)
            turns_to_kill = target.health / 2
            can_kill_alone = False
            if turns_to_engage + turns_to_kill < turns_to_base:
                can_kill_alone = True

            debug(f'Hero {hero.id} targeting high threat enemy {target.id} at {target.x}, {target.y}, can_kill_alone = {can_kill_alone}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # medium threat targets
    if len(threat_medium.keys()) > 0:
        for id in sorted(threat_medium.keys()):
            target = threat_medium[id]
            distance = distance_between(hero.x, hero.y, target.x, target.y)
            distance_to_base = id - 300
            turns_to_base = math.floor(distance_to_base / 400)
            turns_to_engage = math.ceil(distance / 800)
            turns_to_kill = target.health / 2
            can_kill_alone = False
            if turns_to_engage + turns_to_kill < turns_to_base:
                can_kill_alone = True

            debug(f'Hero {hero.id} targeting medium threat enemy {target.id} at {target.x}, {target.y}, can_kill_alone = {can_kill_alone}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # low threat targets
    if len(threat_low.keys()) > 0:
        for id in sorted(threat_low.keys()):
            target = threat_low[id]
            debug(f'Hero {hero.id} targeting low threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # default location
    if NEXT_LOCATION.get(hero.id, None) is None:
        NEXT_LOCATION[hero.id] = 0
    
    target_location = WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]]
    distance_to_target = distance_between(hero.x, hero.y, target_location[0], target_location[1])

    # set next location
    if distance_to_target < 100:
        NEXT_LOCATION[hero.id] += 1

        # wrap around to starting location
        if NEXT_LOCATION[hero.id] >= len(WAITING_SPOTS[base_x]):
            NEXT_LOCATION[hero.id] = 0

    return f'MOVE {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][0]} {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][1]} patrol'

# fights monsters near base
# attempts to deal with enemy hero offense
# shields tank hero
def support_strat_1(g, hero_id):
    hero = [hero for hero in g['my_heroes'] if hero.id == hero_id][0]
    
    # one of these will be defined
    target = None
    spell = None

    threat_critical = {}
    threat_high = {}
    threat_medium = {}
    threat_low = {}
    enemy_heroes = {}

    DISTANCE_THREAT_HIGH = 4000
    DISTANCE_THREAT_MEDIUM = 9000
    HP_MIN_CONTROL = 14
    HP_MIN_SHIELD = 20
    MANA_MIN_SPELL = 29

    # waiting spots
    WAITING_SPOTS = {
        17630: [
            (17630 - 5200, 9000 - 4000),
            (17630 - 7300, 9000 - 2200),
        ],
        0: [
            (5200, 4000),
            (7300, 2200),
        ]
    }

    enemy_base_x = 0
    enemy_base_y = 0
    if base_x == 0:
        enemy_base_x = 17630
        enemy_base_y = 9000

    for enemy in g['opp_heroes']:
        distance = distance_between(hero.x, hero.y, enemy.x, enemy.y)
        if distance > RANGE_CONTROL:
            continue

        enemy_heroes[distance] = enemy

    for monster in g['monsters']:
        # ignore monsters outside this strategy radius from base
        distance_from_base = distance_between(base_x, base_y, monster.x, monster.y)
        if distance_from_base > DISTANCE_THREAT_MEDIUM:
            continue

        # targeting priority - mixed
        # - near_base = 1, threat_for = 2
        # - near_base = 0, threat_for = 2

        if monster.threat_for == 1 and monster.near_base == 1:
            threat_high[distance_from_base] = monster

            if monster.shield_life > 0:
                threat_critical[distance_from_base] = monster

        if monster.threat_for == 1 and monster.near_base == 0:
            threat_medium[distance_from_base] = monster

        if monster.threat_for == 0 and monster.is_controlled == 0:
            threat_low[distance_from_base] = monster

    if g['my_mana'] >= COST_SPELL:
        # if there are critical threats and an enemy hero present, shield the tank
        if len(threat_critical.keys()) > 0 and len(enemy_heroes.keys()) > 0:
            tank = [hero for hero in g['my_heroes'] if hero.id in [2, 5]][0]
            if tank.shield_life == 0:
                distance_from_tank = distance_between(hero.x, hero.y, tank.x, tank.y)
                if distance_from_tank < RANGE_SHIELD:
                    return f'SPELL SHIELD {tank.id} bubble'

        # # if there are critical threats and an enemy hero present, shield yourself
        # if len(threat_critical.keys()) > 0 and len(enemy_heroes.keys()) > 0:
        #     if hero.shield_life == 0:
        #         return f'SPELL SHIELD {hero.id} bubble'

        # if there are high threats and an enemy hero present, control the hero away
        if len(threat_high.keys()) > 0 and len(enemy_heroes.keys()) > 0:
            enemy = enemy_heroes[min(enemy_heroes.keys())]
            if enemy.shield_life == 0:
                return f'SPELL CONTROL {enemy.id} {enemy_base_x} {enemy_base_y} shoo'

        # if there are high threats and an enemy hero present, shield the tank
        if len(threat_high.keys()) > 0 and len(enemy_heroes.keys()) > 0:
            tank = [hero for hero in g['my_heroes'] if hero.id in [2, 5]][0]
            if tank.shield_life == 0:
                distance_from_tank = distance_between(hero.x, hero.y, tank.x, tank.y)
                if distance_from_tank < RANGE_SHIELD:
                    return f'SPELL SHIELD {tank.id} bubble'

        # blow away monsters and enemy heroes if there is danger in the base
        if len(threat_high.keys()) > 1 and len(enemy_heroes.keys()) > 0:
            distance_from_base = min(enemy_heroes.keys())
            target = enemy_heroes[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if distance_from_hero < RANGE_WIND:
                if base_x == 0:
                    return f'SPELL WIND 17630 9000 woosh!'
                else:
                    return f'SPELL WIND 0 0 woosh!'

        # blow away monsters if more than 1 are in the base
        if len(threat_high.keys()) > 1:
            distance_from_base = min(threat_high.keys())
            target = threat_high[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if distance_from_hero < RANGE_WIND:
                if base_x == 0:
                    return f'SPELL WIND 17630 9000 woosh!'
                else:
                    return f'SPELL WIND 0 0 woosh!'

        # control monsters near the base that will eventually be a problem
        if len(threat_medium.keys()) > 0:
            distance_from_base = min(threat_medium.keys())
            target = threat_medium[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if not target.id in CONTROL_IDS:
                if distance_from_hero < RANGE_CONTROL:
                    if target.health > HP_MIN_CONTROL:
                        if target.is_controlled == 0:
                            if target.shield_life == 0:
                                CONTROL_IDS.append(target.id)

                                if base_x == 0:
                                    debug(target)
                                    return f'SPELL CONTROL {target.id} 17630 9000 that way!'
                                else:
                                    return f'SPELL CONTROL {target.id} 0 0 that way!'

        # control monsters near the base
        if len(threat_low.keys()) > 1:
            distance_from_base = min(threat_low.keys())
            target = threat_low[distance_from_base]
            distance_from_hero = distance_between(hero.x, hero.y, target.x, target.y)

            if not target.id in CONTROL_IDS:
                if distance_from_hero < RANGE_CONTROL:
                    if target.health > HP_MIN_CONTROL:
                        if target.shield_life == 0:
                            CONTROL_IDS.append(target.id)

                            if base_x == 0:
                                return f'SPELL CONTROL {target.id} 17630 9000 that way!'
                            else:
                                return f'SPELL CONTROL {target.id} 0 0 that way!'

    # attacking
    # - attack threat_high, threat_medium, threat_low
    # - if no defined target, move to waiting spot
    
    # critical threat targets
    if len(threat_critical.keys()) > 0:
        for id in sorted(threat_critical.keys()):
            target = threat_critical[id]
            debug(f'Hero {hero.id} targeting critical threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # high threat targets
    if len(threat_high.keys()) > 0:
        for id in sorted(threat_high.keys()):
            target = threat_high[id]
            debug(f'Hero {hero.id} targeting high threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # medium threat targets
    if len(threat_medium.keys()) > 0:
        for id in sorted(threat_medium.keys()):
            target = threat_medium[id]
            debug(f'Hero {hero.id} targeting medium threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # low threat targets
    if len(threat_low.keys()) > 0:
        for id in sorted(threat_low.keys()):
            target = threat_low[id]
            debug(f'Hero {hero.id} targeting low threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x + target.vx} {target.y + target.vy} attack {target.id}'

    # default location
    if NEXT_LOCATION.get(hero.id, None) is None:
        NEXT_LOCATION[hero.id] = 0
    
    target_location = WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]]
    distance_to_target = distance_between(hero.x, hero.y, target_location[0], target_location[1])

    # set next location
    if distance_to_target < 100:
        NEXT_LOCATION[hero.id] += 1

        # wrap around to starting location
        if NEXT_LOCATION[hero.id] >= len(WAITING_SPOTS[base_x]):
            NEXT_LOCATION[hero.id] = 0

    return f'MOVE {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][0]} {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][1]} patrol'

# fights monsters near enemy base that are low threat to the enemy
# tries to push spiders into enemy base
# shields spiders in the enemy base
# controls enemy defenders
# TODO: track when controlled spiders should reach the enemy
def dps_strat_1(g, hero_id):
    hero = [hero for hero in g['my_heroes'] if hero.id == hero_id][0]
    
    # one of these will be defined
    target = None
    spell = None

    threat_high = {}
    threat_medium = {}
    threat_low = {}
    enemy_heroes = {}
    monsters_in_wind_range = 0

    DISTANCE_THREAT_HIGH = 4000
    DISTANCE_THREAT_MEDIUM = 9000
    HP_MIN_CONTROL = 17
    HP_MIN_SHIELD = 18
    MANA_MIN_SPELL = 29

    # waiting spots
    WAITING_SPOTS = {
        17630: [
            (17630 - 15630, 9000 - 2200),
            (17630 - 10000, 9000 - 6200),
            (17630 - 15630, 9000 - 7000),
        ],
        0: [
            (15630, 2200),
            (10000, 6200),
            (15630, 7000),
        ]
    }

    enemy_base_x = 0
    enemy_base_y = 0
    if base_x == 0:
        enemy_base_x = 17630
        enemy_base_y = 9000

    for enemy in g['opp_heroes']:
        distance = distance_between(hero.x, hero.y, enemy.x, enemy.y)
        if distance > RANGE_CONTROL:
            continue

        enemy_heroes[distance] = enemy

    for monster in g['monsters']:
        # ignore monsters outside this strategy radius from base
        distance_from_base = distance_between(enemy_base_x, enemy_base_y, monster.x, monster.y)
        distance_from_hero = distance_between(hero.x, hero.y, monster.x, monster.y)

        # count the number of monsters in wind range
        if distance_from_hero <= RANGE_WIND:
            monsters_in_wind_range += 1

        if distance_from_base > DISTANCE_THREAT_MEDIUM:
            continue

        # targeting priority - offense
        # - near_base = 1, threat_for = 2
        # - near_base = 0, threat_for = 2

        if monster.threat_for == 2 and monster.near_base == 1:
            threat_high[distance_from_base] = monster

        if monster.threat_for == 2 and monster.near_base == 0:
            threat_medium[distance_from_base] = monster

        if monster.threat_for == 0 and not monster.is_controlled:
            threat_low[distance_from_base] = monster

    # TODO: somewhere in here, determine if the unit should continue moving towards the enemy base
    moves_toward_enemy_base = MOVE_TO_ENEMY_BASE.get(hero.id, 0)
    if moves_toward_enemy_base > 0:
        MOVE_TO_ENEMY_BASE[hero.id] = moves_toward_enemy_base - 1
        debug(f'{hero.id} moving to enemy base')
        return f'MOVE {enemy_base_x} {enemy_base_y} move to base'

    if g['my_mana'] > MANA_MIN_SPELL:
        # spell casting
        # - near_base = 0, threat_for = 2, shield = 0, hp > x, control
        # - near_base = 1, threat_for = 2, shield = 0, is_controlled = 1, shield
        # - distance from enemy base < wind.distance and len dangerous_enemies > 1, wind towards enemy base

        # blast monster into enemy base if they'll go in
        if len(threat_high.keys()) > 0:
            distance_from_base = min(threat_high.keys())
            target = threat_high[distance_from_base]
            distance = distance_between(hero.x, hero.y, target.x, target.y)
            if distance_from_base < 2500:
                if distance < RANGE_WIND:
                    MOVE_TO_ENEMY_BASE[hero.id] = 2
                    debug(f'move to base {hero.id} = True')

                    if base_x == 0:
                        return f'SPELL WIND 17630 9000 big woosh!'
                    else:
                        return f'SPELL WIND 0 0 big woosh!'
                else:
                    debug(f'Hero {hero.id} following high threat enemy for wind {target.id} at {target.x - (2 * target.vx)}, {target.y - (2 * target.vy)}')
                    return f'MOVE {target.x - (2 * target.vx)} {target.y - (2 * target.vy)} follow {target.id}'
            elif distance_from_base < 4000:
                debug(f'Hero {hero.id} following high threat enemy to base {target.id} at {target.x - (2 * target.vx)}, {target.y - (2 * target.vy)}')
                return f'MOVE {target.x - (2 * target.vx)} {target.y - (2 * target.vy)} follow {target.id}'

        # throw shields on a monster if there's a crowd
        if len(threat_high.keys()) > 0 and len(enemy_heroes.keys()) > 0:
            distance_from_base = min(threat_high.keys())
            target = threat_high[distance_from_base]
            distance = distance_between(hero.x, hero.y, target.x, target.y)

            if distance < RANGE_SHIELD:
                if target.health > HP_MIN_SHIELD:
                    if target.shield_life == 0:
                        return f'SPELL SHIELD {target.id} boop'

        # blast things towards enemy base if there's a crowd
        # TODO: follow them
        if monsters_in_wind_range > 1:
            # make a note to move towards the enemy base for 2 turns
            # wind range is 2200, after 2 turns he should be in range again
            MOVE_TO_ENEMY_BASE[hero.id] = 2
            debug(f'move to base {hero.id} = True')

            if base_x == 0:
                return f'SPELL WIND 17630 9000 herding spiders!'
            else:
                return f'SPELL WIND 0 0 herding spiders!'

        # if len(threat_high.keys()) > 1:
        #     distance_from_base = min(threat_high.keys())
        #     target = threat_high[distance_from_base]
        #     distance = distance_between(hero.x, hero.y, target.x, target.y)

        #     if distance < RANGE_WIND:
        #         if base_x == 0:
        #             return f'SPELL WIND 17630 9000 woosh!'
        #         else:
        #             return f'SPELL WIND 0 0 woosh!'

        # control enemy heroes if there are monsters in the base
        if len(threat_high.keys()) > 0 and len(enemy_heroes.keys()) > 0:
            distance_from_base = min(enemy_heroes.keys())
            target = enemy_heroes[distance_from_base]
            distance = distance_between(hero.x, hero.y, target.x, target.y)

            if distance < RANGE_CONTROL:
                if target.shield_life == 0:
                    if base_x == 0:
                        return f'SPELL CONTROL {target.id} 0 0 that way!'
                    else:
                        return f'SPELL CONTROL {target.id} 17630 9000 that way!'

        # blast monster into enemy base if they'll go in
        if len(threat_medium.keys()) > 0:
            distance_from_base = min(threat_medium.keys())
            target = threat_medium[distance_from_base]
            distance = distance_between(hero.x, hero.y, target.x, target.y)
            if distance_from_base < 7000:
                if distance < RANGE_WIND:
                    MOVE_TO_ENEMY_BASE[hero.id] = 2
                    debug(f'move to base {hero.id} = True')

                    if base_x == 0:
                        return f'SPELL WIND 17630 9000 medium woosh!'
                    else:
                        return f'SPELL WIND 0 0 medium woosh!'

        # blast monster into enemy base if they'll go in
        if len(threat_low.keys()) > 0:
            distance_from_base = min(threat_low.keys())
            target = threat_low[distance_from_base]
            distance = distance_between(hero.x, hero.y, target.x, target.y)
            if distance_from_base < 7000:
                if distance < RANGE_WIND:
                    MOVE_TO_ENEMY_BASE[hero.id] = 2
                    debug(f'move to base {hero.id} = True')

                    if base_x == 0:
                        return f'SPELL WIND 17630 9000 smol woosh!'
                    else:
                        return f'SPELL WIND 0 0 smol woosh!'
        
        # control low threat targets to move towards enemy base
        if len(threat_low.keys()) > 0:
            distance_from_base = min(threat_low.keys())
            target = threat_low[distance_from_base]
            distance = distance_between(hero.x, hero.y, target.x, target.y)

            if distance < RANGE_CONTROL:
                if target.health > HP_MIN_CONTROL:
                    if target.is_controlled == 0:
                        if base_x == 0:
                            debug(target)
                            return f'SPELL CONTROL {target.id} 17630 9000 that way!'
                        else:
                            return f'SPELL CONTROL {target.id} 0 0 that way!'

    # low threat targets
    if len(threat_low.keys()) > 0:
        for id in sorted(threat_low.keys()):
            target = threat_low[id]
            debug(f'Hero {hero.id} targeting low threat enemy {target.id} at {target.x}, {target.y}')
            return f'MOVE {target.x} {target.y} attack {target.id}'

    # default location
    if NEXT_LOCATION.get(hero.id, None) is None:
        NEXT_LOCATION[hero.id] = 0
    
    target_location = WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]]
    distance_to_target = distance_between(hero.x, hero.y, target_location[0], target_location[1])

    # set next location
    if distance_to_target < 100:
        NEXT_LOCATION[hero.id] += 1

        # wrap around to starting location
        if NEXT_LOCATION[hero.id] >= len(WAITING_SPOTS[base_x]):
            NEXT_LOCATION[hero.id] = 0

    return f'MOVE {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][0]} {WAITING_SPOTS[base_x][NEXT_LOCATION[hero.id]][1]} patrol'

Entity = namedtuple('Entity', [
    'id', 'type', 'x', 'y', 'shield_life', 'is_controlled', 'health', 'vx', 'vy', 'near_base', 'threat_for'
])

TYPE_MONSTER = 0
TYPE_MY_HERO = 1
TYPE_OP_HERO = 2

COST_SPELL = 10
RANGE_WIND = 1280
RANGE_SHIELD = 2200
RANGE_CONTROL = 2200

# strategy per unit id
# heroes always start as 0-2 or 3-5 depending on team
STRATEGY = {
    0: 'OFFENSE',
    1: 'MIXED',
    2: 'DEFENSE',
    3: 'OFFENSE',
    4: 'MIXED',
    5: 'DEFENSE'
}

MAX_DISTANCE = {
    0: 5000,
    1: 6000,
    2: 7000
}

# holds location that the hero should reach next when looking for targets
# - hero.id: index in WAITING_SPOTS {0: 1}
NEXT_LOCATION = {}

# This is gross, but if hero.id: number, this hero should move towards the enemy base this number of turns
MOVE_TO_ENEMY_BASE = {}

# holds the ID of any monsters or heroes controlled on this turn
CONTROL_IDS = []

# base_x,base_y: The corner of the map representing your base
base_x, base_y = [int(i) for i in input().split()]

# always 3
heroes_per_player = int(input())

# game loop
while True:
    my_health, my_mana = [int(j) for j in input().split()]
    enemy_health, enemy_mana = [int(j) for j in input().split()]
    entity_count = int(input())  # Amount of heroes and monsters you can see

    monsters = []
    my_heroes = []
    opp_heroes = []

    current_targets = []
    CONTROL_IDS = []

    for i in range(entity_count):
        _id, _type, x, y, shield_life, is_controlled, health, vx, vy, near_base, threat_for = [int(j) for j in input().split()]
        entity = Entity(
            _id,            # _id: Unique identifier
            _type,          # _type: 0=monster, 1=your hero, 2=opponent hero
            x, y,           # x,y: Position of this entity
            shield_life,    # shield_life: Ignore for this league; Count down until shield spell fades
            is_controlled,  # is_controlled: Ignore for this league; Equals 1 when this entity is under a control spell
            health,         # health: Remaining health of this monster
            vx, vy,         # vx,vy: Trajectory of this monster
            near_base,      # near_base: 0=monster with no target yet, 1=monster targeting a base
            threat_for      # threat_for: Given this monster's trajectory, is it a threat to 1=your base, 2=your opponent's base, 0=neither
        )
        
        if _type == TYPE_MONSTER:
            monsters.append(entity)
        elif _type == TYPE_MY_HERO:
            my_heroes.append(entity)
        elif _type == TYPE_OP_HERO:
            opp_heroes.append(entity)

    game_state = {}
    game_state['monsters'] = monsters
    game_state['my_heroes'] = my_heroes
    game_state['opp_heroes'] = opp_heroes
    game_state['my_health'] = my_health
    game_state['my_mana'] = my_mana
    game_state['enemy_health'] = enemy_health
    game_state['enemy_mana'] = enemy_mana

    for hero in my_heroes:
        if STRATEGY[hero.id] == 'DEFENSE':
            print(tank_strat_1(game_state, hero.id))
        elif STRATEGY[hero.id] == 'OFFENSE':
            print(dps_strat_1(game_state, hero.id))
        elif STRATEGY[hero.id] == 'MIXED':
            print(support_strat_1(game_state, hero.id))
        else:
            print(f'MOVE {base_x} {base_y} whoops')
