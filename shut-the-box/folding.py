import numpy as np

from prism import startingPrisms

import net as prism_net
import prism as rect_prism
import utils.grids as grids
import utils.misc as misc
from utils.drawing import cellsPictureTeX

from copy import deepcopy

import argparse
import logging

def squareOnFace(face, corners):
    '''
    face: (a, b, c) where two of the three are 2d tuples specifying a range
    corners: (c1, c2, c3, c4) where ci is 3d point
    '''
    def pointOnFace(point):
        nonlocal face
        for idx,f in enumerate(face):
            if type(f) == tuple:
                if not (f[0] <= point[idx] and point[idx] <= f[1]):
                    return False
            elif f != point[idx]:
                return False
        return True
    return all(map(pointOnFace, corners))
                    
def faceIdxs(face):
    ranged = []
    fixed = None
    for idx, f in enumerate(face):
        if type(f) == tuple:
            ranged.append(idx)
        else:
            fixed = idx
    return fixed, ranged

def faceSquares(face):
    fixed_idx, ranged_idxs = faceIdxs(face)
    ranged_idx1 = ranged_idxs[0]
    ranged_idx2 = ranged_idxs[1]
    fixed_val = face[fixed_idx]
        
    squares = []
    def makeCorner(range1, range2):
        nonlocal fixed_idx, fixed_val
        nonlocal ranged_idx1
        nonlocal ranged_idx2
                    
        corner = [None, None, None]
        corner[fixed_idx] = fixed_val
        corner[ranged_idx1] = range1
        corner[ranged_idx2] = range2
        return tuple(corner)
        
    for i in range(face[ranged_idx1][0], face[ranged_idx1][1]+1):
        for j in range(face[ranged_idx2][0], face[ranged_idx2][1]+1):
            bottom_left = makeCorner(i, j)
            bottom_right = makeCorner(i+1, j)
            top_right = makeCorner(i+1, j+1)
            top_left = makeCorner(i, j+1)
            square = tuple([bottom_left, bottom_right, top_right, top_left])
            if squareOnFace(face, square):
                squares.append(square)
    return squares

def shutTheBox(net, prism):
    '''
    Given a net of a rectangular prism and a rectangular prism statically positioned somewhere on the net,
    try to fold up the net into the prism.
    '''
    def inContactWithNet(face):
        cells_on_face = list(filter(lambda square: squareOnFace(face, square), [cell.corners for cell in net.cells.values()]))
        if len(cells_on_face) > 0:
            return cells_on_face
        else:
            return False

    prism_squares = set()
    starting_face = None
    starting_squares_on_prism = []
    for face_key, edges in prism.face_to_edges.items():
        for square in faceSquares(face_key[0]):
            prism_squares.add(square)
        net_contact = inContactWithNet(face_key[0])
        if net_contact:
            assert starting_face == None, "Multiple faces of the prism are in contact with the net at the beginning."
            starting_face = face_key
            starting_squares_on_prism = net_contact

    logging.debug('starting face: {}'.format(str(starting_face)))
    logging.debug('len(prism_squares): {}'.format(str(len(prism_squares))))
    assert len(prism_squares) == prism.surfaceArea()

    prism_squares_to_net_cells = {frozenset(square): None for square in prism_squares}
    for square in starting_squares_on_prism:
        key = frozenset(square)
        prism_squares_to_net_cells[key] = net.cells[key]

    logging.debug('len(starting_squares_on_prism): {}'.format(str(len(starting_squares_on_prism))))

    net = deepcopy(net)    

    shutRec(prism_squares_to_net_cells, starting_face, prism, net, None, deepcopy(net.cells), 0)

    empty_count = 0
    for v in prism_squares_to_net_cells.values():
        if v == None:
            empty_count += 1
            
    logging.debug('num empty squares: {}'.format(empty_count))

    if None not in prism_squares_to_net_cells.values():
        return net, True
    else:
        return net, False

COUNT = 1

def shutRec(mapping, face_key, prism, net, no_fold_edge, pool_cells, depth):
    global COUNT
    if None not in mapping.values():
        print("this didn't happen")
        return
    
    for idx, edge in enumerate(prism.face_to_edges[face_key]):
        print("                    idx: {} at face '{}' and depth '{}'".format(idx, face_key[1], depth))
        if edge == no_fold_edge:
            print("                    skipping no fold edge '{}' at face '{}' and depth '{}'".format(edge, face_key[1], depth))
            continue
        destination_face_key = prism.destinationFaceKey(face_key, edge)

        print("               attempting to fold edge             '{}' at face '{}' and depth '{}'".format(edge, face_key[1], depth))
        return_val = net.fold(face_key, (edge, idx), destination_face_key[0], deepcopy(pool_cells))
        if type(return_val) == tuple:
            if return_val[0] == -1:
                # return unsuccessfully---net can't fold into prism
                print("this didn't happen either")
                return
            elif return_val[0] == 0:
                # no cells to fold along edge for this face
                print("                    no cells to fold along on edge '{}' at face '{}' and depth '{}'".format(edge, face_key[1], depth))
                continue
            else:
                assert False, "Return code {} unrecognized".format(str(return_val[0]))
        # logging.debug(return_val)
        assert type(return_val) == dict, "If net.fold is successful, it should return a dictionary of the new cells"
        new_cells = deepcopy(return_val)

        # for c in new_cells:
        #     print(c)
        #     print()
        
        for cell_key, cell in new_cells.items():
            if cell_key in mapping:
                if mapping[cell_key] == None:
                    mapping[cell_key] = cell
                else:
                    print(cell_key, mapping[cell_key])
                    print("so this must have happened? this is bad...")
                    cellsPictureTeX(new_cells.values(), 'latest-bug')
                    # return unsuccesffully, square on prism already covered
                    return
                    #return
        print("                    folded on edge '{}' on '{}' at depth '{}'".format(edge, face_key[1], depth))

        print()
        print(COUNT, face_key)
        prism_net.drawTikzs([net], 'pictures/{}debug'.format(COUNT), True, None, True)
        COUNT += 1        
        
        shutRec(mapping, destination_face_key, prism, net, edge, deepcopy(new_cells), depth+1)
        # need to remove new_cells from pool_cells
        # print(pool_cells)
        # print()
        # print('do we get here?')
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", help='debugging output')
    args = parser.parse_args()
    
    if args.debug:
        logging.basicConfig(format='%(message)s',level=logging.DEBUG)
    complete_net = prism_net.Net(grids.FULL_GRID)

    prism = rect_prism.Prism((7,6,2))
    prism.translate((6,13,-2))

    prism_net.drawTikzs([complete_net], 'pictures/0debug')    
    
    res = shutTheBox(complete_net, prism)
    prism_net.drawTikzs([res[0]], 'pictures/ohwell')
    print(res[1])
    
