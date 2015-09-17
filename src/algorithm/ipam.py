import sys
import copy
import heapq
from ipam_ds import *
import new_ipam

## read in all inputs (may be multiple sets)
def readin(input_filename, compact, multi):
    fin = open(input_filename, "r")    
    if (multi):
        inputs = []
        while (True):
            line = fin.readline()
            if (line == None) or (len(line) == 0):
                break
            nbits = int(line)
            input = readin_policies(fin, compact)
            if (input == None):
                return None
            inputs.append((input[0], input[1], nbits))
        fin.close()
        return inputs
    else:
        input = readin_policies(fin, compact)
        fin.close()
        return input

## read in a single set of input
def readin_policies(fin, compact):
    ## input uses 0 to stand for * to denote patterns
    def strd(d):
        if (d == 0): 
            return WC
        else:
            return str(d)

    ## starts here
    line = fin.readline()
    tokens = line.split(' ')
    ## number of elements in the domain
    m = int(tokens[0])
    ## number of functions
    n = int(tokens[1])
    ## number of patterns
    r = int(tokens[2])

    ## readin values of the elements in functions
    if (compact):
        values = dict()
        for i in range(0, m):
            line = fin.readline()
            tokens = line.split(' ')
            vs = map(int, tokens)
            if (len(vs) != n + 1):
                return None
            key = ' '.join(str(v) for v in vs[0:n])
            values[key] = vs[n]
    else:
        values = []
        for i in range(0, m):
            line = fin.readline()
            tokens = line.split(' ')
            vs = map(int, tokens)
            if (len(vs) != n):
                return None
            newline = ' '.join(str(v) for v in vs)
            values.append(newline)

    if (len(values) != m):
        return None
    policies = Policies(n, m, values, compact)

    ## readin the combinations of function values and their weights
    patterns = set()
    for i in range(0, r):
        line = fin.readline()
        tokens = line.split(' ')
        if (len(tokens) != n + 1):
            return None
        w = int(tokens[n])
        vs = map(int, tokens[:n])
        dims = map(strd, vs)
        patterns.add(Pattern(dims, w))

    return policies, patterns

## this is the ipam for prefix-based solution
def prefix(policies, patterns):
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

    def mask(d1, d2):
        d3 = [None] * len(d1)
        for i in range(len(d1)):
            if (d1[i] == d2[i]):
                d3[i] = d1[i]
            else:
                d3[i] = WC
        return d3

    ## work starts here
    counts = policies.counts
    terms = []
    repr_cnt = [0] * len(patterns)
    for keys, c in counts.items():
        x = 1
        dims = keys.split(' ')
        while (c >= x):
            if (c & x) > 0:
                terms.append((x, dims))
                for i, p in enumerate(patterns):
                    if (p.contain(dims)):
                        repr_cnt[i] = repr_cnt[i] + 1
            x = x << 1

    while (len(terms) > 1):
        min_x = terms[0][0]
        for x1, _ in terms:
            min_x = min(min_x, x1)

        best_repr = -1
        best_j1 = -1
        best_j2 = -1
        for j1 in range(len(terms)):
            x1, d1 = terms[j1]
            if (min_x != x1):
                continue
            for j2 in range(j1 + 1, len(terms)):
                x2, d2 = terms[j2]
                if (x1 != x2):
                    continue
                repr_total = 0
                for i, p in enumerate(patterns):
                    if (p.contain(d1)) and (p.contain(d2)):
                        repr_total = repr_total + repr_cnt[i]
#                        repr_total = repr_total + 1
                if (repr_total > best_repr):
                    best_repr = repr_total
                    best_j1 = j1
                    best_j2 = j2

        if (best_repr < 0):
            break
        x1, d1 = terms[best_j1]
        x2, d2 = terms[best_j2]
        for i, p in enumerate(patterns):
            if (p.contain(d1)) and (p.contain(d2)):
                repr_cnt[i] = repr_cnt[i] - 1
        terms.pop(best_j2)
        terms.pop(best_j1)
        d3 = mask(d1, d2)
        terms.append((x1 << 1, d3))

    grouped_pattern_idx = [8, 24, 31, 37, 39, 42]
    curterm = 0
    for i in range(len(patterns)):
        print "max_term", repr_cnt[i]
        curterm = curterm + repr_cnt[i]
        if ((i + 1) in grouped_pattern_idx):
            print "current_term", curterm
            curterm = 0
    print ""
    ##

    '''
    counts = policy.counts
    num_rules = 0
    for c in counts.values():
        num_rules = num_rules + ones(c)

    if (policy.n == 1):
        return num_rules

    nrules = [0] * policy.n
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
    '''

