import julia
from julia.api import Julia
jl = Julia(compiled_modules=False)

print('Finished Julia(compiled_modules=False)')

from julia import Base
from julia import Optim

print('Finished from julia import Optim')

Base.setprecision(512)

def f(xin):
    x = xin[0]
    return -(375*x**33-289*x**84)

start_x = 0.2

res = Optim.optimize(f, [Base.big(start_x)], Optim.BFGS(), Optim.Options(g_tol=1e-150))

print(str(Optim.minimizer(res)[0]))

# Wolfram vs.
# Julia (in python):
# 0.98687493600918687291775868743778051722761975951145802547180973941661635931 vs.
# 0.986874936009186872917758687437780517227619759511458025471809739416616359316303938862023473755673032887460123873785031304698117000198743921915313722452944

# Alright. Killer we are in buisness to write a function which gives the probability of reaching *full count* given a p Let's do this an another python file
