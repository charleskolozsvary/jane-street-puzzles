import numpy as np

def sumTuples(t1: tuple[int], t2: tuple[int]) -> tuple[int]:
    assert len(t1) == len(t2), 'lengths of supplied tuples do not match'
    return tuple(sum(z) for z in zip(t1, t2))

def np2Tuple(oned_np_array):
    simple = []
    for t in tuple(oned_np_array):
        simple.append(float(t))
    return tuple(simple)

def npCorners2Tuple(np_corners):
    simple = []
    for corner in np_corners:
        simple.append(np2Tuple(corner))
    return tuple(simple)


# 90 degree rotations about each axis
ROTATIONS = {'x': np.array([[1, 0, 0],
                            [0, 0,-1],
                            [0, 1, 0]]),
             
             'inv(x)': np.array([[1, 0, 0],
                                 [0, 0, 1],
                                 [0,-1, 0]]),

             'y': np.array([[0, 0,-1],
                            [0, 1, 0],
                            [1, 0, 0]]),

             'inv(y)': np.array([[ 0, 0, 1],
                                 [ 0, 1, 0],
                                 [-1, 0, 0]]),

             'z': np.array([[0,-1, 0],
                            [1, 0, 0],
                            [0, 0, 1]]),

             'inv(z)': np.array([[ 0, 1, 0],
                                 [-1, 0, 0],
                                 [ 0, 0, 1]])}

FE_TOROT = {('left', 0):'z',
            ('left', 1):'inv(z)',
            ('left', 2):'y',
            ('left', 3):'inv(y)',

            ('right', 0):'inv(z)',
            ('right', 1):'z',
            ('right', 2):'inv(y)',
            ('right', 3):'y',

            ('front', 0):'inv(z)',
            ('front', 1):'z',
            ('front', 2):'x',
            ('front', 3):'inv(x)',

            ('back', 0):'z',
            ('back', 1):'inv(z)',
            ('back', 2):'inv(x)',
            ('back', 3):'x',

            ('bottom', 0):'inv(y)',
            ('bottom', 1):'y',
            ('bottom', 2):'inv(x)',
            ('bottom', 3):'x',

            ('top', 0):'y',
            ('top', 1):'inv(y)',
            ('top', 2):'x',
            ('top', 3):'inv(x)'}

def faceEdgeToRotation(face, edge):
    return ROTATIONS[FE_TOROT[(face, edge)]]
