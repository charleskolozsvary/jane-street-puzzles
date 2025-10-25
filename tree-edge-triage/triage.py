from decimal import *

def seeIfConverge(cutoff, check, p):
    A = Decimal(1)
    B = Decimal(1)
    counter = 0
    while (counter < cutoff):
        counter += 1
        A = Decimal(Decimal(2)*p*B - p*p*B*B)
        B = Decimal(p*p*A*A)
        if (counter % check == 0):
            print(counter, A)
        if (not (A > 0)):
            print(A)
            print("Broke at depth = ", counter)
            return 0
    return 1

if __name__ == '__main__':
    seeIfConverge(1000000000, 1, Decimal(.75))
