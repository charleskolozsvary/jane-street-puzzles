import numpy as np
import math
import os
import itertools
from collections import Counter
from copy import deepcopy

ROTATIONS = {'east': np.array([[0, 0, 1],
                               [0, 1, 0],
                               [-1, 0, 0]]),
             
             'north': np.array([[1, 0, 0],
                                [0, 0, 1],
                                [0, -1, 0]]),
             
             'west': np.array([[0, 0, -1],
                               [0, 1, 0],
                               [1, 0, 0]]),
             
             'south': np.array([[1, 0, 0],
                                [0, 0, -1],
                                [0, 1, 0]])}

# Convert 1xn numpy array into tuple of n scalar integers.
def npArr2Tuple(arr):
    return tuple([int(a) for a in arr])

# Convert 4x3 numpy array into tuple of four scalar tuples.
# The scalar tuples are 3d points, where each coordinate is
# a standard python int, not a numpy Int64.
def npFace2Tuple(np_face):
    return tuple([npArr2Tuple(p) for p in np_face])

def zIsZero(point_3d):
    x, y, z = point_3d
    return z == 0

def writeObj(prism, fname):
    with open('{}.obj'.format(fname), 'w') as fh:
        fh.write('o\n')
        for p in prism.points:
            p = npArr2Tuple(p)
            fh.write('v {} {} {}\n'.format(p[0], p[1], p[2]))
        for f in prism.obj_faces:
            fh.write('f {} {} {} {}\n'.format(f[0]+1, f[1]+1, f[2]+1, f[3]+1)) # .obj uses 1 (not zero) indexing

def writeObjs(prisms, fnames):
    os.chdir('objs')
    for i, prism in enumerate(prisms):
        writeObj(prism, fnames[i])

class Prism:
    def __init__(self, dimensions):
        self.dimensions = dimensions

        l, w, h = dimensions        

        def getEdges(face):
            edges = []
            mutable = list(face)
            for i, p in enumerate(face):
                if type(p) == tuple:
                    edge1 = mutable.copy()
                    edge2 = mutable.copy()
                    edge1[i] = p[0]
                    edge2[i] = p[1]
                    edges.append(tuple(edge1))
                    edges.append(tuple(edge2))
            return edges
        

        names = ['left', 'right', 'front', 'back', 'bottom', 'top']
        j = 0
        self.face_to_edges = {}
        for i, dim in enumerate(dimensions):
            for close_far in [0, dim]:
                plane = tuple((0, dimensions[idx]) if idx != i else close_far for idx in range(len(dimensions)))
                self.face_to_edges[(plane, names[j])] = getEdges(plane)
                j += 1
        
        points = np.array([[x, y, z] for x in range(l+1) for y in range(w+1) for z in range(h+1)])
        
        obj_vertices = {npArr2Tuple(p):i for i,p in enumerate(points)} # for writing to .obj file
        obj_faces = []  # for writing to .obj file
        
        orig_faces = [] # numpy array of shape (num faces, 4, 3) 
        curr_faces = [] # same shape as orig_faces

        ihat = np.array([1, 0, 0])
        jhat = np.array([0, 1, 0])
        khat = np.array([0, 0, 1])

        self.sides = {i: [] for i in range(1, 7)}

        # Update obj_faces and orig_faces
        def addFace(pt, plane):
            x, y, z = pt
            face = []
            side = None
            # The order of the points in the face are important;
            # they must give the correct normal for 3D rendering
            if plane == 'xy':
                f = [pt, pt - jhat, pt - jhat + ihat, pt + ihat]
                if z == 0:
                    face = reversed(f)
                    side = 1
                else:
                    face = f
                    side = 2
            elif plane == 'xz':
                f = [pt, pt - ihat, pt - ihat + khat, pt + khat]
                if y == 0:
                    face = reversed(f)
                    side = 3
                else:
                    face = f
                    side = 4
            elif plane == 'yz':
                f = [pt, pt + jhat, pt + jhat + khat, pt + khat]
                if x == 0:
                    face = reversed(f)
                    side = 5
                else:
                    face = f
                    side = 6
            else:
                assert False, "Plane '{}' unrecognized.".format(str(plane))

            np_face = np.array(list(face))
            tuple_face = npFace2Tuple(np_face)
            
            if all(map(lambda p: p in obj_vertices, tuple_face)):
                obj_faces.append([obj_vertices[p] for p in tuple_face])
                orig_faces.append(np_face)
                self.sides[side].append(frozenset(tuple_face))
        
        for plane in ['xz', 'yz', 'xy']:
            for p in points:
                if plane == 'xy' and (p[2] == 0 or p[2] == h):
                    addFace(p, plane)
                if plane == 'xz' and (p[1] == 0 or p[1] == w):
                    addFace(p, plane)
                if plane == 'yz' and (p[0] == 0 or p[0] == l):
                    addFace(p, plane)
                    
        self.points = points
        self.obj_faces = obj_faces
        
        self.orig_faces = np.array(orig_faces)
        self.curr_faces = deepcopy(self.orig_faces)
        self.orig_face_tuples = [npFace2Tuple(f) for f in self.orig_faces]
        self.perimiter = self.genBottomPerimiter()

    def __repr__(self):
        return str({'dimensions': self.dimensions,
                    'perimiter': self.perimiter,
                    'len(points)': len(self.points),
                    'obj_faces': self.obj_faces,
                    'orig_faces': self.orig_faces,
                    'orig_face_tuples': self.orig_face_tuples,
                    'curr_faces': self.curr_faces})

    # Return the point the prism is rotated about when it tips in the given direction
    def tipAbout(self, direction):
        zZeroPoints = list(filter(zIsZero, self.points))
        xs = list(map(lambda p: p[0], zZeroPoints))
        ys = list(map(lambda p: p[1], zZeroPoints))    

        if direction == 'east':
            return (max(xs), 0, 0)
        elif direction == 'north':
            return (0, max(ys), 0)
        elif direction == 'west':
            return (min(xs), 0, 0)
        elif direction == 'south':
            return (0, min(ys), 0)
        else:
            assert False, "Direction '{}' not recognized.".format(str(direction))        

    # Tip the prism in the given direction
    def tip(self, direction):
        translation_point = self.tipAbout(direction)
        assert direction in ROTATIONS, "Direction '{}' unrecognized".format(str(direction))
        
        rotation_matrix = ROTATIONS[direction]

        # Update points
        self.points -= translation_point
        self.points = np.dot(rotation_matrix, self.points.transpose()).transpose()
        self.points += translation_point

        # Update faces
        self.curr_faces -= translation_point
        for i, face in enumerate(self.curr_faces):
            self.curr_faces[i] = np.dot(rotation_matrix, face.transpose()).transpose()
        self.curr_faces += translation_point

    # Return a dictionary of current z == 0 faces to original faces
    # keys and values are tuples like those returned by 'npFace2Tuple'
    def heightZeroToOrigFaces(self):
        h_zero_to_orig = {}
        for i, face in enumerate(self.curr_faces):
            if all(map(zIsZero, face)):
                h_zero_to_orig[frozenset(npFace2Tuple(face))] = frozenset(self.orig_face_tuples[i])
        return h_zero_to_orig

    def getSideFaces(self, plane):
        # an example plane would be (None, None, 0) which is the xy plane with z == 0
        # (None, 4, None) would be all points where y == 4
        def inPlane(point_3d):
            for i, value in enumerate(plane):
                if value is not None and point_3d[i] != value:
                    return False
            return True
        
        faces = set()
        length = 0
        for i, face in enumerate(self.curr_faces):
            if all(map(inPlane, face)):
                faces.add(frozenset(npFace2Tuple(face)))
                length += 1
        assert len(faces) == length
        return faces

    # Return points along perimiter of the original prism's
    # bottom face. Points are numpy nx3 arrays
    def genBottomPerimiter(self):
        l, w, h = self.dimensions
        perim = []
        for x in range(l+1):
            for y in range(w+1):
                if x == 0 or x == l or y == 0 or y == w:
                    perim.append([x, y, 0])
                    
        return np.array([p for p in perim])

    def translate(self, translation_point):
        self.points += translation_point
        self.curr_faces += translation_point

        def shiftTuple(tup, scalar):
            return tuple(map(lambda x: x + scalar, tup))

        def addToPlaneOrEdge(p_or_e):
            return tuple(p_or_e[i] + translation_point[i] if type(p_or_e[i]) != tuple else shiftTuple(p_or_e[i], translation_point[i]) for i in range(len(translation_point)))
        
        new_face_to_edges = {}
        for planepair, edges in self.face_to_edges.items():
            plane, name = planepair
            new_plane = addToPlaneOrEdge(plane)
            new_edges = [addToPlaneOrEdge(e) for e in edges]
            new_face_to_edges[(new_plane, name)] = new_edges

        self.face_to_edges = new_face_to_edges

