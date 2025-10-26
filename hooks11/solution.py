import polyominoes
import hooks
import tikzify
from clues import CLUES
import utils

def computeAnswer(completeGrid):
    gridW = len(completeGrid)
    emptySquares = list(filter(lambda coor: not completeGrid[coor[1]][coor[0]], [(x, y) for y in range(len(completeGrid)) for x in range(len(completeGrid[y]))]))
    answer = 1

    def emptySquaresRemaining():
        if len(emptySquares) == 0:
            return False
        start = emptySquares[0]
        visited = set()
        def dfs(pos):
            visited.add(pos)
            for (x, y) in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                adjSquare = utils.sumTuples(pos, (x, y))
                (x, y) = adjSquare
                if (x >= 0 and x < gridW and y >= 0 and y < gridW) and (adjSquare not in visited) and completeGrid[y][x] == 0:
                    dfs(adjSquare)
        dfs(start)
        nonlocal answer
        answer *= len(visited)
        for v in visited:
            emptySquares.remove(v)
        return len(emptySquares) > 0

    while emptySquaresRemaining():
        continue
    
    return answer

def satsPolyominoPartitionSums(cover, completeGrid):
    for polyominoname, placement in cover.items():
        if sum([completeGrid[y][x] for (x, y) in placement]) % 5 != 0:
            return False
    return True

# 1. hpartition['hooks']['toCoordinates'] gives a dictionary {hookNum : list of grid coordinates that belong to hookNum}
# 2. hpartition['dhpartners'] gives a dictionary {digit : hookNum}
def fillPolyominoesWithDigits(gridW, cover, hpartition):
    digmem = hpartition['dhpartners']
    hookmem = {hookNum : digit for digit, hookNum in digmem.items()}
    hgrid = hpartition['hooks']['grid']    

    completedGrid = polyominoes.makeGrid(gridW, gridW, 0)
    remDigs = {d:d for d in range(1, gridW+1)}
    placedCoors = []
    for polyominoname, placement in cover.items():
        for (x, y) in placement:
            hookNum = hgrid[y][x]
            digit = hookmem[hookNum]
            if remDigs[digit] >= 1:
                completedGrid[y][x] = digit
                remDigs[digit] -= 1
                placedCoors.append((x, y))
            else:
                return 'no dice', cover, hpartition, completedGrid
    return completedGrid
    
def solve(gridW):
    dimension = '{n}x{n}'.format(n=gridW)
    hookps = utils.load_variable('vhps-{}.pkl'.format(dimension))
    covers = utils.load_variable('covers-{}.pkl'.format(dimension))

    solutions = []
    def resolvePartitions(hookpartition, covers):
        for cover in covers:
            completeGrid = fillPolyominoesWithDigits(gridW, cover, hookpartition)
            if type(completeGrid) is not tuple and satsPolyominoPartitionSums(cover, completeGrid):
                print('not a tuple:', completeGrid)
                solutions.append({'polypartition':cover, 'hookpartition':hookpartition, 'completeGrid':completeGrid})
                
    for hookpartition in hookps:
        resolvePartitions(hookpartition, covers)
    
    for i, solution in enumerate(solutions): 
        print(solution)
        answer = 'The product of the areas of the connected unfilled squares is {}'.format(computeAnswer(solution['completeGrid']))
        tikzify.drawSolution(solution['polypartition'], solution['hookpartition'], CLUES[gridW], answer, '{}solution-{}'.format(dimension, i))
            
if __name__ == '__main__':
    solve(5)
    solve(9)
