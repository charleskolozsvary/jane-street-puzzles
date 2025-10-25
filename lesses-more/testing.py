def f(a, b, c, d):
    count = 1
    k = len(str(a))
    while(not(a == 0 and b == 0 and c == 0 and d == 0)):
        print(f'({a:{k}}, {b:{k}}, {c:{k}}, {d:{k}})')
        count += 1
        a_ = a
        a = abs(a-b)
        b = abs(b-c)
        c = abs(c-d)
        d = abs(d-a_)
    print(f'({a:{k}}, {b:{k}}, {c:{k}}, {d:{k}})')
    return count

if __name__ == '__main__':
    print("\n10")
    f(0,       2,       5,      11)
    print("\n11")
    f(0,       2,       6,      13)
    print("\n12")
    f(0,       5,      14,      31)
    print("\n13")
    f(0,       6,      17,      37)
    print("\n14")
    f(0,       7,      20,      44)
    print("\n15")
    f(0,      17,      48,     105)
    print("\n16")
    f(0,      20,      57,     125)
    print("\n17")
    f(0,      24,      68,     149)
    print("\n18")
    f(0,      57,     162,     355)
    print("\n19")
    f(0,      68,     193,     423)
    print("\n20")
    f(0,      81,     230,     504)

    
# from lesses_more import f
# f(10, 6, 3, 1)
# (10,  6,  3,  1)
# ( 4,  3,  2,  9)
# ( 1,  1,  7,  5)
# ( 0,  6,  2,  4)
# ( 6,  4,  2,  4)
# ( 2,  2,  2,  2)
# ( 0,  0,  0,  0)
# 7


