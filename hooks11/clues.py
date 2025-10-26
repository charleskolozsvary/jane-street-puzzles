digits = {3: (2,0),
          2: (8,3),
          6: (0,5),
          7: (6,8)}

digitsdir = {(2,0): (0,1),
             (8,3): (-1,0),
             (0,5): (1,0),
             (6,8): (0,-1)}
polys = {
    'I': (0,8),
    'N': (0,3),
    'Z': (0,0),
    'V': (8,0),
    'X': (8,5),
    'U': (8,8)}

polydirs = {
    (0,8): (1, 0),
    (0,3): (1, 0),
    (0,0): (1, 0),
    (8,0): (-1, 0),
    (8,5): (-1, 0),
    (8,8): (-1, 0)}

filledsquares = {(4,4):1, (4,0):9, (5,1):8, (3,7):4, (4,8):5}

hook1 = (4,4)

expolys = {
    'U': (4,3),
    'Y': (0,0),
    'F': (4,1)}

expolydirs = {
    (4,3):(-1,0),
    (0,0):(1,0),
    (4,1):(-1,0)}

exfilledsquares = {(0,2):3,(1,2):2,(2,1):1,(2,3):3,(3,2):5,(4,0):4,(4,4):4}

exhook1 = (2, 1)

def makeClue(digits, digdirs, polys, polydirs, filledsquares, hook1coordinate):
    return {'digs':digits,'digdirs':digdirs,'polys':polys,'polydirs':polydirs,'filledsquares':filledsquares,'hook1coordinate':hook1coordinate}

CLUES = {9:makeClue(digits, digitsdir, polys, polydirs, filledsquares, hook1), 5: makeClue({}, {}, expolys, expolydirs, exfilledsquares, exhook1)}
