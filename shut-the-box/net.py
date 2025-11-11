import re
import numpy as np
import utils.grids as grids
import itertools
from copy import deepcopy

# filled cells
class Cell:
    def __init__(self, coordinate, attributes_string):
        x, y = coordinate
        self.position = (x, y)
        self.corners = set([(x, y, 0), (x+1, y, 0), (x, y+1, 0), (x+1, y+1, 0)])
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
        return str({'position': self.position,
                    'corners': self.corners,
                    'circled': self.circled,
                    'squared': self.squared,
                    'number': self.number})
            
class Net:
    def __init__(self, grid):
        list_of_cells = [Cell(pos, attrs) for pos, attrs in grid.items()]
        self.cells = {frozenset(cell.corners) : cell for cell in list_of_cells}
        # key is the original set of cell corners value is the current orientation of the cell corners/face
        self.cell_orientations = {face: deepcopy(face) for face in self.cells}
        
        self.points_set = None
        self.points_np = None
        self.update_points()

    def update_points(self):
        self.points_set = set(p for cell in self.cells.values() for p in cell.corners)
        self.points_np = np.array([p for p in self.points_set])

    def tikzpicture(self, no_points = False):
        picture = '\\pagenumbering{gobble}\\['
        picture += '''%\\resizebox{30pc}{!}\n\\hspace{-10em}{\\begin{tikzpicture}'''
        thickness = '1pt'
        for cell in self.cells.values():
            x, y = cell.position
            p = (x, y, 0)
            center_p = (x+.5, y+.5, 0)
            square_p = (x+.2, y+.2)
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
        
        picture += '\n\\vspace{5ex}\n\n\\[\\resizebox{30pc}{!}{\\begin{tikzpicture}'
        for p in self.points_set:
            picture += '\\filldraw {} circle ({});\n'.format(p, 0.05)
        picture += '\\end{tikzpicture}}\\]\n'
        return picture

    def __repr__(self):
        return str({'cells': self.cells,
                    'points_set': self.points_set,
                    'points_np': self.points_np})

    def isOneConnectedComponent(self):
        visited = set()
        positions = [cell.position for cell in self.cells.values()]

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
        if not poss_net.isOneConnectedComponent():
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
        
EXAMPLE_NET = Net(grids.EXAMPLE_GRID)

FULL_NET = Net(grids.FULL_GRID)

def drawTikzs(nets, fname, no_points = False):
    tex_file = '\\documentclass{article}\n\\usepackage{tikz}\n\\usepackage{graphicx}\\usepackage{stix2}\n\\begin{document}\n'
    for net in nets:
        tex_file += net.tikzpicture(no_points)
    tex_file += '\\end{document}\n'
    with open('{}.tex'.format(fname), 'w') as f:
        f.write(tex_file)

if __name__ == '__main__':
    drawTikzs([FULL_NET], 'pictures/full-net')
    drawTikzs([EXAMPLE_NET], 'pictures/example-net')
    
    # possible_nets = possibleNets(FULL_NET)

    # print(len(possible_nets))

    # possible_ex_nets = possibleNets(EXAMPLE_NET)

    # print(len(possible_ex_nets))

    # drawTikzs(possible_nets, 'net-pictures/possible-nets', no_points = True)

    # drawTikzs(possible_ex_nets, 'net-pictures/example-poss-nets', no_points = True)    
            
