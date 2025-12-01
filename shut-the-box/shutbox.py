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

def shutTheBox(net, prism, _animate, fold_file_prefix):
    '''
    Given a net of a rectangular prism and a rectangular prism statically positioned somewhere on the net,
    try to fold the net into the prism.
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

    # deepcopy use might be a little profligate, though deepcopy(net.cells) prevents 'latest-bug'
    
    net = deepcopy(net)

    logging.debug(f'len(prism_squares_to_net_cells): {len(prism_squares_to_net_cells)}')

    shutRec(prism_squares_to_net_cells, starting_face, prism, net, None, deepcopy(net.cells), 0, _animate, fold_file_prefix)

    empty_count = 0
    for v in prism_squares_to_net_cells.values():
        if v == None:
            empty_count += 1
            
    logging.debug('num empty squares: {}'.format(empty_count))

    if None not in prism_squares_to_net_cells.values():
        return net, True
    else:
        return net, False

FOLD_COUNT = 1

def shutRec(mapping, face_key, prism, net, no_fold_edge, pool_cells, depth, _animate, fold_file_prefix):
    global FOLD_COUNT
    if None not in mapping.values():
        logging.debug("Net successfully folded into prism.")
        return
    
    for idx, edge in enumerate(prism.face_to_edges[face_key]):
        logging.debug("                    idx: {} at face '{}' depth '{}'".format(idx, face_key[1], depth))
        destination_face_key = prism.destinationFaceKey(face_key, edge)        
        if edge == no_fold_edge:
            logging.debug("                    skipping no fold edge '{}' at face '{}' depth '{}' dest face '{}'".format(edge, face_key[1],
                                                                                                                         depth,
                                                                                                                         destination_face_key[1]))
            continue
        # destination_face_key = prism.destinationFaceKey(face_key, edge)

        logging.debug("               attempting to fold edge             '{}' at face '{}' depth '{}' to dest face '{}'".format(edge, face_key[1],
                                                                                                                                     depth,
                                                                                                                                     destination_face_key[1]))
        return_val = net.fold(face_key, (edge, idx), destination_face_key[0], deepcopy(pool_cells))
        if type(return_val) == tuple:
            if return_val[0] == -1:
                # return unsuccessfully---net can't fold into prism
                logging.debug("Net cannot fold into prism.")
                return
            elif return_val[0] == 0:
                # no cells to fold along edge for this face
                logging.debug("                    no cells to fold along on edge '{}' at face '{}' depth '{}'".format(edge, face_key[1], depth))
                continue
            else:
                assert False, "Return code {} unrecognized".format(str(return_val[0]))
                
        assert type(return_val) == dict, "If net.fold is successful, it should return a dictionary of the new cells"
        new_cells = deepcopy(return_val)

        added_this_fold = 0
        for cell_key, cell in new_cells.items():
            if cell_key in mapping:
                if mapping[cell_key] == None:
                    mapping[cell_key] = cell
                    added_this_fold += 1
                else:
                    # return unsuccesffully, square on prism already covered
                    logging.debug('Returning  unsuccessfully...')
                    logging.debug(f'cell_key {cell_key} already defined in mapping as {mapping[cell_key]}.')
                    logging.debug('See pictures/latest-bug.tex')
                    cellsPictureTeX(new_cells.values(), 'latest-bug')
                    return
                
        logging.debug("                    folded on edge '{}' on '{}' depth '{}' to destination face '{}'".format(edge, face_key[1], depth,
                                                                                                                    destination_face_key[1]))

        logging.debug(f'faces added to mapping this fold: {added_this_fold}')
        empty_count = 0
        for v in mapping.values():
            if v == None:
                empty_count += 1
        logging.debug(f'Faces still without mapping: {empty_count}')

        logging.debug('\n')
        logging.debug(f'{FOLD_COUNT}: {face_key}')

        prism_net.makeTeX(net, 'folds/TeX/{}{}fold{}'.format('static-' if not _animate else '',
                                                             fold_file_prefix,
                                                             FOLD_COUNT), animate = _animate) 
        FOLD_COUNT += 1
        
        shutRec(mapping, destination_face_key, prism, net, edge, deepcopy(new_cells), depth+1, _animate, fold_file_prefix)

def foldNetAroundPrism(net, prism_dimensions, prism_translate, fold_file_prefix, args):
    prism = rect_prism.Prism(prism_dimensions)
    prism.translate(prism_translate)
    prism_net.makeTeX(net,
                      'folds/TeX/{}{}fold0'.format('static-' if not args.animate else '', fold_file_prefix),
                      animate = args.animate)
    global FOLD_COUNT
    FOLD_COUNT = 1
    net_out, folded_succ = shutTheBox(net, prism, args.animate, fold_file_prefix)
    if folded_succ:
        prism_net.makeTeX(net_out, f'{fold_file_prefix}shut-box', animate = args.animate, _3dview_shift = True)
        print(f'The net successfully folded into the prism with dimensions {prism_dimensions}. See pictures/{fold_file_prefix}shut-box.tex')
    else:
        print(f'The net did NOT fold into the prism with dimensions {prism_dimensions}.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true", help='debugging output')
    parser.add_argument("-a", "--animate", action="store_true", help='draw 360 frames of each picture of the net, folded or otherwise')
    parser.add_argument("-t", "--topdown", action="store_true", help='draw the nets from a top-down perspective')    
    args = parser.parse_args()
    
    if args.debug:
        logging.basicConfig(format='%(message)s',level=logging.DEBUG)

    full_net = prism_net.Net(grids.FULL_GRID)
    example_net = prism_net.Net(grids.EXAMPLE_GRID)
    
    foldNetAroundPrism(example_net, (2, 1, 4), (2, 1, -4), 'example-net-', args)
    foldNetAroundPrism(full_net, (7, 2, 6), (6, 11, -6), 'full-net-', args)    
    
    
