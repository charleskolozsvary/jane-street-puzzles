import numpy as np
from net import *
from prism import *
# net is a Net from net.py
# prism is a Prism from prism.py
def canFoldToPrism(net, prism):
    Q = prism.perimiter
    P = net.points
    for p in P:
        for q in Q:
            start_point = np.array(p) - np.array(q)
            
        
