def optimalMixedStrategies(a, b, c, d):

    assert a+d-b-c != 0, "denominator is zero"
    
    x = (d-c)/(a+d-b-c)
    y = (d-b)/(a+d-b-c)

    if y == 1:
        x = 0
    elif y == 0:
        x = 1
    elif x == 1:
        y = 0
    elif x == 0:
        y = 1

    assert (not (y == 0 or y == 1)) and (not (x == 0 or x == 1)), "Not a mixed strategy"

    return (x, y)

def expectedPayout(a, b, c, d):
    return (a*d)/(a+d-b-c)

if __name__ == '__main__':
    print()
