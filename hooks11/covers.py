from polyominoes import PENTOMINOES, getPlacements, orientations, makeGrid
from clues import CLUES
import utils
import tikzify
import itertools
from copy import deepcopy

def makeProblemMatrix(grid, polys):
    gridW = len(grid[0])
    clues = CLUES[gridW]['polys'] if gridW in CLUES else None
    rows = {}
    idx = 0
    keys = set()
    
    for polyominoname, basePolyomino in polys.items():
        keys.add(polyominoname)
        oris = orientations(basePolyomino)
        placements = getPlacements(polyominoname, oris, grid, clues)
        for placement in placements:
            row = {polyominoname: 1}
            for square in placement:
                keys.add(square)
                row[square] = 1
            rows[idx] = row
            idx += 1
    return rows, keys

def withinGrid(gridW, pos):
    x, y = pos
    return x >= 0 and x < gridW and y >= 0 and y < gridW

def getCovers(gridW, rows, primaryKeys, prune2x2 = False):
    
    polyclues = CLUES[gridW]['polys'] if gridW in CLUES else None
    polydirs  = CLUES[gridW]['polydirs'] if gridW in CLUES else None
    
    pkCounts = {}
    for row in rows.values():
        for key in row:
            if key not in primaryKeys: 
                continue 
            if key in pkCounts:
                pkCounts[key] += 1
            else:
                pkCounts[key] = 1
    
    def chooseKey(counts): #choose key with minimum rows
        return {v:k for k,v in counts.items()}[min(counts.values())]
    
    solutions = [] #list of lists of row indices

    def existsFilled2x2(crow, curr_filled_squares):
        filledSquares = curr_filled_squares.copy()
        for key in crow:
            if type(key) is not tuple:
                continue
            filledSquares[key] = 1
        for x in range(gridW-1):
            for y in range(gridW-1):
                by2 = [(x,y), (x+1,y), (x,y+1), (x+1,y+1)]
                if all(map(lambda sq: sq in filledSquares, by2)):
                    return True
        return False

    def violatesPolyClue(crow, curr_filled_squares):
        filledSquares = curr_filled_squares.copy()
        newpoly = None
        newsquares = []
        for key in crow:
            if type(key) is not tuple:
                newpoly = key
            elif type(key) is tuple:
                newsquares.append(key)
        assert newpoly is not None 
        curr_polys = set(curr_filled_squares.values())
        curr_polys.add(newpoly)
        
        for sq in newsquares:
            filledSquares[sq] = newpoly

        for pname, start_pos in polyclues.items():
            if pname not in curr_polys:
                continue
            move = polydirs[start_pos]
            curr_pos = start_pos            
            while withinGrid(gridW, curr_pos):
                if curr_pos in filledSquares:
                    if filledSquares[curr_pos] == pname:
                        break
                    else:
                        return True
                        
                curr_pos = utils.sumTuples(curr_pos, move)
        return False
            
    def search(curr_sol, curr_rows, curr_kcounts, curr_filled_squares):
        if len(curr_kcounts) == 0:
            solutions.append(curr_sol)
            return
        
        coverKey = chooseKey(curr_kcounts)
        
        candidateRows = [] 
        for cridx, crow in curr_rows.items():
            if coverKey in crow:
                candidateRows.append(cridx)

        if len(candidateRows) == 0:
            return
        
        for chosenRowIdx in candidateRows:
            chRow = curr_rows[chosenRowIdx] 
            if prune2x2 and (existsFilled2x2(chRow, curr_filled_squares) or violatesPolyClue(chRow, curr_filled_squares)):
                continue
            
            next_sol = curr_sol.copy()
            next_rows = curr_rows.copy()
            next_kcounts = curr_kcounts.copy()
            next_filled_squares = curr_filled_squares.copy()
            
            next_sol.append(chosenRowIdx)            
            for cridx, crow in curr_rows.items():
                willDelete = False
                for key in crow:
                    if key in chRow:
                        willDelete = True
                        break
                if willDelete:
                    for key in crow:
                        if key in primaryKeys:
                            next_kcounts[key] -= 1
                    del next_rows[cridx]

            chpoly = None
            for key in chRow:
                if type(key) is str:
                    chpoly = key
                    break
            assert chpoly is not None, "somehow chpoly is still None"

            ## remove keys that belong to chosen row
            for key in chRow:
                if type(key) is tuple:
                    next_filled_squares[key] = chpoly
                if key not in primaryKeys:
                    continue
                assert next_kcounts[key] == 0
                del next_kcounts[key]
                    
            search(next_sol, next_rows, next_kcounts, next_filled_squares)
    
    search([], rows, pkCounts, {})

    return translateCovers(solutions, rows)

# The incoming covers are lists of row indices from the problem matrix.
# The outgoing covers are lists of dictionaries with polyomino names
# as keys and occupied squares as values
def translateCovers(covers_in, matrix):
    covers_out = []
    for cover_in in covers_in:
        cover_out = {}
        rows = [matrix[ridx] for ridx in cover_in]
        for row in rows:
            polyname = None
            squares = []
            for key in row:
                if type(key) is tuple:
                    squares.append(key)
                else:
                    assert polyname is None, "..."
                    polyname = key
            cover_out[polyname] = squares
        covers_out.append(cover_out)
    return covers_out