# Return dictionary of dimensions to list of Prisms 
def startingPrisms(surface_area):
    max_dim = math.ceil((surface_area - 2)/4)+1
    possible_dimensions = []
    # This isn't efficient at all, but that's okay. We only need to do this once.
    # The surface area is at most 150, so there are at most 38**3 == 54874 iterations
    for l in range(1, max_dim):
        for w in range(1, max_dim):
            for h in range(1, max_dim):
                if surface_area == 2*(l*w + l*h + w*h):
                    dim = Counter([l, w, h])
                    if dim not in possible_dimensions:
                        possible_dimensions.append(dim)
                        
    # Turn counters back into tuples
    possible_dimensions = [tuple([val for val,freq in dim.items() for _ in range(freq)]) for dim in possible_dimensions]
                    
    starting_prisms = dict()
    for dim in possible_dimensions:
        orientations = set(itertools.permutations(dim, 3)) 
        starting_prisms[dim] = [Prism(ori) for ori in orientations] 
    
    return starting_prisms

def testTipping():
    prism = Prism((2, 1, 3))
    east = deepcopy(prism)
    east.tip('east')
    north = deepcopy(prism)
    north.tip('north')
    west = deepcopy(prism)
    west.tip('west')
    south = deepcopy(prism)
    south.tip('south')
    
    north_north = deepcopy(north)
    north_north.tip('north')
    north_north_east = deepcopy(north_north)
    north_north_east.tip('east')
    
    writeObjs([prism, east, north, west, south, north_north, north_north_east], 'prism east north west south north_north north_north_east'.split(' '))

def oldMain():
    # testTipping()
    s = startingPrisms(256)
    
    total = 0
    for key, value in s.items():
        print('prism dimensions:', key)
        print('     len(value):', len(value))
        print()
        total += len(value)
    print('      total starting prisms:', total)
    print('number of unique dimensions:', len(s))
    print()

    testPrism = list(s.values())[0][0]
    print(testPrism)

if __name__ == '__main__':
    prism = Prism((7, 6, 2))
    for plane, edges in prism.face_to_edges.items():
        print(plane, edges)
    print()
    prism.translate((6,13,0))
    for plane, edges in prism.face_to_edges.items():
        print(plane, edges)
    print()
    
            
            
