GIVE_X = lambda p: p[0]
GIVE_Y = lambda p: p[1]
GIVE_Z = lambda p: p[2]

def startingPrismOrientations(l, w, h):
    
    r90_xy = np.matrix([[0, -1, 0], [1, 0, 0], [0, 0, 1]])
    r90_xz = ROTATIONS['west']
    r90_yz = ROTATIONS['south']
    prism = Prism(l, w, h)
    orientations = set()
    
    def doAllRotations(pts):
        prev1 = pts
        prev2 = pts
        prev3 = pts
        for i in range(2): #why not
            for j in range(2):
                for k in range(2):
                    rotation_matrix = r90_xy**i * (r90_xz**j * (r90_yz**k))
                    print(rotation_matrix)
                    orientations.add(numpyPts2Frzset(normalize(np.array(np.transpose(rotation_matrix * np.transpose(pts))))))
                    
    doAllRotations(prism.points)

    def dimOfPoints(pts):
        max_x = max(map(GIVE_X, pts))
        max_y = max(map(GIVE_Y, pts))
        max_z = max(map(GIVE_Z, pts))
        return (max_x, max_y, max_z)

    dims = []
    for ori in orientations:
        dims += [dimOfPoints(ori)]
    print(len(orientations))
    print(len(dims))
    print(dims)

# points is nx3 numpy array
def numpyPts2Frzset(points):
    return frozenset([np2Tuple(p) for p in points])

# points is nx3 numpy array
def normalize(points):
    n_points = len(points)
    min_x = min(map(GIVE_X, points))
    min_y = min(map(GIVE_Y, points))
    min_z = min(map(GIVE_Z, points))
    return points - np.repeat([[min_x, min_y, min_z]], n_points, axis=0)
