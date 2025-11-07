import re
import numpy as np
from grids import *

# filled cells
class Cell:
    def __init__(self, coordinate, attributes_string):
        x, y = coordinate
        self.position = (x, y)
        self.corners = set([(x, y, 0), (x+1, y, 0), (x, y+1, 0), (x+1, y+1, 0)])
        self.number = None
        self.circled = None
        self.squared = None
        if attributes_string == '':
            return
        for attr in attributes_string.split(','):
            if attr.isdigit():
                self.number = int(attr)            
            elif attr == 'circled':
                self.circled = True
            elif attr == 'squared':
                self.squared = True
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
        self.points_set = set(p for cell in list_of_cells for p in cell.corners)
        self.points_np = np.array([p for p in self.points_set])

    def tikzpicture(self):
        picture = '''\\documentclass{article}\n\\usepackage{tikz}\n\\begin{document}\n\\[\\begin{tikzpicture}'''    
        for cell in self.cells.values():
            x, y = cell.position
            p = (x, y, 0)
            center_p = (x+.5, y+.5, 0)
            square_p = (x+.15, y+.15)
            picture += '\\draw[thick] {}--cycle;\n'.format('--++'.join([str(p), '(1, 0, 0)', '(0, 1, 0)', '(-1, 0, 0)']))
            if cell.number:
                picture += '\\draw node at {} {{{}}};\n'.format(center_p, '\\Large $\\mathsf{{{}}}$'.format(cell.number))
            if cell.circled:
                picture += '\\fill[color = gray, opacity = 0.5] {} circle ({});\n'.format(center_p, 0.35)
            if cell.squared:
                picture += '\\fill[color = gray, opacity = 0.5] {} rectangle ++({w}, {w});\n'.format(square_p, w = 0.7)
        picture += '\\end{tikzpicture}\\]\n\n\\vspace{5ex}\n\n\\[\\begin{tikzpicture}'
        for p in self.points_set:
            picture += '\\filldraw {} circle ({});\n'.format(p, 0.05)
        picture += '\\end{tikzpicture}\\]\n\\end{document}\n'
        return picture

    def __repr__(self):
        return str({'cells': self.cells,
                    'points_set': self.points_set,
                    'points_np': self.points_np})
    
EXAMPLE_NET = Net(EXAMPLE_GRID)

def drawTikz():
    with open('picture-net.tex', 'w') as f:
        f.write(EXAMPLE_NET.tikzpicture())

if __name__ == '__main__':
    drawTikz()
            
