using Symbolics
using Base
@variables p

#----------------------------------------------------------------------------------------
# I don't know if Base.GMP.BigInt propegates to the other constants, so I'm just going to
# add it to everything, even if it's unecessary
#----------------------------------------------------------------------------------------

# Expected reward for each state
V = Dict((3,2) => (Base.GMP.BigInt(4)*p) / (1 + Base.GMP.BigInt(4)*p))


# Terminal states
V[(3,3)] = 0
V[(2,3)] = 0
V[(1,3)] = 0
V[(0,3)] = 0
V[(4,2)] = 1
V[(4,1)] = 1
V[(4,0)] = 1

# Optimal mixed strategy for each state
O = Dict((3,2) => (Base.GMP.BigInt(4)*p) / (1 + Base.GMP.BigInt(4)*p))

function evaluate_state(b, s)
    A = V[(b+1, s)]
    B = V[(b, s+1)]
    D = Base.GMP.BigInt(4)*p + (Base.GMP.BigInt(1)-p) * B
    
    O[(b, s)] = (( p * (Base.GMP.BigInt(4) - B) ) / ( A + p*(Base.GMP.BigInt(4) - B) - B ) )
    V[(b, s)] = ( (A*D - B*B) / (A + p*(Base.GMP.BigInt(4) - B) - B) )
end

b = 3
s = 2

# find O[(0,0)]
while !haskey(O, (0,0))
    global b
    global s
    evaluate_state(b, s)
    for l = 1:b
	evaluate_state(b-l, s)
    end
    for u = 1:s
      	evaluate_state(b, s-u)
    end
    b = b-1
    s = s-1
end

if getindex(ARGS, 1) == "--s" #for strategies
    for (key, value) in O
        local b
        local s
        b, s = key
        print("$key: ", simplify(value), "\n\n")
    end
elseif getindex(ARGS, 1) == "--q" #for complete polynomial which evaulates to q

    for (key, value) in O
        O[key] = simplify(value)
    end

    paths = [[1, 1, 1, 0, 0], [1, 1, 0, 1, 0], [1, 1, 0, 0, 1], [1, 0, 1, 1, 0], [1, 0, 1, 0, 1], [1, 0, 0, 1, 1], [0, 1, 1, 1, 0], [0, 1, 1, 0, 1], [0, 1, 0, 1, 1], [0, 0, 1, 1, 1]]

    function alpha(x)
        ((x) * (x))
    end

    function beta(x)
        1 - (((x)*(x)) + ((1-x)*(1-x))*p)
    end

    q = 0

    for path in paths
        path_prob = 1
        global q
        local b
        local s
        b, s = 0, 0
        for transition in path
    	    x = O[(b, s)]
	    if transition == 1
	        path_prob *= alpha(x)
	        b += 1
	    else
	        path_prob *= beta(x)
	        s += 1
	    end
        end
        q += path_prob    
    end

    println(q)
else
    println("Please specify either '--s' for the strategy polynomials or '--q' for the entire explicit q polynomial")
end

