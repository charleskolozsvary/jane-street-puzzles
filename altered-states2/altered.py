def getFeasiblePaths(board, popDict, maxDepth) -> list[str]:
    paths = []
    directions = {'U': [-1, 0], 'UR': [-1, 1], 'R': [0, 1], 'DR': [1, 1], 'D': [1, 0], 'DL': [1, -1], 'L': [0, -1], 'UL': [-1, -1]}
    #-------------------------------------------------------------------------------------
    def rec(position, currStr, remainingPossibleStates, depth):
        noMoreStates, remStates = cantBeAnyState(currStr, remainingPossibleStates)
        if noMoreStates:
            return
        if depth == maxDepth:
            paths.append(currStr)
            return
        for dir in directions:
            newPos = (position[0] + directions[dir][0], position[1] + directions[dir][1])
            if newPos[0] >= 0 and newPos[0] < len(board) and newPos[1] >= 0 and newPos[1] < len(board):
                rec(newPos, currStr + board[newPos[0]][newPos[1]], remStates.copy(), depth + 1)
    #---------------------------------------------------------------------------------------
    for i in range(len(board)):
        for j in range(len(board[i])):
            rec((i, j), board[i][j], popDict.copy(), 1)
    return paths

def cantBeAnyState(s: str, rps):
    remainingPossibleStates = rps.copy()
    if len(s) <= 1:
        return False, remainingPossibleStates
    #--------------------------------------------------------------
    def cantBeState(s: str, state: str) -> bool:
        if len(s) > len(state):
            return True
        errors = 0
        for i, char in enumerate(s):
            if errors > 1:
                break
            if char != state[i]:
                errors += 1
        return errors > 1
    #--------------------------------------------------------------
    statesToRemove = []
    for state in remainingPossibleStates:
        if cantBeState(s, state):
            statesToRemove.append(state)
    for state in statesToRemove:
        del remainingPossibleStates[state]
    return len(remainingPossibleStates) == 0, remainingPossibleStates
            
def printBoard(board):
    for i in range(len(board)):
        for j in range(len(board[i])):
            print(board[i][j], end = ' ')
        print()
        
def preprocess(s: str, rem: list[str]) -> str:
    i = 0
    while(i < len(s)):
        if s[i] in rem:
            s = s[:i]+s[i+1:] if i+1 < len(s) else s[:i]
        else:
            i += 1
    res = s.split('\t')
    return res[0].upper(), int(res[1])

def getPopDict(filename: str):
    f = open(filename)
    lines = f.readlines(); f.close()
    remove = ['\n', ',', ' ']
    dict = {}
    for line in lines:
        key, value = preprocess(line, remove)
        dict[key] = value
    s_keys = sorted(dict, key = lambda x : dict[x], reverse = True)
    f_dict = {}
    for key in s_keys:
        f_dict[key] = dict[key]
    return f_dict
    
def stateLengthDict(popDict):
    dict = {}
    for state in popDict:
        length = len(state)
        if length in dict:
            dict[length].append(state)
        else:
            dict[length] = [state]
    return dict
    
def isAState(maybeState, state):
    errors = 0
    for i, char in enumerate(maybeState):
        if errors > 1:
            break
        if char != state[i]:
            errors += 1
    return errors <= 1 and len(maybeState) == len(state)
    
def scoreBoard(board, popDict):
    stateLenDict = stateLengthDict(popDict)
    statesFound = {} #dict with states found and all the paths that found it
    for length in stateLenDict:
        paths = getFeasiblePaths(board, popDict, maxDepth = length)
        for state in stateLenDict[length]:
            for path in paths:
                if isAState(path, state):
                    if state in statesFound:
                        statesFound[state].append(path)
                    else:
                        statesFound[state] = [path]
    score = 0
    for state in statesFound:
        score += popDict[state]
    return score, statesFound

if __name__ == '__main__':
    popDict = getPopDict('populations.txt')
    board = ['GFLSY',
             'EOILV',
             'YRNAC',
             'WETHS',
             'PJUOZ']
#    board = ['CALIF', 'TEXAS', 'OHIOR', 'ILLIN', 'FORNI']
    printBoard(board)
    boardString = ''
    for line in board:
        boardString += line
    print('board string:', repr(boardString.lower()))
    score, statesFound = scoreBoard(board, popDict)
    print('score:', score, '\nlen(statesFound):', len(statesFound))
    print()
    for state in statesFound:
        print(state)
        print('all possible paths:')
        print(statesFound[state], end = '\n\n')
