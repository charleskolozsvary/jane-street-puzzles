import julia
from julia.api import Julia
jl = Julia(compiled_modules=False)

print('Finished Julia(compiled_modules=False)')

from julia import Base
from julia import Optim

print('Loaded Base and Optim')

from robotbaseball import calculate_q
from q_polynomial import Q_FORMULA

print('Loaded calculate_q from baseball.py')

Base.setprecision(512)

def find_max(f, start_value):
    res = Optim.optimize(lambda x: -f(x[0]), [Base.big(start_value)], Optim.BFGS(), Optim.Options(g_tol=1e-300))
    maximizing_p = Optim.minimizer(res)[0] #Optim.minizer(res) gives a single element list
    max_q = f(maximizing_p)
    print(res)    
    print("p that maximizes q: {:1.10f}".format(float(maximizing_p)))
    print("         maximum q: {:1.10f}".format(float(max_q)))
    print()

start_p = 0.5

print()
print("Maximizing calculate_q from robotbaseball.py")
find_max(calculate_q, start_p)

print("Maximizing Q_FORMULA from q_polynomial.py")
find_max(Q_FORMULA, start_p)
