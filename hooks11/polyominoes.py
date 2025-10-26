from typing import Callable, Any, Union
from clues import CLUES
import utils

PENTOMINOES = {
    'F': [(0, 0), (-1, 0), (0, -1), (0, 1), (1, 1)],
    'I': [(0, 0), (0, 1), (0, 2), (0, 3), (0,4)],
    'L': [(0, 0), (0, 1), (0, 2), (0, 3), (1,0)],
    'N': [(0, 0), (0, 1), (0, 2), (1, 2), (1, 3)],
    'P': [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)],
    'T': [(0, 0), (0, 1), (0, 2), (-1, 2), (1, 2)],
    'U': [(0, 0), (0, 1), (1, 0), (2, 0), (2, 1)],
    'V': [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)],
    'W': [(0, 0), (1, 0), (1, 1), (2, 1), (2, 2)],
    'X': [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)],
    'Y': [(0, 0), (1, 0), (1, 1), (2, 0), (3, 0)],
    'Z': [(0, 0), (-1, 0), (-1, 1), (-1, 2), (-2, 2)]
}
    
def makeGrid(n: int, m: int, fill: Any):
    grid = []
    for _ in range(n):
        grid.append([])
        for _ in range(m):
            grid[-1].append(fill)
    return grid

#--------------------------------------------------------------
# Given an nxm grid, produce a list of cartesian grid indices (x, y) which each correspond to grid[y][x]
#--------------------------------------------------------------
def gridCoordinates(grid: list[list[Any]]) -> list[tuple[int]]:
    coordinates = []
    colWidth = len(grid[0])
    for i in range(len(grid)):
        assert len(grid[i]) == colWidth, 'inputted grid is not nxm---there are varying column sizes'
        for j in range(len(grid[i])):
            coordinates.append(tuple([j, i]))
    return coordinates

def orientations(basePolyomino):
    def rotate90(polyomino: list[tuple[int]]) -> list[tuple[int]]:
        return [(sq[1], -sq[0]) for sq in polyomino]

    def reflectYAxis(polyomino: list[tuple[int]]) -> list[tuple[int]]:
        return [(-sq[0], sq[1]) for sq in polyomino]

    def normalize(polyomino: list[tuple[int]]) -> list[tuple[int]]:
        xMax = max([t[0] for t in polyomino])
        yMax = max([t[1] for t in polyomino])
        return [(t[0] - xMax, t[1] - yMax) for t in polyomino]
    
    orientations = [basePolyomino]    
    for _ in range(3):
        orientations.append(rotate90(orientations[-1]))
    for i in range(len(orientations)):
        orientations.append(reflectYAxis(orientations[i]))
    return set(frozenset(normalize(polyomino)) for polyomino in orientations)

#-----------------------------------------------------
# Get all  individual polyomino placements in the grid
#-----------------------------------------------------
# polyominoname: str
# orientations: set[frozenset[tuple[int]]]
# grid: list[list[bool]]
#-----------------------------------------------------
def getPlacements(polyominoname, orientations, grid, clues):
    def satPolyominoClue(polyominoname, placement):
        if clues is None or polyominoname not in clues.keys():
            return True
        mustHaveY = clues[polyominoname][1] #one of the squares in placement must be the y value of the polyomino clue
        for (x, y) in placement:
            if y == mustHaveY:
                return True
        return False

    def tryPlacement(insertionCoordinate, orientation, grid):
        xMax, yMax = len(grid[0]), len(grid)
        placementInGrid = []
        for coordinate in orientation:
            (x, y) = utils.sumTuples(coordinate, insertionCoordinate)
            if x >= 0 and x < xMax and y >= 0 and y < yMax and grid[y][x]:
                placementInGrid.append((x, y))
            else:
                return None
        return placementInGrid
    
    placements = []
    for ori in orientations:
        for insertionCoordinate in gridCoordinates(grid):
            placement = tryPlacement(insertionCoordinate, ori, grid)
            if placement and satPolyominoClue(polyominoname, placement):
                placements.append(placement)
    return placements
