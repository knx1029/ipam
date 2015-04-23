import sys

class Policies:
    def __init__(self, n, m, values):
        self.n = n
        self.m = m
        self.values = values

    def project(self, nth):
        def f(line):
            tokens = line.split(' ')
            return tokens[nth]

        if (nth >= self.n) or (nth < 0):
            return None
        if (self.n == 1):
            return self

        nth_values = map(f, self.values)
        return Policies(1, self.m, nth_values)

    def get_value(self, x):
        if (x >= self.n) or (x < 0):
            return None
        return self.values[x]

    def count_values(self):
        counts = dict()
        for v in self.values:
            if (v in counts):
                counts[v] = counts[v] + 1
            else:
                counts[v] = 1
        return counts

def readin_policies(input):
    fin = open(input, "r")    
    line = fin.readline()
    tokens = line.split(' ')
    ## number of elements in the domain
    m = int(tokens[0])
    ## number of functions
    n = int(tokens[1])
    values = []
    for i in range(0, m):
        line = fin.readline()
        tokens = line.split(' ')
        vs = map(int, tokens)
        if (len(vs) != n):
            return None
        newline = ' '.join(str(v) for v in vs)
#        values.append(vs)
        values.append(newline)
    if (len(values) != m):
        return None

    policies = Policies(n, m, values)
    return policies



def wildcard_two(policyC):

    def get_terms(policy):
        counts = policy.count_values()
        terms = dict()
        for v, c in counts.items():
            s = set()
            for i in range(0, 31):
                j = (1<<i)
                if (c & j) > 0:
                    s.add((i, j))
            terms[v] = s
        return terms

    ## work starts here
    policyA = policyC.project(0)
    policyB = policyC.project(1)

    termsA = get_terms(policyA)
    termsB = get_terms(policyB)
    termsC = get_terms(policyC)

    print "A"
    print "\n".join("{} {}".format(v, t) for (v, t) in sorted(termsA.items()))
    print "B"
    print "\n".join("{} {}".format(v, t) for (v, t) in sorted(termsB.items()))
    print "C"
    print "\n".join("{} {}".format(v, t) for (v, t) in sorted(termsC.items()))
    print "................."

    perfect_pairs = []
    temp_dont = []
    temp_undec = []
    for valueC, termC in termsC.items():
        tokens = valueC.split(' ')
        valueA = tokens[0]
        valueB = tokens[1]
        termA = termsA[valueA]
        termB = termsB[valueB]

        for term in termC:
            if (term in termB):
                if (term in termA):
                    perfect_pairs.append((valueA, valueB, term))
                    termB.remove(term)
                    termA.remove(term)
                else:
                    temp_dont.append((valueA, valueB, term))
                    termB.remove(term)
            else:
                temp_undec.append((valueA, valueB, term))

    print "A"
    print "\n".join("{} {}".format(v, t) for (v, t) in sorted(termsA.items()))
    print "B"
    print "\n".join("{} {}".format(v, t) for (v, t) in sorted(termsB.items()))
    print "................."
    print "perfect"
    print "\n".join(str(t) for t in perfect_pairs)

    ## match up the undecided ones
    termsK = dict()
    for valueA, valueB, term in temp_undec:
        termA = termsA[valueA]
        termB = termsB[valueB]

        if (valueB not in termsK):
            termsK[valueB] = []
        termK = termsK[valueB]

        ## find the smallest terma that is no smaller than term
        best_term = None
        for terma in termA:
            if (terma[1] >= term[1]):
                if best_term == None or terma[1] < best_term[1]:
                    best_term = terma
        termA.remove(best_term)
        if (best_term[1] > term[1]):
            termA.add((best_term[0], best_term[1] - term[1]))
        termK.append((term, (best_term[0], valueA)))

    print "to-be-decided"
    print "\n".join("{} {}".format(v, sorted(t)) for (v, t) in sorted(termsK.items()))


    decided_pairs = []
    for valueA, valueB, term in temp_dont:
        termA = termsA[valueA]
        termB = termsB[valueB]

        best_term = None
        for terma in termA:
            if (terma[1] >= term[1]):
                best_term = terma
                break
        termA.remove(best_term)
        if (best_term[1] > term[1]):
            termA.add((best_term[0], best_term[1] - term[1]))
        decided_pairs.append((valueB, term, (best_term[0], valueA)))

    print "pre-decide"
    print "\n".join(str(t) for t in decided_pairs)




#        print valueC, " : ", termA, " | ", termB, " | ", termC
    


def ipam(policy):
    def ones(x):
        y = 0
        while (x > 0):
            x = x & (x - 1)
            y = y + 1
        return y

    def value_equal(v1, v2, nth):
        if (v1 == None or v2 == None):
            return False
        l1 = int(v1.split(' ')[nth])
        l2 = int(v2.split(' ')[nth])
        return l1 == l2

    counts = policy.count_values()
    num_rules = 0
    for c in counts.values():
        num_rules = num_rules + ones(c)

    if (policy.n == 1):
        return num_rules

    nrules = [0] * policy.n
    print policy.n
    for nth in range(0, policy.n):
        last_v = None
        last_c = 0
        nrule = 0
        for v, c in counts.items():
            if (not value_equal(v, last_v, nth)) and (last_v != None):
                nrule = nrule + ones(last_c)
                last_c = 0
            last_c = last_c + c
            last_v = v
        if (last_v != None):
            nrule = nrule + ones(last_c)
        nrules[nth] = nrule

    return num_rules, nrules

    
input = sys.argv[1]
p = readin_policies(input)

option = "nanxi" # "ori"
# option = "ori"
if option == "nanxi":
    wildcard_two(p)
elif option == "ori":
    num_rules, nrules = ipam(p)
    print "heuristics:", num_rules, " =", nrules

    print "best:",
    for i in range(0, p.n):
        q = p.project(i)
        print ipam(q),
    print ""