## construct terms from the policy
## connect terms based on patterns 
def get_leveled_terms(policies, patterns):

    ## append value to d[key]
    def add_to_dict(d, key, value):
        if (key in d):
            d[key].append(value)
        else:
            d[key] = [value]

    ## extract terms from the policy
    def get_terms(policy, patterns):
        counts = policy.counts
        terms = []
        for v, c in counts.items():
            dims = v.split(' ')
            sum_ps = 0
            pattern_keys = set()
            for p in patterns:
                if (p.contain(dims)):
                    sum_ps = sum_ps + p.weight
                    pattern_keys.add(p)
            for i in range(0, Pyramid.nbits):
                j = (1<<i)
                if (c & j) > 0:
                    term = Term(i, v.split(' '), 0, sum_ps, None, pattern_keys)
                    terms.append(term)
        return terms

    ## find the patterns that two terms share
    def eq_patterns(term1, term2, patterns):
        ps = set()
        for pattern in term1.pattern_keys:
            if ((pattern in term2.pattern_keys) and
                (pattern not in term1.edges) and
                (pattern not in term2.edges)):
                ps.add(pattern)
        return ps

    ## sum up the weights of patterns
    def sum_ps_weight(ps):
        if (len(ps) == 0):
            return 0
        else:
            return sum(map(lambda(x):x.weight, ps))

    ## aggregate two terms into a term with their
    ## common dimension values
    def mask_term(term1, term2, ps):
        dims = copy.copy(term1.dims)
        for i in range(len(term1.dims)):
            if (term1.dims[i] == term2.dims[i]):
                dims[i] = term1.dims[i]
            else:
                dims[i] = WC

        sum_ps =  sum_ps_weight(ps)
        return Term(term1.level + 1,
                    dims,
                    term1.weight + term2.weight + sum_ps,
                    sum_ps,
                    (term1, term2),
                    copy.copy(ps))


    ## work starts here

    ## get the atomic term (the term without * in the dims)
    atomic_terms = get_terms(policies, patterns)
    leveled_terms = dict()
    for term in atomic_terms:
        add_to_dict(leveled_terms, term.level, term)

    ## connect terms in the same level 
    ## to construct new terms (in the next level)
    for level in range(Pyramid.nbits):
        if (level not in leveled_terms):
            continue

        terms = leveled_terms[level]
        matches = []
        ## enumerate a term
        for i in range(len(terms)):
            term_i = terms[i]
            ## enumerate the second term
            for j in range(i + 1, len(terms)):
                term_j = terms[j]
                ps_ij = eq_patterns(term_i, term_j, patterns)
                if (len(ps_ij) > 0):
                    ## heapq is min heap
                    heapq.heappush(matches,
                                   (-sum_ps_weight(ps_ij), i, j, ps_ij))

        ## greedily match up terms
        while len(matches) > 0:
            tp, best_i, best_j, best_ps = heapq.heappop(matches)
            term_i = terms[best_i]
            term_j = terms[best_j]
            ## check the weight changes
            prev_weight = sum_ps_weight(best_ps)
            if (prev_weight == 0):
                continue
            best_ps.difference_update(set(term_i.edges))
            best_ps.difference_update(set(term_j.edges))
            best_weight = sum_ps_weight(best_ps)

            ## push back the match
            if (best_weight != prev_weight):
                if (best_weight > 0):
                    heapq.heappush(matches, 
                                   (best_weight,
                                    best_i, 
                                    best_j,
                                    best_ps))
            ## match two terms
            else:
                term_k = mask_term(term_i, term_j, best_ps)
                add_to_dict(leveled_terms, term_k.level, term_k)
                for p in best_ps:
                    term_i.edges[p] = term_k
                    term_j.edges[p] = term_k

    return leveled_terms
                            

## construct pyramids from terms
def construct_pyramids(leveled_terms):
    
    ## mark the term and its subtree as visited
    def mark_visited(term):
        if (term in visited_terms):
            return
        visited_terms.add(term)
        if (term.subs != None):
            mark_visited(term.subs[0])
            mark_visited(term.subs[1])
    
    ## recalculate the weight of terms
    def recalc_weight(term):
        if (term in visited_terms):
            term.weight = 0
            return 0
        if (term.subs != None):
            recalc_weight(term.subs[0])
            recalc_weight(term.subs[1])
            term.weight = (term.subs[0].weight + 
                           term.subs[1].weight + 
                           term.sum_ps)

    ## starts here
    pyramids = set()
    connections = []
    ## each atomic term is a pyramid
    for level, terms in leveled_terms.items():
        for term in terms:
            if (term.subs == None):
                py = Pyramid.one_term_pyramid(term)
                pyramids.add(py)
            else:
                connections.append(Conn(term))

    print "all", len(pyramids) + len(connections)
    ## use non-atomic term (i.e., connection) to merge pyramids
    ## sort those terms based on weight in descending order
    visited_terms = set()
    heapq.heapify(connections)
    while len(connections) > 0:
        ## check the weight
        conn = heapq.heappop(connections)
        if (conn.term in visited_terms):
            continue
        old_w = conn.term.weight
        recalc_weight(conn.term)
        if (old_w != conn.term.weight):
            heapq.heappush(connections, conn)
            continue

