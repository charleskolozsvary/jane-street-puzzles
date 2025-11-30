import re
import numpy as np
import utils.grids as grids
import utils.misc as misc
import itertools
from copy import deepcopy
from prism import Prism

# filled cells
class Cell:
    ''' Don't know how much I standardized this, but a square should be a collection of four 3d points which are the corners of a cell.'''
    def __init__(self, coordinate, attributes_string):
        x, y = coordinate
        self.corners = ((x, y, 0), (x+1, y, 0), (x+1, y+1, 0), (x, y+1, 0))
        self.bottom_left = self.corners[0]
        self.number = None
        self.circled = None
        self.squared = None
        self.canvas_spec = 'canvas is xy plane at z = 0, transform shape'

        '''Most of this alpha beta maybe shennanigans isn't used much'''

        # there can only be one alpha and one beta cell and either the alpha or the beta cell (but not both) is part of the net
        self.alpha = None
        self.beta = None

        # a maybe cell may or may not be filled
        self.maybe = None

        # symbol is the symbol used in the tikzpicture
        self.symbol = None
        if attributes_string == '':
            return
        for attr in attributes_string.split(','):
            if attr.isdigit():
                self.number = int(attr)
                self.symbol = attr
            elif attr == 'circled':
                self.circled = True
            elif attr == 'squared':
                self.squared = True
            elif attr == 'alpha':
                self.alpha = True
                self.symbol = '\\alpha'
            elif attr == 'beta':
                self.beta = True
                self.symbol = '\\beta'
            elif attr == 'm':
                self.maybe = True
                self.symbol = '?'
            else:
                assert False, "Cell attribute '{}' is unrecognized.".format(attr)
                
        if self.circled or self.squared:
            assert self.number, "If the cell is in a gray circle or square, it must have a digit, too."
            
    def __repr__(self):
        return str({'corners': self.corners,
                    'circled': self.circled,
                    'squared': self.squared,
                    'number': self.number})

def faceEdgeIdxs(face, edge):
    idxs = {}
    for idx in range(len(face)):
        if type(face[idx]) != tuple:
            idxs['face fixed'] = idx
        elif type(edge[idx]) != tuple:
            idxs['edge fixed'] = idx
        else:
            idxs['edge ranged'] = idx
    return idxs    
                        
