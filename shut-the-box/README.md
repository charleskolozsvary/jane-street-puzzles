# [Shut the Box](https://www.janestreet.com/puzzles/current-puzzle/) (November 2025)

## Description
Remove one or more orthogonally connected groups of cells from the grid. Each of these groups must have at least one cell which is part of the grid boundary, and the remaining cells in the grid must form an orthogonally connected component without any holes which can be folded to form a rectangular prism (the "box").

Cells marked with arrow(s) are *not* part of the box. They indicate the direction of the nearest cell which is.

Cells marked with a number *are* part of the box, and the number indicates how many cells also belong to the box which are within one king's move of the cell (including the numbered cell).

Cells marked with a gray circle must be opposite another cell marked with a gray circle once the box is assembled.

Cells marked with a gray square must be adjacent to (and on the same face as) another cell marked with a gray square once the box is assembled.

The answer to the puzzle is the product of the six sums of numbers on each face of the box.

## Approach
I was able to find by hand the net of the box (by filling in which cells in the given grid belong to the box) and then cut out the filled in cells and assemble the box. Though there were a just a couple of cells which couldn't be known with complete certainty, but they didn't confuse things that much.

However, I now want to write a program which creates an animation of the box assembling as the prism "stamps" the net.

I got the idea from skimming [this paper](https://vga.usask.ca/cccg2020/papers/Efficient%20Folding%20Algorithms%20for%20Regular%20Polyhedra.pdf).

It addresses how to determine if a polygon (net) can be folded into various regular polyhedra, giving specific focus to pentagons and dodecahedrons (the polyhedron whose sides are pentagons).

I'll represent the net in `net.py`, the prism in `prism.py` and the algorithm for assembling the box in `folding.py`

## Folding nets into boxes
Given the surface area of the net, we can search for all possible rectangular prisms whose dimensions give the surface area. If the prism's dimensions are all different, there are six starting orientations of the prism. If two are the same, there are three, and if they are all the same there's only one.

Given a fixed orientation of the prism $Q$, and the polygonal net, $P$, we want to determine if $P$ can fold into $Q$. We do this by enumerating all pairs of points in the net $p_i \in P$[^1] and along the boundary of the bottom face of $q_i \in Q$, translating the prism by the starting point they form and then "stamping" the prism about the net by tipping it in orthogonal directions (north, east, west, south).

If upon tipping in a direction
1. there aren't any prism faces which land on a cell in the net or
2. a prism face lands on a cell which has already been stamped
we return.

If after this DFS "rolling" we find that every face of the prism has been stamped to a corresponding cell in the net, then we know that the net can be folded into the prism, if not, we try another staring point formed from a pair ($p_i$, $q_j$).

I'm not interested in *every way* to fold the net into the prism, I stop as soon as I've found a single one.

[^1]: We would only need to check the points along the boundary of $P$, not inside of it, as Section 3.1.1 of the earlier linked paper mentions "no vertex of $Q$ exists inside of $P$." But finding the non-convex bounding of the net takes a bit more thought that I thought was worth it given that the grids I'm trying to solve are relatively small.