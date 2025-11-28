import re
import numpy as np
import utils.grids as grids
import utils.misc as misc
import itertools
from copy import deepcopy
from prism import Prism

# filled cells
class Cell:
    def __init__(self, coordinate, attributes_string):
        x, y = coordinate
        self.corners = ((x, y, 0), (x+1, y, 0), (x+1, y+1, 0), (x, y+1, 0))
        self.bottom_left = self.corners[0]
        self.number = None
        self.circled = None
        self.squared = None
        self.canvas_spec = 'canvas is xy plane at z = 0, transform shape'

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
        
        self.points_set = None
        self.points_np = None
        self.update_points()        

    def fold(self, face_key, edge_key, destination_face):
        face, face_name = face_key
        edge, edge_idx = edge_key
        folding_cells = self.foldingCells(face, edge)
        
        cell_keys = [frozenset(cell.corners) for cell in folding_cells]
        if type(folding_cells) == str:
            return None

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
            
            
            # self.cells[c_key].corners = folded_corners[i]
            # self.cells[c_key].canvas_spec = 'canvas is {}'.format(spec)
            # self.cell_corners = [cell.corners for cell in self.cells.values()]            
        

    def foldingCells(self, face, edge):
        '''
        return the cells which will be folded along a face and an edge

        A square is a tuple of four corner points of a cell
        '''
        
        face_edge_idxs = faceEdgeIdxs(face, edge)
        face_fixed_idx, edge_fixed_idx, edge_range_idx = face_edge_idxs['face fixed'], face_edge_idxs['edge fixed'], face_edge_idxs['edge ranged']

        # print(face_fixed_idx, edge_fixed_idx, edge_range_idx)

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

        cells_on_edge = list(filter(cellOnEdge, self.cell_corners))

        cells_inside_edge = list(filter(cellInsideEdge, cells_on_edge))

        starting_cells = deepcopy(cells_on_edge)
        for cine in cells_inside_edge:
            starting_cells.remove(cine)

        cell_corners_set = set(self.cell_corners)

        def partOfNet(corners):
            return corners in cell_corners_set

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
            return """
            The net cannot fold along this edge (or into a prism).
            At least one of the squares which will fold along the edge is adjacent to
            a square which rests inside the edge.
            """

        return [self.cells[frozenset(v)] for v in visited] # return the cells

    def update_points(self):
        self.points_set = set(p for cell in self.cells.values() for p in cell.corners)
        self.points_np = np.array([p for p in self.points_set])

    def tikzpicture(self, no_points = False, certain_cells = None):
        picture = '\\pagenumbering{gobble}\\['
        orientation = 'canvas is xy plane at z = 0, transform shape, 3d view = {60}{20}'
        picture += '\\resizebox{30pc}{!}\n{\\begin{tikzpicture}'
        picture += '[' + orientation + ']'
        # picture += ', every node/.style = {' + orientation + '}]'
        thickness = '1pt'
        
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
            
            if cell.symbol:
                if cell.circled:
                    picture += '\\node[circle,fill=gray,opacity=0.5,{}] at {} {{{}}};\n'.format(cell.canvas_spec, center_p, '\\LARGE $\\hphantom{{\\mathsf{{{}}}}}$'.format(cell.symbol))
                picture += '\\node[{}] at {} {{{}}};\n'.format(cell.canvas_spec, center_p, '\\Large $\\mathsf{{{}}}$'.format(cell.symbol))
                picture += '\\draw[line width = {}] {}--cycle;\n'.format(thickness, '--'.join([str(c) for c in cell.corners]))
            else:
                picture += '\\fill[gray, opacity = 0.5] {}--cycle;\n'.format('--'.join([str(c) for c in cell.corners]))
                picture += '\\draw[line width = {}] {}--cycle;\n'.format(thickness, '--'.join([str(c) for c in cell.corners]))
                
            if cell.circled:
                picture += ''
                # picture += '\\begin{{scope}}[{}]\n'.format(cell.canvas_spec)
                # picture += '\\fill[color = gray, opacity = 0.5] {} circle ({});\n'.format(center_p, 0.28)
                # picture += '\\end{scope}\n'
            elif cell.squared:
                picture += '\\fill[color = gray, opacity = 0.5] {}--cycle;\n'.format('--'.join([str(c) for c in inside_path]))
            
        picture += '\\end{tikzpicture}}\\]\n'

        if no_points:
            return picture
        
        picture += '\n\\vspace{5ex}\n\n\\[\\resizebox{!}{30pc}{\\begin{tikzpicture}'
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

