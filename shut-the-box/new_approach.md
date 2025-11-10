I want to represent the folding.

At the initial state some face is in contact with a number of cells in the net. There are then four edges of the prism along which we can form a crease.

if we start with the face in contact being the bottom, we can fold along the top, left, right, or bottom edge of the prism.

To make this fold we need to

1. specify an edge to form the crease
2. identify the net constituents corresponding to that crease
3. perform the rotation on the constituents

After we've made the fold we need to identify again which edges can next be folded over and repeat the process.

When we start, there are four edges we can possible fold.

Let's consider the right edge.

The constituents of the net involved with this fold will be the connected component of the cells which are right-adjacent to the edge of the prism in the same plane as the prisms current stamping face. I.e. it starts with the cells which share a point with the edge of the prism and we only expand the connected component to the cells which are in a direction other than the opposite of the starting cells which share an edge with the prism.


So if the current stamping face is down and we fold along the right edge, the starting cells of the connected component are those who have two points belonging to the edge and two points to the right (greater) than the edge points. Then we expand the constituent of cells by first looking in directions other than to the left (the opposite of the chosen edge direction) and then expand the rest of the connected cells as usual, returning when we encounter a cells we've already visited.


This gives us which cells are involved in the fold.


Then we transform the cells (rotate them) to make the crease.

After transformation, we see which cells in the constituent are now in contact with the right prism face and that is the new stamping face going forward.

Now since we just used the bottom right edge for the last fold, we cannot fold along that same edge again for this constituent.

We can only choose the right front, right back, and right top edges of the prism.

We try to make a fold for each of these edges.

Let's consider the right front edge.

we find the sub constituent of the net that will be folded along this edge by including seed cells which share two points with the edge and whose other two points are forward of the edge (coming toward me from the screen).

Then we expand the connected component by looking in directions other than negative y.

Then we perform the rotation along the edge, rotating negative 90 degrees counter clockwise about the z axis (rotating the xy plane).


And then we continue.


So when we look for the connected components, we need to identify the plane in which the constituent cells are in.


if it is in plane ab, then (all planes being a, b, or c) we look ±a and ±b and ignore c.


We will still identify cells by their originally bottom left point when they are in the xy plane.



The Net object:

keys of cell_orientations are the same as cells: these are the original xy plane faces

cells: {set of four 3d points: a Cell object}

cell_orientations: {set of four 3d points: current set of four 3d points}


The initial Cell object:

        self.position = (x, y, 0)
        self.corners = set([(x, y, 0), (x+1, y, 0), (x, y+1, 0), (x+1, y+1, 0)])
	
        self.number = None
        self.circled = None
        self.squared = None

after rotation we need to update the positions and corners of each cell.

For now, we'll do this not using numpy, but using an individual 3D point rotater method which we can pass to `map`.



Now to think about the rotations.

There are twelve edges to the prism.

There are only two ways to fold over an edge, so there are at most 24 folding rotations

But these are only different because of the edge the rotations happen about, not the rotations themselves.

There are only three distinct rotations.

We can rotate about the x, y, or z axis, in plane with the yz, xz, or xy axis respectively.

Let's now name the faces of the prism.

there's the bottom, top, left, right, front, and back.

Along each face there are four folds.


For the bottom we have

-90 degrees along x for the bottom front edge
90 degrees along y for the bottom right edge
90 degrees along x for the bottom front edge
-90 degrees along y for the bottom left edge

The prism is now going to remain static and the net will be transformed.



