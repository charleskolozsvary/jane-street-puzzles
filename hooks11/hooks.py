from typing import Iterator, Callable, Any
import itertools
import utils

import tikzify
import polyominoes
from clues import CLUES

def tostr(digmem):
    return '\\string{'+(', '.join('{}:{}'.format(d,h) for d,h in digmem.items()))+'\\string}'
    
def digitToHookMembership(gridW, hookpartition):
    grid = hookpartition['hooks']['grid']
    
    clues = CLUES[gridW]
    
    digitclues = clues['digs']
    digitcluesdir = clues['digdirs']
    alreadyplacedDigits = clues['filledsquares']
    
    digtohookMem = {d : '$\\sqcup$' for d in range(1, gridW+1)}
    for coordinate, digit in alreadyplacedDigits.items():
        (x, y) = coordinate
        if digtohookMem[digit] != '$\\sqcup$' and grid[y][x] != digtohookMem[digit]: #assigned digit is in more than one hook (only applies to 5x5 grid) 
            return tostr(digtohookMem)+'\ndigit {} is in more than one hook'.format(digit) 
        if digit > grid[y][x]*2-1: # the digit is in a hook that is too small
            return tostr(digtohookMem)+'\nhook {} is too small for digit {}'.format(grid[y][x], digit)
        digtohookMem[digit] = grid[y][x]

    def digitsFightForHook():
        hookMembers = {h : set() for h in range(1, gridW+1)}
        for d, h in digtohookMem.items():
            if h != '$\\sqcup$' and type(h) is int:
                hookMembers[h].add(d)
        if max([len(dsbelongingtohook) for dsbelongingtohook in hookMembers.values()]) > 1:
            morethanone = list(filter(lambda x: len(hookMembers[x]) > 1, hookMembers.keys()))[0]
            return tostr(digtohookMem)+'\ndigits {} are fighting over hook {}'.format(','.join([str(d) for d in hookMembers[morethanone]]), morethanone)
        return False
    
    areFighting = digitsFightForHook()
    if areFighting:
        return areFighting

    def insideGrid(coordinate):
        (x, y) = coordinate
        return x >= 0 and x < gridW and y >= 0 and y < gridW        

    def possibleHookAssignments(digit: int): #possible hooks to assign to digit
        currPos = digitclues[digit]
        moveDirection = digitcluesdir[currPos]
        possibleHooks = set() # that this digit belongs to
        while insideGrid(currPos):
            (x, y) = currPos
            hookNum = grid[y][x]
            if hookNum not in digtohookMem.values() and digit <= hookNum*2-1:
                possibleHooks.add(hookNum)
            currPos = utils.sumTuples(currPos, moveDirection)
        possibleHooks = list(possibleHooks)
        return possibleHooks[0] if len(possibleHooks) == 1 else possibleHooks

    haveNoAssignment = list(filter(lambda d : d not in alreadyplacedDigits.values(), digtohookMem.keys()))

    for digit in haveNoAssignment:
        digtohookMem[digit] = possibleHookAssignments(digit)

    def narrowedMembership():
        narrowed = False
        reverseMem = {tuple(hook) if type(hook) is list else hook: digit for digit, hook in digtohookMem.items()}
        for digit, hook in digtohookMem.items():
            if type(hook) is list:
                for h in hook:
                    if h not in reverseMem:
                        continue
                    digtohookMem[digit].remove(h)
                    narrowed = True
        for digit, hook in digtohookMem.items():
            if type(hook) is list and len(hook) == 1:
                digtohookMem[digit] = hook[0]
                narrowed = True
        return narrowed

    while narrowedMembership():
        continue

    areFighting = digitsFightForHook()
    if areFighting:
        return areFighting

    def moreUncertainDigitsThanAvailableHooks():
        uncertainDigits = list(filter(lambda d: type(digtohookMem[d]) is list and digtohookMem[d] != [], digtohookMem))
        availableHooks = set()
        for digit in uncertainDigits:
            for hook in digtohookMem[digit]:
                availableHooks.add(hook)
        if len(uncertainDigits) > len(availableHooks):
            dlist = ','.join([str(d) for d in uncertainDigits])
            hlist = ','.join([str(h) for h in availableHooks])
            return tostr(digtohookMem)+'\nthere are more uncertain digits ({}) than available hooks ({})'.format(dlist, hlist)
        return False
    
    lackOfHooks = moreUncertainDigitsThanAvailableHooks()
    if lackOfHooks:
        return lackOfHooks

    hasEmpty = any([1 if h == [] else 0 for h in digtohookMem.values()])
    if hasEmpty:
        emptyDigs = list(filter(lambda d: digtohookMem[d] == [], digtohookMem))
        return tostr(digtohookMem)+'\ndigit(s) {} cannot be assigned to any hook'.format(','.join([str(d) for d in emptyDigs]))
    
    return digtohookMem