def filterCovers(gridW, covers, ntotsquares): 
    clues = CLUES[gridW]['polys']
    cluesDir = CLUES[gridW]['polydirs']
    
    def isOneConnectedComponent(cover):
        inverseEncoding = {(x, y) : polyominoname for polyominoname, placement in cover.items() for (x, y) in placement}
        
        startSquare = next(iter(inverseEncoding.keys()))
        visited = set()
        def dfs(pos):
            visited.add(pos)
            for adjD in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                adjSquare = utils.sumTuples(pos, adjD)
                if withinGrid(gridW, adjSquare) and (adjSquare in inverseEncoding) and (adjSquare not in visited):
                    dfs(adjSquare)
        dfs(startSquare)
        return len(visited) == ntotsquares

    def matchesPolyominoClues(cover):
        inverseEncoding = {(x, y) : polyominoname for polyominoname, placement in cover.items() for (x, y) in placement}                    
        for cluepolyomino, pos in clues.items():
            move = cluesDir[pos]
            while withinGrid(gridW, pos):
                if pos in inverseEncoding:
                    polyofsquare = inverseEncoding[pos]
                    if polyofsquare != cluepolyomino:
                        return False
                    else:
                        break
                pos = utils.sumTuples(pos, move)
        return True

    filteredCovers = []
    nonccCovers = []
    noncluesCovers = [] #should be zero
    
    for i, polys in enumerate(covers):
        if matchesPolyominoClues(polys):
            if isOneConnectedComponent(polys):
                filteredCovers.append(polys)
            else:
                nonccCovers.append(polys)
        else:
            noncluesCovers.append(polys)

    return filteredCovers, nonccCovers, noncluesCovers

def coversChess():
    polys = PENTOMINOES
    gridW = 8
    grid = makeGrid(gridW,gridW,1)
    emptySquares = [(3,3),(4,3),(3,4),(4,4)]    
    for (x, y) in emptySquares:
        grid[y][x] = 0
    matrix, keys = makeProblemMatrix(grid, polys)
    print(len(matrix))
    covers = getCovers(gridW, matrix, keys)
    print(len(covers))    

    tikzify.drawCovers(gridW, covers, 'chess-tilings')

def covers5x5():
    gridW = 5
    grid = makeGrid(gridW, gridW, 1)
    yfu = ['Y', 'F', 'U']
    afs = list(CLUES[gridW]['filledsquares'].keys())
    
    polys = {letter : PENTOMINOES[letter] for letter in yfu}
    primaryKeys = yfu + afs
    
    matrix, keys = makeProblemMatrix(grid, polys)
    covers = getCovers(gridW, matrix, primaryKeys, prune2x2 = True)
    print(len(covers))

    good, noncc, nonclues = filterCovers(gridW, covers, 15)
    print(len(good), len(noncc), len(nonclues))
    
    tikzify.drawCovers(gridW, good, 'good-example-covers')
    tikzify.drawCovers(gridW, noncc, 'noncc-example-covers')

    assert len(nonclues) == 0
    # def drawCovers(gridW, covers, filename, perLine = 1, maxDraw: int = None):
    
    utils.save_variable('covers-{w}x{w}.pkl'.format(w=gridW), good)

def covers9x9():
    gridW = 9
    clues = CLUES[gridW]

    afs = list(CLUES[gridW]['filledsquares'].keys())

    emptySquares = [(0,5),(2,0),(2,1),(5,3),(6,3),(7,3),(8,3)]
    
    grid = makeGrid(gridW, gridW, 1)
    for (x,y) in emptySquares:
        grid[y][x] = 0

    ntotsquares = gridW * 5
    allcovers = []
    
    known = set(clues['polys'].keys())
    unkown = set(PENTOMINOES.keys()) - known - {'P'} #P has a filled 2x2, so there's no need to consider it

    selections = sorted(list(itertools.combinations(unkown, 3)))

    noncc_covers = []
    
    for i, trio in enumerate(selections):
        polys = {pname : PENTOMINOES[pname] for pname in known.union(trio)}
        primaryKeys = list(polys.keys()) + afs
        print('run {}/{}'.format(i, len(selections)))
        print('chosen pentomino trio:', trio)
        matrix, keys = makeProblemMatrix(deepcopy(grid), polys)
        covers = getCovers(gridW, matrix, primaryKeys, prune2x2 = True)
        
        good, noncc, nonclues = filterCovers(gridW, covers, ntotsquares)
        print('    len(good):', len(good))
        print('   len(noncc):', len(noncc))
        print('len(nonclues):', len(nonclues)) #should always be zero
        print()
        
        allcovers += good
        noncc_covers += noncc

    print('len(allcovers):', len(allcovers)) #22567
    utils.save_variable('covers-9x9.pkl', allcovers)
    utils.save_variable('noncc-covers-9x9.pkl', noncc_covers)    

if __name__ == '__main__':
    coversChess()
    covers5x5()
    covers9x9()
