import sys
import math
import numpy as np

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

# helper methods
def debug(msg):
    print(str(msg), file=sys.stderr)

# game loop
while True:
    action_count = int(input())  # the number of spells and recipes in play
    
    debug('action_count')
    debug(action_count)
    debug('--------')

    BREWS = {}
    SPELLS = {}
    INVENTORY = None

    for i in range(action_count):
        # action_id: the unique ID of this spell or recipe
        # action_type: in the first league: BREW; later: CAST, OPPONENT_CAST, LEARN, BREW
        # delta_0: tier-0 ingredient change
        # delta_1: tier-1 ingredient change
        # delta_2: tier-2 ingredient change
        # delta_3: tier-3 ingredient change
        # price: the price in rupees if this is a potion
        # tome_index: in the first two leagues: always 0; later: the index in the tome if this is a tome spell, equal to the read-ahead tax
        # tax_count: in the first two leagues: always 0; later: the amount of taxed tier-0 ingredients you gain from learning this spell
        # castable: in the first league: always 0; later: 1 if this is a castable player spell
        # repeatable: for the first two leagues: always 0; later: 1 if this is a repeatable player spell        

        action_id, action_type, delta_0, delta_1, delta_2, delta_3, price, tome_index, tax_count, castable, repeatable = input().split()
        action_id = int(action_id)
        delta_0 = int(delta_0)
        delta_1 = int(delta_1)
        delta_2 = int(delta_2)
        delta_3 = int(delta_3)
        price = int(price)
        tome_index = int(tome_index)
        tax_count = int(tax_count)
        castable = castable != "0"
        repeatable = repeatable != "0"

        debug('actions')
        debug(f'{action_id}, {action_type}, {delta_0}, {delta_1}, {delta_2}, {delta_3}, {price}, {tome_index}, {tax_count}, {castable}, {repeatable}, ')
        debug('--------')

        if action_type == 'BREW':
            BREWS[action_id] = {
                'ingredients': np.array([delta_0, delta_1, delta_2, delta_3]),
                'price': price
            }
        elif action_type == 'CAST':
            if castable:
                SPELLS[action_id] = {
                    'ingredients': np.array([delta_0, delta_1, delta_2, delta_3])
                }

    for i in range(2):
        # inv_0: tier-0 ingredients in inventory
        # score: amount of rupees
        # YOUR DATA IS ALWAYS FIRST
        inv_0, inv_1, inv_2, inv_3, score = [int(j) for j in input().split()]
        if i == 0:
            INVENTORY = np.array([inv_0, inv_1, inv_2, inv_3])

    debug('brews')
    debug(BREWS)
    debug('--------')  

    debug('spells')
    debug(SPELLS)
    debug('--------')  

    debug('inventory')
    debug(INVENTORY)
    debug('--------')      

    CAN_BREW = {}
    CAN_CAST = {}

    for i in BREWS.keys():
        brew = BREWS[i]
        inv_remaining = np.add(INVENTORY, brew['ingredients'])
        
        # can we make it
        can_brew = True
        for j in range(0, len(inv_remaining)):
            if inv_remaining[j] < 0:
                can_brew = False
                break
        
        if can_brew:
            CAN_BREW[brew['price']] = i

    for i in SPELLS.keys():
        spell = SPELLS[i]
        inv_remaining = np.add(INVENTORY, spell['ingredients'])
        
        # can we make it
        can_cast = True
        for j in range(0, len(inv_remaining)):
            if inv_remaining[j] < 0:
                # too expensive
                can_cast = False
                break
            elif np.sum(inv_remaining) > 10:
                # not enough room in inventory
                can_cast = False
                break
            elif np.max(inv_remaining) > 5:
                # we would have more than 5 of a single item
                can_cast = False
                break
        
        if can_cast:
            value = np.sum(inv_remaining)
            CAN_CAST[value] = i

    debug('can_brew')
    debug(CAN_BREW)
    debug('--------')  

    debug('can_cast')
    debug(CAN_CAST)
    debug('--------')  

    # pick the best brew
    # sort them by price/cost?
    # always go for highest price?
    if len(CAN_BREW.keys()) > 0:
        item_to_brew = CAN_BREW[max(CAN_BREW.keys())]
        print(f'BREW {item_to_brew}')
    elif len(CAN_CAST.keys()) > 0:
        spell_to_cast = CAN_CAST[max(CAN_CAST.keys())]
        print(f'CAST {spell_to_cast}')
    else:
        print('REST')

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)


    # in the first league: BREW <id> | WAIT; 
    # later: BREW <id> | CAST <id> [<times>] | LEARN <id> | REST | WAIT
    # print("BREW 0")
