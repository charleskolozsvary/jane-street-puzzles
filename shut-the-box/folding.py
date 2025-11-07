import numpy as np
import net
from prism import startingPrisms
from copy import deepcopy
# net is a Net from net.py
# prism is a Prism from prism.py
# assumes prism is just one of many orientations
# with respect to the polygon (net) P.
def netFoldsToPrism(net, prism):
    Q = prism.perimiter
    P = net.points_np
    for p in P:
        for q in Q:
            start_prism = deepcopy(prism)
            starting_point = p - q
            start_prism.translate(starting_point)

            face_mapping = {frozenset(f): None for f in start_prism.orig_face_tuples}

            # print('len(face_mapping):', len(face_mapping))
            print('trying straing point = {}'.format(starting_point))
            # print()
            stampDFS(start_prism, face_mapping, net)
            if None not in face_mapping.values():
                print('SOLUTION FOUND')
                print('starting_point = {}'.format(starting_point))
                # print()
                # print(face_mapping)
                return face_mapping
    return None

DIRECTIONS = ['north', 'east', 'west', 'south']

# the hope is that different stamping paths don't conflict
# we just need to do a complete DFS traversal of the net
# by stamping or tipping into different directions and the end
# state of mapping will tell us if the net actually folds into
# the prism.
def stampDFS(prism, mapping, net):
    # stamp
    downFaces = prism.heightZeroToOrigFaces()
    if not any(map(lambda dface: dface in net.cells, downFaces)):
        return # none of the faces down are part of the net; return unsuccessfully

    for down_face, key_face in downFaces.items():
        if down_face not in net.cells:
            continue
        elif mapping[key_face] is None:
            print('added:', net.cells[down_face].position, net.cells[down_face].number)
            print('orig_face:', key_face)
            print()
            mapping[key_face] = net.cells[down_face]
        else:
            return # net square already part of mapping, return unsuccessfully
        
    if None not in mapping.values():
        print('Solution already found')
        return # return successfully

    for direction in DIRECTIONS:
        next_prism = deepcopy(prism)
        print('tipping {}...'.format(direction.upper()))
        next_prism.tip(direction)
        stampDFS(next_prism, mapping, net)

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

# messy, but this works...
def assembleBox(net):
    solutions = []
    surface_area = len(net.cells)
    starting_prisms = startingPrisms(surface_area)
    print('START')
    for dimensions, prisms in starting_prisms.items():
        print('dimensions:', dimensions)
        print('len(prisms):', len(prisms))
        print()
        for prism in prisms:
            print('prism dimensions:', prism.dimensions)
            mapping = netFoldsToPrism(net, prism)
            if mapping:
                print("NUMBERS ON SIDES")
                print()
                nums_on_sides = numbersOnSides(prism, mapping)
                print(nums_on_sides)
                print()
                print("ANSWER")
                print(answer(nums_on_sides))
                solutions.append([prism, mapping])
                break
    print('END')
    return solutions
            

if __name__ == '__main__':
    sols = assembleBox(net.EXAMPLE_NET)
    print(len(sols))
