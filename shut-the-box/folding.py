import numpy as np

def getRectangularPrism(l, w, h):
    points = np.array([[x, y, z] for x in range(l+1) for y in range(w+1) for z in range(h+1)])
    vertices = {tuple(p):i+1 for i,p in enumerate(points)}

    ihat = np.array([1, 0, 0])
    jhat = np.array([0, 1, 0])
    khat = np.array([0, 0, 1])

    faces = []

    def addFace(pt, plane):
        x, y, z = pt[0], pt[1], pt[2]
        ps = []
        if plane == 'xy':
            ps = [pt, pt - jhat, pt - jhat + ihat, pt + ihat]
            if z == 0:
                ps = reversed(ps)
        elif plane == 'xz':
            ps = [pt, pt - ihat, pt - ihat + khat, pt + khat]
            if y == 0:
                ps = reversed(ps)
        elif plane == 'yz':
            ps = [pt, pt + jhat, pt + jhat + khat, pt + khat]
            if x == 0:
                ps = reversed(ps)
        else:
            assert False
                
                
        ps = [tuple(p) for p in ps]
            
        if all(map(lambda p: p in vertices, ps)):
            faces.append([vertices[p] for p in ps])
        
    for plane in ['xz', 'yz', 'xy']:
        for p in points:
            if plane == 'xy' and (p[2] == 0 or p[2] == h):
                addFace(p, plane)
            if plane == 'xz' and (p[1] == 0 or p[1] == w):
                addFace(p, plane)
            if plane == 'yz' and (p[0] == 0 or p[0] == l):
                addFace(p, plane)

    with open('prism.obj', 'w') as obj:
        for p in points:
            obj.write('v {} {} {}\n'.format(p[0], p[1], p[2]))
        for f in faces:
            obj.write('f {} {} {} {}\n'.format(f[0], f[1], f[2], f[3]))
        
    


# Q = {starting face : current face} where are face (t1, t2, t3, t4) is four points counter clockwise
def faceDownFaces(Q):
    def faceZAllZero(face):
        t1, t2, t3, t4 = face
        return t1[2] == 0 and t2[2] == 0 and t3[2] == 0 and t4[2] == 0
    
    return list(filter(faceZAllZero, Q.values()))

# rotate p about q in direction d
def rotate(p, q, d):
    x,y,z = p

def tipQ(direction, Q):
    down_faces = faceDownFaces(Q)
    
    
    
if __name__ == '__main__':
    getRectangularPrism(50, 50, 1)