class Net:
    def __init__(self, grid):
        list_of_cells = [Cell(pos, attrs) for pos, attrs in grid.items()]

        self.cells = {frozenset(cell.corners) : cell for cell in list_of_cells}
        self.cell_corners = [cell.corners for cell in self.cells.values()]

        self.grid_w = max([coor for coor in grid.keys()])[0]
        
        self.points_set = None
        self.points_np = None
        self.update_points()

    def fold(self, face_key, edge_key, destination_face, pool_cells):
        face, face_name = face_key
        edge, edge_idx = edge_key
        
        folding_cells = self.foldingCells(face, edge, pool_cells)

        if type(folding_cells) == str:
            return -1, folding_cells        

        elif len(folding_cells) == 0:
            return 0, 'No cells to fold along face {} and edge {}'.format(str(face), str(edge))

        # continue: there's at least one cell to fold
        
        cell_keys = [frozenset(cell.corners) for cell in folding_cells]

        face_edge_idxs = faceEdgeIdxs(face, edge)
        xyz = ['x', 'y', 'z']
        rotate_about_coor = xyz[face_edge_idxs['edge ranged']]

        plane = ''
        offset = ''
        for i, c in enumerate(destination_face):
            if type(c) == tuple:
                plane += xyz[i]
            else:
                assert offset == ''
                offset = '{} = 0'.format(xyz[i])
        spec = '{} plane at {}'.format(plane, offset)
        
        translation_point = np.array([0 if type(e) == tuple else e for e in edge])
        
        folding_corners = np.array([cell.corners for cell in folding_cells])
        
        folding_corners -= translation_point

        # select correct rotation
        rotation = misc.faceEdgeToRotation(face_name, edge_idx)

        np_rotated_corners = []
        for corners in folding_corners:
            np_rotated_corners.append(np.transpose(np.dot(rotation, np.transpose(corners))))

        folding_corners = np.array(np_rotated_corners)
        folding_corners += translation_point

        folded_corners = [misc.npCorners2Tuple(corners) for corners in folding_corners]

        # update
        new_cells = {}
        for i, c_key in enumerate(cell_keys):
            new_key = frozenset(folded_corners[i])
            new_cells[new_key] = deepcopy(self.cells[c_key])
            new_cells[new_key].corners = folded_corners[i]
            new_cells[new_key].canvas_spec = 'canvas is {}'.format(spec)
            del self.cells[c_key]
            self.cells[new_key] = deepcopy(new_cells[new_key])

        self.cell_corners = [cell.corners for cell in self.cells.values()]
        
        return new_cells

    def foldingCells(self, face, edge, pool_cells):
        '''
        return the cells which will be folded along a face and an edge

        A square is a tuple of four corner points of a cell
        '''
        
        face_edge_idxs = faceEdgeIdxs(face, edge)
        face_fixed_idx, edge_fixed_idx, edge_range_idx = face_edge_idxs['face fixed'], face_edge_idxs['edge fixed'], face_edge_idxs['edge ranged']

        def pointOnEdge(pos3d):
            nonlocal face_fixed_idx
            nonlocal edge_fixed_idx
            nonlocal edge_range_idx            

            idx1 = face_fixed_idx
            idx2 = edge_fixed_idx
            idx3 = edge_range_idx

            start = edge[idx3][0]
            end = edge[idx3][1]

            return pos3d[idx1] == edge[idx1] and pos3d[idx2] == edge[idx2] and pos3d[idx3] >= start and pos3d[idx3] <= end

        def cellOnEdge(corners):
            num_on = 0
            for corner in corners:
                if pointOnEdge(corner):
                    num_on += 1
            return num_on == 2

        def cellInsideEdge(corners):
            nonlocal edge_fixed_idx
            efi = edge_fixed_idx

            def pointInside(pt):
                if edge[efi] == face[efi][0]:
                    return pt[efi] > edge[efi]
                elif edge[efi] == face[efi][1]:
                    return pt[efi] < edge[efi]
                else:
                    assert False, "The fixed edge coordinate value should be the start or end of the corresponding face range"
            
            points_not_on_edge = list(filter(lambda p: not pointOnEdge(p), corners))
            
            if len(points_not_on_edge) != 2:
                return False
            
            for pne in points_not_on_edge:
                if not pointInside(pne):
                    return False
            return True

        squares = [cell.corners for cell in pool_cells.values()]

        cells_on_edge = list(filter(cellOnEdge, squares))

        cells_inside_edge = list(filter(cellInsideEdge, cells_on_edge))

        starting_cells = deepcopy(cells_on_edge)
        for cine in cells_inside_edge:
            starting_cells.remove(cine)

        squares_set = set(squares)

        def partOfNet(square):
            return square in squares_set

        def adjacentInPlane(corners: tuple[int]):
            nonlocal face_fixed_idx
            nonlocal edge_fixed_idx
            nonlocal edge_range_idx
            non_face_fixed = [edge_fixed_idx, edge_range_idx]
            shift_points = [tuple([pm if idx == nf else 0 for idx in [0, 1, 2]]) for nf in non_face_fixed for pm in [1, -1]]

            def shiftedCorners(shift_point):
                return tuple(map(lambda cs: misc.sumTuples(cs, shift_point), corners))

            return list(filter(partOfNet, [shiftedCorners(sp) for sp in shift_points]))
        
        adjacent_starting = []
        for sc in starting_cells:
            adjacent_starting += adjacentInPlane(sc)

        visited = set(starting_cells)
        frontier = set(filter(lambda cs: not cellInsideEdge(cs), adjacent_starting)) - visited

        def DFS(square):
            if square in visited:
                return
            visited.add(square)
            for adj_square in adjacentInPlane(square):
                DFS(adj_square)

        for f in frontier:
            DFS(f)

        if any(map(lambda square: square in cells_inside_edge, visited)):
            return -1, """
            The net cannot fold along this edge (or into this prism).
            The connected component of orthogonally adjacent squares which will fold along
            the edge includes a square which is inside the edge. See `pictures/test-fold-net.pdf`.
            """

        return [self.cells[frozenset(v)] for v in visited] # return the cells

    def update_points(self):
        self.points_set = set(p for cell in self.cells.values() for p in cell.corners)
        self.points_np = np.array([p for p in self.points_set])

    def tikzpicture(self, no_points = False, certain_cells = None, multiframe_arg_to_3dview = False):
        scale = .85

        orientation = 'canvas is xy plane at z = 0, transform shape, 3d view = {{{}}}{{30}}'.format('#1' if multiframe_arg_to_3dview else 0)
        picture = '\\newcommand{\\parampicture}[1]{{\\begin{tikzpicture}'
        picture += '[{ori}, scale = {sc}, every node/.style = {{scale = {sc}}}]\n'.format(ori=orientation, sc=scale)
        
        if not multiframe_arg_to_3dview:
            picture += '\\useasboundingbox (-{w},-{w},-{w}) -- ({w},{w},{w});'.format(w=(self.grid_w+5)//2)

        if not multiframe_arg_to_3dview:
            picture += '''\\rotateRPY{{0}}{{0}}{{{arg}}}
        \\begin{{scope}}[RPY, shift = {{(-{w2},-{w2},0)}}]'''.format(arg=0 if multiframe_arg_to_3dview else '#1',
                                                                     w2=(self.grid_w+1)/2)
        
        thickness = '.9pt'
        
        cells = certain_cells if certain_cells != None else self.cells.values()
        
        for cell in cells:
            x, y, z = cell.corners[0]
            a = np.array(cell.corners[0])
            b = np.array(cell.corners[1])
            c = np.array(cell.corners[2])
            d = np.array(cell.corners[3])
            
            center_p = misc.np2Tuple(a + (c-a)/2)
            
            inside_a = misc.np2Tuple(a + (c-a)/5)
            inside_c = misc.np2Tuple(a + 4*(c-a)/5)
            inside_b = misc.np2Tuple(b + (d-b)/5)
            inside_d = misc.np2Tuple(b + 4*(d-b)/5)
            inside_path = [inside_a, inside_b, inside_c, inside_d]

            opacity = 0.3

            text_color = '\\textcolor{black}'

            circled_color = 'RoyalPurple'
            squared_color = 'Goldenrod'
            squared_opacity = .4
            
            if cell.symbol:
                if cell.squared:
                    picture += '\\fill[color = {}, opacity = {}] {}--cycle;\n'.format(squared_color,
                                                                                      squared_opacity,
                                                                                      '--'.join([str(c) for c in inside_path]))
                if cell.circled:
                    picture += '\\node[circle, fill={}, opacity={}, {}] at {} {{{}}};\n'.format(circled_color,
                                                                                                opacity,
                                                                                               cell.canvas_spec,
                                                                                                center_p,
                                                                                                '\\LARGE $\\hphantom{\\mathsf{'+cell.symbol+'}}$')
                    
                picture += '\\node[{}] at {} {{{}}};\n'.format(cell.canvas_spec, center_p, '\\Large '+ text_color + '{{$\\mathsf{{{}}}$}}'.format(cell.symbol))
                picture += '\\draw[line width = {}] {}--cycle;\n'.format(thickness, '--'.join([str(c) for c in cell.corners]))
            else:
                picture += '\\fill[gray, opacity = {}] {}--cycle;\n'.format(opacity, '--'.join([str(c) for c in cell.corners]))
                picture += '\\draw[line width = {}] {}--cycle;\n'.format(thickness, '--'.join([str(c) for c in cell.corners]))    

        if not multiframe_arg_to_3dview:
            picture += '\\end{scope}\n'
        picture += '\\end{tikzpicture}}}\n'

        if no_points:
            return picture

        # likely no longer compatible
        
        picture += '\n\\vspace{5ex}\n\n\\[\\resizebox{20pc}{!}{\\begin{tikzpicture}'
        for p in self.points_set:
            picture += '\\filldraw {} circle ({});\n'.format(p, 0.05)
        picture += '\\end{tikzpicture}}\\]\n'
        return picture

    def __repr__(self):
        return str({'cells': self.cells,
                    'points_set': self.points_set,
                    'points_np': self.points_np})    

def isOneConnectedComponent(positions):
    visited = set()
    def DFS(pos):
        x, y = pos        
        if pos in visited or pos not in positions:
            return
        visited.add(pos)
        for next_pos in [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]:
            DFS(next_pos)
    start = positions[0]
    DFS(start)
        
    return len(visited) == len(positions)

# return all possible nets (if net contains maybe or alpha and beta cells)
def possibleNets(net):
    uncertain_cells = {}
    for face, cell in net.cells.items():
        if cell.symbol and not cell.symbol.isdigit():
            uncertain_cells[face] = cell
    unc_cells_indexed = {face:i for i,face in enumerate(uncertain_cells)}
    include_excludes = list(itertools.product((0,1), repeat=len(uncertain_cells)))
    possible_nets = []
    for inc_exc in include_excludes:
        remove_faces = list(filter(lambda f: inc_exc[unc_cells_indexed[f]], uncertain_cells))
        poss_net = deepcopy(net)
        for r_f in remove_faces:
            del poss_net.cells[r_f]
        poss_net.update_points()
        positions = [cell.bottom_left for cell in poss_net.cells.values()]
        if not isOneConnectedComponent(positions):
            continue
        has_alpha = any(map(lambda f: poss_net.cells[f].alpha, poss_net.cells))
        has_beta = any(map(lambda f: poss_net.cells[f].beta, poss_net.cells))
        if not (has_alpha and has_beta):
            for face, cell in poss_net.cells.items():
                if cell.alpha or cell.beta or cell.maybe:
                    cell.alpha = None
                    cell.beta = None
                    cell.maybe = None
                    cell.symbol = None
            possible_nets.append(poss_net)
        
    return possible_nets

def drawTikzs(nets, fname, no_points = True, certain_cells = None, animate = True, _3dview_shift = False):
    with open('pictures/preamble.tex', 'r') as f:
        preamble = f.readlines()
    
    tex_file = ''.join(preamble)
    for i, net in enumerate(nets):
        if certain_cells != None:
            tex_file += net.tikzpicture(no_points, certain_cells[i], _3dview_shift)
        else:
            tex_file += net.tikzpicture(no_points, certain_cells = None, multiframe_arg_to_3dview = _3dview_shift)
            
    if animate:
        tex_file += '''
        \\begin{document}
        \\begin{animateinline}{1}
        \\multiframe{360}{i=0+1}{\\parampicture{\\i}}
        \\end{animateinline}
        '''
    else:
        tex_file += '''
        \\begin{document}
        \\parampicture{60}
        '''
    tex_file += '\\end{document}\n'
    
    with open('{}.tex'.format(fname), 'w') as f:
        f.write(tex_file)


if __name__ == '__main__':
    full_net = Net(grids.FULL_GRID)
    test_net = Net(grids.TEST_FOLD)
    example_net = Net(grids.EXAMPLE_GRID)
    
            
            
