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
                assert False, "Cell attribute {} is unrecognized.".format(attr)
                
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
        self.points = set(p for cell in list_of_cells for p in cell.corners)

    def tikzpicture(self):
        picture = '''\\documentclass{article}\n\\usepackage{tikz}\n\\begin{document}\n\\[\\begin{tikzpicture}'''    
        for cell in self.cells.values():
            x, y = cell.position
            p = (x, y, 0)
            picture += '\\filldraw {}--cycle;\n'.format('--++'.join([str(p), '(1, 0, 0)', '(0, 1, 0)', '(-1, 0, 0)']))
        picture += '\\end{tikzpicture}\\]\n\n\\vspace{5ex}\n\n\\[\\begin{tikzpicture}'
        for p in self.points:
            picture += '\\draw {} circle (0.1);\n'.format(p)
        picture += '\\end{tikzpicture}\\]\n\\end{document}\n'
        return picture
        

    def __repr__(self):
        return str({'cells': self.cells,
                    'points': self.points,
                    'perimiter': self.perimiter})
        

if __name__ == '__main__':
    ex = Net(EXAMPLE_GRID)
    print(ex.points)
    # print(ex)
    # print(ex.tikzpicture())
            