def drawTikzs(nets, fname, no_points = False, certain_cells = None):
    tex_file = '\\documentclass{article}\n\\usepackage{tikz}\\usepackage{tikz-3dplot}\n'
    tex_file += '\\usetikzlibrary{perspective}\n\\usepackage{graphicx}\\usepackage{stix2}\n\\begin{document}\n'
    for i, net in enumerate(nets):
        if certain_cells != None:
            tex_file += net.tikzpicture(no_points, certain_cells[i])
        else:
            tex_file += net.tikzpicture(no_points)
    tex_file += '\\end{document}\n'
    with open('{}.tex'.format(fname), 'w') as f:
        f.write(tex_file)
        
# EXAMPLE_NET = Net(grids.EXAMPLE_GRID)

FULL_NET = Net(grids.FULL_GRID)

TEST_NET = Net(grids.TEST_FOLD)


if __name__ == '__main__':
    drawTikzs([FULL_NET], 'pictures/full-net')
    # drawTikzs([EXAMPLE_NET], 'pictures/example-net')

    net = FULL_NET

    drawTikzs([TEST_NET], 'pictures/test-fold-net')

    dimensions = (7, 6, 2)    

    prism = Prism(dimensions)
    prism.translate((6,13,0))

    face_key = (((6, 13), (13, 19), 0), 'bottom')    
    
    edges = prism.face_to_edges[face_key]

    face, face_name = face_key

    # print(edges)
    
    # edges = [(6, (13, 19), 0), (13, (13, 19), 0), ((6, 13), 13, 0), ((6, 13), 19, 0)]

    edge_left = edges[0]

    edge_right = edges[1]

    edge_bottom = edges[2]

    edge_top = edges[3]

    # a = net.foldingCells(face, edge_right)

    # b = net.foldingCells(face, edge_bottom)

    c = net.foldingCells(face, edge_left)

    assert c == [], "c not empty?"

    # d = net.foldingCells(face, edge_top)

    # net.fold(face_key, edge_right, prism.destinationFace(face_key, edge_right))

    nfk = ((13, (13, 19), (0, 2)), 'right')
    ne = [(13, 13, (0, 2)), (13, 19, (0, 2)), (13, (13, 19), 0), (13, (13, 19), 2)]    

    # net.fold(nfk, ne[3], prism.destinationFace(nfk, ne[3]))

    net.fold(face_key, (edge_bottom, 2), prism.destinationFace(face_key, edge_bottom))

    # print(net.cells)

    # (((6, 13), 13, (0, 2)), 'front') [(6, 13, (0, 2)), (13, 13, (0, 2)), ((6, 13), 13, 0), ((6, 13), 13, 2)]
    nfk2 = (((6, 13), 13, (0, 2)), 'front')
    nne = [(6, 13, (0, 2)), (13, 13, (0, 2)), ((6, 13), 13, 0), ((6, 13), 13, 2)]
    
    net.fold(nfk2, (nne[3], 3), prism.destinationFace(nfk2, nne[3]))

    drawTikzs([FULL_NET], 'pictures/folded-full-net')    

    # drawTikzs([FULL_NET], 'pictures/right-fold', no_points = True, certain_cells = [a])    

    # drawTikzs([FULL_NET], 'pictures/bottom-fold', no_points = True, certain_cells = [b])

    # drawTikzs([FULL_NET], 'pictures/left-fold', no_points = True, certain_cells = [c])

    # drawTikzs([FULL_NET], 'pictures/top-fold', no_points = True, certain_cells = [d])        

    # if type(a) != str:
    #     for c in a:
    #         print(c)
    # else:
    #     print(a)
            

    # print()

    # if type(b) != str:
    #     for c in b:
    #         print(c)
    # else:
    #     print(b)
            
            
