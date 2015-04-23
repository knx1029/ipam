import sys
import math
import random

def two(n1, n2):
    print n1 * n2, "2"
    for i in range(0, n1):
        for j in range(0, n2):
            print i, j


def rand(n, ms):
    print n, len(ms)
#    random.seed(1029)
    random.seed()
    for i in range(0, n):
        vs = map(lambda(m): random.randint(1, m),
                 ms)
        print " ".join(str(v) for v in vs)

def bld_group(nbuildings, ngroups, nusers_per_group):
    def rand_num_bld():
        xy = [(0.0, 1), (0.5, 2), (0.75, 3), (0.85, 4), (0.9, 5)]
        x_star = random.randint(1, 100) / 100.0
        y_star = 0
        for (x, y) in xy:
            if (x_star >= x) and (y >= y_star):
                y_star = y
        if (y_star > nbuildings):
            return nbuildings
        if (x_star <= 0.9):
            return y_star

        a = (5.0 - nbuildings) / math.log(0.9)
        y_star = int(a * math.log(x_star) + nbuildings)
        return y_star

    random.seed()
    nusers = nusers_per_group * ngroups
    print nusers, 2
    for i in range(ngroups):
        b = rand_num_bld()
#        print b
        blds = random.sample(range(0, nbuildings), b)
        k = 0
        for j in range(0, nusers_per_group):
            print i + 1, blds[k] + 1
            k = (k + 1) % b

# two(10, 10)
# rand(32, [3, 3, 3])
nb = int(sys.argv[1])
ng = int(sys.argv[2])
nu = int(sys.argv[3])
bld_group(nb, ng, nu)