#==================================================================================================
# i in [0, ntotHookPartitions-1]
# hookPartitions[i]['hooks']['grid'][y][x] == hookNum at coordinate (x, y)
# hooks = hookPartitions[i]['hooks']
# hookPartitions[i]['hooks']['toCoordinates'][hookNum] == list of coordinates (x, y) where
#                                                        hooks['grid'][y][x] == hookNum
#
# hookPartitions[i]['corners'] == a corner sequence, a list of corners that encode a hook partition,
#                                 e.g., ['BL', 'TR', 'TL', 'BR'] for a grid of width 5
#===================================================================================================
def generateHookPartitions(gridW: int):
    #--------------------------------------------------------
    # corner is either 'TL', 'TR', 'BL', or 'BR'
    #--------------------------------------------------------
    def fillHook(grid, coordinates, corner, bounds, hookNum):    
        hSide, vSide = bounds[corner[0]], bounds[corner[1]]
        for x in range(len(grid)):
            if grid[hSide][x] is None:
                grid[hSide][x] = hookNum
                coordinates[hookNum].add((x, hSide))
        for y in range(len(grid)):
            if grid[y][vSide] is None:
                grid[y][vSide] = hookNum
                coordinates[hookNum].add((vSide, y))
        return grid, coordinates
    #----------------------------------------------------------------------------------------
    # A corner is just one of four pairs of sides in a square, denoted with two letters;
    # a hook is a contiguous set of squares in an 'L' shape (with equal sides) within the grid
    # A grid of width w can be partitioned into hooks with a corner sequence of length w-1
    #-----------------------------------------------------------------------------------------
    # corners: list[str]: sequence of corners
    # hooks['grid']: list[list[int]] hooks['grid'][y][x] gives the hookNum at coordinate (x, y)
    # hooks['toCoordinates']: dictionary of hook number to set of coordinates that belong to
    #                       the hook number in the grid
    #-----------------------------------------------------------------------------------------
    def corners2hooks(corners: list[str]):
        gridW = len(corners)+1
        grid = [[None for _ in range(gridW)] for _ in range(gridW)]
        hookToCoordinates = {i: set() for i in range(1, gridW+1)}
        bounds = {'L': 0, 'B': 0, 'T': gridW-1, 'R': gridW-1}
        for i, corner in enumerate(corners):
            grid, hookToCoordinates = fillHook(grid, hookToCoordinates, corner, bounds, gridW-i)
            bounds[corner[0]] += 1 if corner[0] == 'B' else -1
            bounds[corner[1]] += 1 if corner[1] == 'L' else -1
        
        assert(bounds['B'] == bounds['T'] and bounds['L'] == bounds['R']) #only one place to put the last hook
        grid[bounds['B']][bounds['L']] = 1
        hookToCoordinates[1].add((bounds['L'], bounds['B']))

        for hookNum, coordinates in hookToCoordinates.items():
            hookToCoordinates[hookNum] = sorted(list(coordinates))
        return {'grid': grid, 'toCoordinates':hookToCoordinates}

    cornerSequences = list(itertools.product(['TL', 'TR', 'BR', 'BL'], repeat=gridW-1))
    hookPartitions = [{'corners': corners, 'hooks': corners2hooks(corners)} for corners in cornerSequences]
    return hookPartitions

#------------------------------------------------
# filter only using the coordinate of hook 1
#------------------------------------------------
def hook1Filter(hookPartitions, hook1Coordinate):
    (x, y) = hook1Coordinate
    def hook1Matches(hookPartition):
        return hookPartition['hooks']['grid'][y][x] == 1
    return list(filter(hook1Matches, hookPartitions))

def writeVHPS(gridW, debug = False):
    clues = CLUES[gridW]
    allhp = generateHookPartitions(gridW)
    print('len(allhp):', len(allhp))
    filteredHPs  = hook1Filter(allhp, clues['hook1coordinate'])
    print('len(filteredHPs):', len(filteredHPs))
    dhmems = [digitToHookMembership(gridW, fhp) for fhp in filteredHPs]

    if debug:
        labels = [tostr(dhmem) if type(dhmem) != str else dhmem for dhmem in dhmems]
        allhps = [{'dhpartners': dhmems[i], 'hooks': filteredHPs[i]['hooks'], 'corners': filteredHPs[i]['corners']} for i in range(len(filteredHPs))]
        tikzify.drawHookPartitions(allhps, 1, labels, 'debug-digit-assignments{w}x{w}'.format(w=gridW), maxDraw=750)
    
    validIdxs = list(filter(lambda i: type(dhmems[i]) is not str, range(len(dhmems))))
    vhps = [{'dhpartners': dhmems[i], 'hooks': filteredHPs[i]['hooks'], 'corners': filteredHPs[i]['corners']} for i in validIdxs]
    print('number of valid hook partitions: ', len(vhps))

    utils.save_variable('vhps-{w}x{w}.pkl'.format(w=gridW), vhps)
    
    return vhps
    
if __name__ == '__main__':
    vhps5 = writeVHPS(5)
    vhps9 = writeVHPS(9)
    # def drawHookPartitions(hookPartitions, perLine, labels, filename, maxDraw = None, validIdxs = []):    
    tikzify.drawHookPartitions(vhps5, 1, ['' for _ in range(len(vhps5))], 'vhps-5x5')
    tikzify.drawHookPartitions(vhps9, 1, ['' for _ in range(len(vhps9))], 'vhps-9x9')    

    
    
