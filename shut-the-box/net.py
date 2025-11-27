import re
import numpy as np
import utils.grids as grids
import utils.misc as misc
import itertools
from copy import deepcopy

# filled cells
class Cell:
    def __init__(self, coordinate, attributes_string):
        x, y = coordinate
        self.bottom_left = (x, y, 0)
        self.corners = ((x, y, 0), (x+1, y, 0), (x+1, y+1, 0), (x, y+1, 0))
        self.number = None
        self.circled = None
        self.squared = None

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
        return str({'bottom_left': self.bottom_left,
                    'circled': self.circled,
                    'squared': self.squared,
                    'number': self.number})
            
class Net:
    def __init__(self, grid):
        list_of_cells = [Cell(pos, attrs) for pos, attrs in grid.items()]

        # self.corners = {cell.corners : cell for cell in list_of_cells}

        self.cell_corners = [cell.corners for cell in list_of_cells]
        self.cells = {frozenset(cell.corners) : cell for cell in list_of_cells}
        
        self.points_set = None
        self.points_np = None
        self.update_points()

    def update_points(self):
        self.points_set = set(p for cell in self.cells.values() for p in cell.corners)
        self.points_np = np.array([p for p in self.points_set])

    def tikzpicture(self, no_points = False, certain_cells = None):
        picture = '\\pagenumbering{gobble}\\['
        picture += '''\\resizebox{!}{30pc}\n{\\begin{tikzpicture}'''
        thickness = '1pt'
        
        cells = certain_cells if certain_cells != None else self.cells.values()
        
        for cell in cells:
            x, y, z = cell.bottom_left
            p = (x, y, z)
            center_p = (x+.5, y+.5, z)
            square_p = (x+.2, y+.2, z)
            if cell.symbol:
                picture += '\\draw node at {} {{{}}};\n'.format(center_p, '\\Large $\\mathsf{{{}}}$'.format(cell.symbol))
                picture += '\\draw[line width = {}] {}--cycle;\n'.format(thickness, '--++'.join([str(p), '(1, 0, 0)', '(0, 1, 0)', '(-1, 0, 0)']))
            else:
                picture += '\\fill[gray, opacity = 0.5] {}--cycle;\n'.format('--++'.join([str(p), '(1, 0, 0)', '(0, 1, 0)', '(-1, 0, 0)']))
                picture += '\\draw[line width = {}] {}--cycle;\n'.format(thickness, '--++'.join([str(p), '(1, 0, 0)', '(0, 1, 0)', '(-1, 0, 0)']))
                
            if cell.circled:
                picture += '\\fill[color = gray, opacity = 0.5] {} circle ({});\n'.format(center_p, 0.28)
            elif cell.squared:
                picture += '\\fill[color = gray, opacity = 0.5] {} rectangle ++({w}, {w});\n'.format(square_p, w = 0.6)
            
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


    def foldingCells(self, face, edge):
        '''
        return the cells which will be folded along a face and an edge

        A square is a tuple of four corner points of a cell
        '''

        def getFaceFixedIdx():
            for i, value in enumerate(face):
                if type(value) != tuple:
                    return i

        def edgeFixedAndRangeIdx(pln_f_idx):
            fix = None
            ran = None
            for i, value in enumerate(edge):
                if type(value) != tuple and i != pln_f_idx:
                    fix = i
                elif type(value) == tuple:
                    ran = i
            return fix, ran
                
        face_fixed_idx = getFaceFixedIdx()

        edge_fixed_idx, edge_range_idx = edgeFixedAndRangeIdx(face_fixed_idx)

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
    tex_file = '\\documentclass{article}\n\\usepackage{tikz}\n\\usepackage{graphicx}\\usepackage{stix2}\n\\begin{document}\n'
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

    # drawTikzs([TEST_NET], 'pictures/test-fold-net')

    dimensions = (7, 6, 2)

    face = ((6, 13), (13, 19), 0)

    edges = [(6, (13, 19), 0), (13, (13, 19), 0), ((6, 13), 13, 0), ((6, 13), 19, 0)]

    edge_left = edges[0]

    edge_right = edges[1]

    edge_bottom = edges[2]

    edge_top = edges[3]

    a = net.foldingCells(face, edge_right)

    drawTikzs([FULL_NET], 'pictures/right-fold', no_points = True, certain_cells = [a])

    b = net.foldingCells(face, edge_bottom)

    c = net.foldingCells(face, edge_left)

    d = net.foldingCells(face, edge_top)

    drawTikzs([FULL_NET], 'pictures/bottom-fold', no_points = True, certain_cells = [b])

    drawTikzs([FULL_NET], 'pictures/left-fold', no_points = True, certain_cells = [c])

    drawTikzs([FULL_NET], 'pictures/top-fold', no_points = True, certain_cells = [d])        

    if type(a) != str:
        for c in a:
            print(c)
    else:
        print(a)
            

    print()

    if type(b) != str:
        for c in b:
            print(c)
    else:
        print(b)
            
            
