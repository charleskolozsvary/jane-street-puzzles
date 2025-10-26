import random
import itertools

from mixed_strategy_polynomials import STRATEGY_FORMULAS
from q_polynomial import Q_FORMULA

from mpmath import mp, mpf

MAX_B = 3
MAX_S = 2

def optimal_strategies(p):
    OSTR = {(b, s): None for b in range(MAX_B+1) for s in range(MAX_S+1)} # optimal strategy for each state
    
    V = {(b, s): None for b in range(MAX_B+1) for s in range(MAX_S+1)} # expected values for each state
    ## terminal states
    for v in [(4, 0), (4, 1), (4, 2)]:
        V[v] = 1 
    for v in [(0, 3), (1, 3), (2, 3), (3, 3)]:
        V[v] = 0

    def fill_state_info(balls, strikes):
        A = V[(balls+1, strikes)]
        B = V[(balls, strikes+1)]
        D = 4*p + (1-p)*B

        denom = A+D-2*B
        assert denom != 0, "denominator is zero"
        x = (D - B) / denom ## probability of throwing ball (also the probability of waiting --- symetric game)
        assert (not (x == 0 or x == 1)), "Not a mixed strategy"
        OSTR[(balls, strikes)] = x
        V[(balls, strikes)] = (A*D - B*B)/denom
        
    b, s = MAX_B, MAX_S
    while OSTR[(0,0)] is None:
        fill_state_info(b, s)
        for l in range(1, b+1):
            fill_state_info(b-l, s)
        for u in range(1, s+1):
            fill_state_info(b, s-u)
        b -= 1
        s -= 1
    return OSTR

## sequence of ball or strikes: True if ball, False if strike
PATHS = [[i in pair for i in range(5)] for pair in itertools.combinations([0, 1, 2, 3, 4], 3)]
        
## q is the probability of reaching full count (dependent on p)
def calculate_q(p):
    ## Step 1: find O[(b, s)] for all b in [0,3] and s in [0,2]
    oms = optimal_strategies(p)
    
    ## Step 2: sum probabilities of traversing each of the 10 paths from (0,0) to (3, 2)
    alpha = lambda x: x**2
    beta = lambda x: 1 - (x**2 + (1-x)**2*p)
    q = 0
    for path in PATHS:
        path_prob = 1
        b, s = 0, 0
        for transition in path:
            x = oms[(b, s)]
            if transition: #gets ball
                path_prob *= alpha(x)
                b += 1
            else:
                path_prob *= beta(x)
                s += 1
        q += path_prob
    return q

#------------------------------
# Testing
#------------------------------
def simulate_q(p, iters):
    oms = optimal_strategies(p)
    successes = 0
    def reachesFullCount():
        b, s = 0, 0
        while b < 4 and s < 3:
            if b == 3 and s == 2:
                return True            
            x = oms[(b, s)]
            wait = random.random() < x 
            ball = random.random() < x 
            if wait and ball:
                b += 1
            elif wait and (not ball):
                s += 1
            elif (not wait) and ball:
                s += 1
            else:
                if random.random() < p:
                    break
                else:
                    s += 1
        return b == 3 and s == 2
    
    for _ in range(iters):
        successes += 1 if reachesFullCount() else 0
    return successes / iters

def computed_vs_explicit_optimal_strategies(inc):
    p = mpf(str(inc))
    nmatch = 50
    def compare_to_explicit(oms, local_p):
        sf = STRATEGY_FORMULAS(local_p)
        for key in oms:
            first = '{:1.{w}f}'.format(float(oms[key]), w = nmatch)
            second = '{:1.{w}f}'.format(float(sf[key]), w = nmatch)
            assert first == second, "computed and explicit values do not match"
            print('{}: {} vs. {}'.format(key, first, second))
            
    while p < 1:
        print('p = {:1.5f}'.format(float(p)))
        oms = optimal_strategies(p) #computed
        compare_to_explicit(oms, p) 
        print()
        p += mpf(str(inc))

def computed_vs_simulated_q(inc, iters):
    p = inc
    while p < 1:
        qc = calculate_q(p)
        qs = simulate_q(p, iters)
        qf = Q_FORMULA(p)
        diff = abs(qc - qs)
        diffc = abs(qc-qf)
        print('p = {:1.2f}: ({:1.10f} and {:1.10f}, diff: {:1.6f}) vs. {:1.10f}, diff = {:1.5f}'.format(float(p), float(qf), float(qc), float(diffc), float(qs), float(diff)))
        print()
        p += inc
        
if __name__ == '__main__':
    computed_vs_explicit_optimal_strategies(0.0001)
    # computed_vs_simulated_q(.01, 1000000)
