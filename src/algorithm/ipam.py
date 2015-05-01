import sys
import copy

MAX_LEVEL = 32

class Policies:
    ## n is #dimension. m is the #hosts
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


def add_to_dict(d, key, value):
    if (key in d):
        d[key].append(value)
    else:
        d[key] = [value]

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


class Term:
    id = 1
    def __init__(self, level, dims, subs = None):
        self.subs = subs
        self.level = level
        self.dims = dims
        self.edges = dict()
        self.id = Term.id
        Term.id = Term.id + 1

    def __str__(self):
        edge_str = ';'.join("{0}->{1}".format(x, y) for (x,y) in self.edges.items())
        sub_str = "None"
        if self.subs:
            sub_str = "({0},{1})".format(self.subs[0].id, self.subs[1].id)
        return "id{0}, L{1}, dims=[{2}], e={3}, subs={4}".format(self.id,
                                                                 self.level,
                                                                 ' '.join(self.dims),
                                                                 edge_str,
                                                                 sub_str)

def wildcard(policyAll):

    def get_terms(policy):
        counts = policy.count_values()
        terms = []
        for v, c in counts.items():
            for i in range(0, MAX_LEVEL):
                j = (1<<i)
                if (c & j) > 0:
                    term = Term(i, v.split(' '))
                    terms.append(term)
        return terms

    def eq_dims(term1, term2):
        indexes = set()
        for index in range(len(term1.dims)):
            if (index not in term1.edges) and (index not in term2.edges):
                if (term1.dims[index] != '*'):
                    if (term1.dims[index] == term2.dims[index]):
                        indexes.add(index)
        return indexes

    def mask_term(term1, term2, indexes):
        dims = ['*'] * len(term1.dims)
        for index in indexes:
            dims[index] = term1.dims[index]
        return Term(term1.level + 1, dims, (term1, term2, len(indexes)))

    ## work starts here
    termsAll = get_terms(policyAll)

    leveled_terms = dict()
    for term in termsAll:
        add_to_dict(leveled_terms, term.level, term)

    for level, terms in leveled_terms.items():
        print "level ", level
        print "\n".join("{}".format(t) for t in terms)

    for level in range(MAX_LEVEL):
        if (level not in leveled_terms):
            continue
        terms = leveled_terms[level]
        print level, len(terms)
        found = False
        ## enumerate a term
        for i in range(len(terms)):
            term_i = terms[i]
            if (len(term_i.dims) == len(term_i.edges)):
                continue
            ## enumerate the second term
            matches = []
            for j in range(i + 1, len(terms)):
                term_j = terms[j]
                if (len(term_j.dims) == len(term_j.edges)):
                    continue
                indexes = eq_dims(term_i, term_j)
                if (len(indexes) > 0):
                    matches.append((len(indexes), j, indexes))
            matches.sort(reverse = True)

            ## match up terms
            for (_, j, indexes) in matches:
                term_j = terms[j]
                indexes = indexes.difference(set(term_i.edges))
                if (len(indexes) == 0):
                    continue
                term_k = mask_term(term_i, term_j, indexes)
                add_to_dict(leveled_terms, term_k.level, term_k)
                for index in indexes:
                    term_i.edges[index] = term_k.id
                    term_j.edges[index] = term_k.id

    for level, terms in leveled_terms.items():
        for term in terms:
            if (term.subs == None):
                term.weight = 1
            else:
                term.weight = term.subs[0].weight + term.subs[1].weight + term.subs[2]

    print "After edges..."
    for level, terms in leveled_terms.items():
        print "level ", level
        print "\n".join("{0}, w={1}".format(t, t.weight) for t in terms)



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
    wildcard(p)
elif option == "ori":
    num_rules, nrules = ipam(p)
    print "heuristics:", num_rules, " =", nrules

    print "best:",
    for i in range(0, p.n):
        q = p.project(i)
        print ipam(q),
    print ""