#        print "\nconnection", str(conn.term),

        ## try merging, if failed at any point, then revert
        temp_pyramids = {p.copy() for p in pyramids}
        temp_visited_terms = copy.copy(visited_terms)
        if (merge_pyramids(temp_pyramids, conn.term, temp_visited_terms)):
            res, _ = check_valid(temp_pyramids)
            if (res):
                pyramids = temp_pyramids
                visited_terms = temp_visited_terms

    ## mark the single atomic pyramid as visited
    for py in pyramids:
        ## single term pyramid
        if (len(py.terms) == 1):
            visited_terms.add(py.terms[0])

    print "visited", len(visited_terms)
#    print "\n".join(str(t) for t in visited_terms)
    print "before final_merge:", correct(pyramids)

    ## final merge
    final_pyramid = final_merge(pyramids)
    if (final_pyramid == None):
        print "WRONG FINAL"
    else:
        print "after final_merge:", correct([final_pyramid])
#        final_pyramid.show()

    return final_pyramid

## the full wildcard algorithm starts here
def wildcard(policies, patterns):
    ## connect terms and assign their weights
    leveled_terms = get_leveled_terms(policies, patterns)
    
    grouped_pattern_idx = [8, 24, 31, 37, 39, 42]

    ## count the min and max rules
    max_rules = 0
    min_rules = 0
    idx = 0
    curterm = 0
    for p in patterns:
#        print p.id, ":", p.dims
        minterm = 0
        maxterm = 0
        for level, terms in leveled_terms.items():
            for term in terms:
                #print str(term)
                if (p in term.pattern_keys):
#                if (p.contain(term.dims)):
#                    print str(term)
                    if (p not in term.edges):
                        min_rules = min_rules + p.weight
                        minterm = minterm + 1
                    if (term.subs == None):
                        max_rules = max_rules + p.weight
                        maxterm = maxterm + 1

        ## curterm, grouped_pattern_idx
        curterm = curterm + maxterm
        idx = idx + 1
        if (idx in grouped_pattern_idx):
            print "current_term", curterm
            curterm = 0
        ##
#        print "min_pattern", minterm
        print "max_pattern", maxterm

    ## merge pyramids based on connection terms
#    final_pyramid = None
    final_pyramid = construct_pyramids(leveled_terms)

    ## bit assignment
    ips = assign_bits(final_pyramid)
#    for term,ip in ips.items():
#        print str(term)
#        print ip

    ## count number of used rules
    use_rules = 0
    ## curterm, grouped_pattern_idx
    idx = 0
    curterm = 0
    ##
    if (final_pyramid != None):
        for p in patterns:
#            p.show()
            cterm = 0
            for term in final_pyramid.terms:
#                if (p.contain(term.dims)):
                if (p in term.pattern_keys):
                    if ((p not in term.edges) or 
                        (term.edges[p] not in final_pyramid.terms)):
                        cterm = cterm + 1
                        use_rules = use_rules + p.weight
#                        print ips[term],
            ## curterm, grouped_pattern_idx
            curterm = curterm + cterm
            idx = idx + 1
            if (idx in grouped_pattern_idx):
                print "current_term", curterm
                curterm = 0
            ## 
#            print ""
            print "ipam_pattern", cterm

    print "max_rules:", max_rules
    print "min_rules:", min_rules
    print "use_rules", use_rules
    print ""



def shorten(input_filename):
    inputs = readin(input_filename, False, False)
#    for (policies, patterns, nbits) in inputs:
    if True:
        policies, patterns = inputs
        counts = policies.counts
        for key in sorted(counts.keys()):
            print key, counts[key]

def ipam(input_filename, mode, nbits = None):
    option = "wildcard" #"prefix"
    new_old_option =  "new"
#    option = "prefix"
    if ("s" in mode):
        input = readin(input_filename, "c" in mode, False)
        if (input != None):
            policies, patterns = input
            Pyramid.nbits = int(nbits)
            if option == "wildcard":
                wildcard(policies, patterns)
            elif option == "prefix":
                num_rules, nrules = prefix(policies, patterns)
                print "heuristics:", sum(nrules)
    elif ("m" in mode):
        inputs = readin(input_filename, "c" in mode, True)
        if (inputs != None):
            for (policies, patterns, nbits) in inputs:
                Pyramid.nbits = nbits
                if option == "wildcard":
                    if (new_old_option == "new"):
                        new_ipam.new_wildcard(policies, patterns)
                    else:
                        wildcard(policies, patterns)
                elif option == "prefix":
                    if (new_old_option == "new"):
                        new_ipam.new_prefix(policies, patterns)
                    else:
                        prefix(policies, patterns)




