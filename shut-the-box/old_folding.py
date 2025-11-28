import numpy as np
import net
from net import possibleNets
from prism import startingPrisms
from copy import deepcopy

import argparse
import logging

DIRECTIONS = {'north': ['north', 'east', 'west', 'south'],
                   'east': ['east', 'north', 'south', 'west'],
                   'west': ['west', 'north', 'south', 'east'],
                   'south': ['south', 'east', 'west', 'north'],
                   None: ['east', 'north', 'west', 'south']}

OPPOSITE_DIRECTION = {'east':'west', 'west':'east', 'north':'south', 'south':'north'}

DUMB = False

# net is a Net from net.py
# prism is a Prism from prism.py
# prism orientation (other than translation) with respect to the net is fixed
def netFoldsToPrism(net, prism):
    _Q = prism.perimiter
    _P = net.points_np # TODO use points along boundary of net
    len_P = len(_P)
    for i, p in enumerate(_P):
        print('{:3}/{:3}'.format(i+1, len_P))
        for q in _Q:
            starting_point = p - q
            if DUMB and tuple(starting_point) != (6,13,0):
                continue
            
            prism.translate(starting_point)

            face_mapping = {frozenset(f): None for f in prism.orig_face_tuples}

            logging.debug("\n"*4)
            logging.debug(f'START POINT = {starting_point}, DIMENSIONS = {prism.dimensions}')

            rollPrism(prism, face_mapping, net, 0, None, None)

            num_filled = 0
            for face, cell in face_mapping.items():
                if cell is not None:
                    num_filled += 1
            print(f'found: {num_filled}/{len(face_mapping)}')

            # reset position (prism returns to where it started after it rolls)
            prism.translate(-starting_point)
            
            if None not in face_mapping.values():
                print('\nSOLUTION FOUND')
                print(f'starting_point = {starting_point}')
                return face_mapping
            if DUMB:
                return None
    return None

# Do DFS traversal of net by tipping prism in orthogonal directions, stamping the prism
# faces which land on the net as we roll. If by the end of this traversal every face of
# the prism is filled, then the net can actually fold into the prism.
def rollPrism(prism, mapping, net, depth, pp_direc, p_direc):
    # stamp
    downFaces = prism.heightZeroToOrigFaces()
    
    # none of the down faces are part of the net; return unsuccessfully    
    if not any(map(lambda dface: dface in net.cells, downFaces)):
        revertRoll(prism, pp_direc, p_direc)
        return

    cells = net.cells

    to_add = {} # key_face, cell dictionary of squares to add

    canStamp = True
    for down_face, key_face in downFaces.items():
        if down_face not in cells:
            continue
        elif mapping[key_face] is None and cells[down_face] not in mapping.values():
            to_add[key_face] = cells[down_face]
        else:
            canStamp = False
            break
    else:
        assert canStamp, "we should be able to stamp"
        logging.debug(f'ADDING {len(to_add)} FACE(S)...')
        for key_face, cell in to_add.items():
            logging.debug(f'{cell.position} {cell.number}')
            mapping[key_face] = cell

    if not canStamp:
        revertRoll(prism, pp_direc, p_direc)
        return
            
    # for down_face, key_face in downFaces.items():
    #     # ignore faces which are not a part of the net
    #     if down_face not in net.cells: 
    #         continue

    #     # after here, only considering faces which are part of the net

    #     elif mapping[key_face] == net.cells[down_face]:
    #         revertRoll(prism, pp_direc, p_direc)
    #         return

    #     # down face is part of the net but not part of the mapping
    #     # elif mapping[key_face] is None and net.cells[down_face] not in mapping.values():
    #     elif net.cells[down_face] not in mapping.values():
    #         logging.debug(f'added: {net.cells[down_face].position} {net.cells[down_face].number}')
    #         mapping[key_face] = net.cells[down_face]

    #     # down face is part of the net but already part of mapping;
    #     # we can only stamp each face once, so return usuccessfully
    #     else:
    #         revertRoll(prism, pp_direc, p_direc)    
    #         return 

    # mapping complete; return successfully
    if None not in mapping.values():
        logging.debug('Solution already found'.upper())
        revertRoll(prism, pp_direc, p_direc)        
        return 

    logging.debug('')
    
    pp_d = pp_direc.upper() if pp_direc else pp_direc
    p_d = p_direc.upper() if p_direc else p_direc    

    # roll
    for next_direc in DIRECTIONS[p_direc]:
        logging.debug('{:8s} {:6s}... D = {:2} p_d = {}'.format('tipping', next_direc.upper(), depth, p_d))
        prism.tip(next_direc)
        rollPrism(prism, mapping, net, depth+1, p_direc, next_direc)

def revertRoll(prism, pp_direc, p_direc):
    opp = OPPOSITE_DIRECTION[p_direc] if p_direc else None
    
    # do not tip back if we've exhausted all directions and are now retracing steps
    if pp_direc == opp: 
        return
    else:
        prism.tip(opp)

def numbersOnSides(prism, mapping):
    sides = {i : [] for i in prism.sides}
    for side, faces in prism.sides.items():
        for face in faces:
            number = mapping[face].number
            if number:
                sides[side].append(number)
    return sides

def answer(numbers_on_sides):
    prod = 1
    for side, nums in numbers_on_sides.items():
        prod *= sum(nums)
    return prod

def assembleBox(net):
    solutions = []
    surface_area = len(net.cells)
    starting_prisms = startingPrisms(surface_area)
    
    logging.debug('assemble box start'.upper())

    prism_i = 1
    n_starting_prisms = len(starting_prisms)
    for dimensions, prisms in starting_prisms.items():
        print(f'{prism_i}/{n_starting_prisms}')
        prism_i += 1
        print('dimensions:', dimensions, 'len(prisms):', len(prisms))
        if DUMB and set(dimensions) != {2, 6, 7}:
            continue
        len_prisms = len(prisms)
        for i, prism in enumerate(prisms):
            if DUMB and prism.dimensions != (7, 6, 2):
                continue
            print(f'{i+1}/{len_prisms}: dimensions = {prism.dimensions}')
            
            mapping = netFoldsToPrism(net, prism)
            
            if mapping:
                nums_on_sides = numbersOnSides(prism, mapping)
                print("\nNUMBERS ON SIDES") 
                print(nums_on_sides)
                print("\nANSWER")
                print(answer(nums_on_sides))
                solutions.append([prism, mapping])
                break
            
    print('\nlen(solutions):', len(solutions))
    logging.debug('assemble box end'.upper())
    return solutions

def solve(net):
    possible_nets = possibleNets(net)
    tot = len(possible_nets)
    for i, net in enumerate(possible_nets):
        print('{:2}/{:2}'.format(i+1, tot))
        assembleBox(net)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", help='diagnostic output')
    args = parser.parse_args()
    
    if args.debug:
        logging.basicConfig(format='%(message)s',level=logging.DEBUG)

    # solve(net.EXAMPLE_NET)
    
    DUMB = True
    solve(net.FULL_NET)
