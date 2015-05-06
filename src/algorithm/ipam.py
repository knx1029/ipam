import sys
import copy
import heapq
from ipam_ds import *

MAX_LEVEL = 32

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


def get_leveled_terms(policyAll):
    ## extract terms from the policy
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

    ## find the dimensions that two terms share
    ## common values
    def eq_dims(term1, term2):
        indexes = set()
        for index in range(len(term1.dims)):
            if ((index not in term1.edges) and 
                (index not in term2.edges)):
                if (term1.dims[index] != '*'):
                    if (term1.dims[index] == term2.dims[index]):
                        indexes.add(index)
        return indexes

    ## aggregate two terms into a term with their
    ## common dimension values
    def mask_term(term1, term2, indexes):
        dims = ['*'] * len(term1.dims)
        for index in indexes:
            dims[index] = term1.dims[index]
        return Term(term1.level + 1,
                    dims,
                    (term1, term2),
                    term1.weight + term2.weight + len(indexes))

    ## work starts here
    termsAll = get_terms(policyAll)


    leveled_terms = dict()
    for term in termsAll:
        add_to_dict(leveled_terms, term.level, term)

    for level in range(MAX_LEVEL):
        if (level not in leveled_terms):
            continue

        terms = leveled_terms[level]
        matches = []
        ## enumerate a term
        for i in range(len(terms)):
            term_i = terms[i]
            if (len(term_i.dims) == len(term_i.edges)):
                continue
            ## enumerate the second term
            for j in range(i + 1, len(terms)):
                term_j = terms[j]
                if (len(term_j.dims) == len(term_j.edges)):
                    continue
                indexes = eq_dims(term_i, term_j)
                if (len(indexes) > 0):
                    ## heapq is min heap
#                    heapq.heappush(matches, (-len(indexes) + len(term_i.edges) + len(term_j.edges), i, j, indexes))
                    heapq.heappush(matches, (-len(indexes), i, j, indexes))
#                    heapq.heappush(matches, (-len(indexes) + term_i.weight + term_j.weight, i, j, indexes))

        ## match up terms
        while len(matches) > 0:
            tp, best_i, best_j, best_indexes = heapq.heappop(matches)
            term_i = terms[best_i]
            term_j = terms[best_j]
            prev_len = len(best_indexes)
            best_indexes.difference_update(set(term_i.edges))
            best_indexes.difference_update(set(term_j.edges))
            
            if (len(best_indexes) != prev_len):
                if (len(best_indexes) > 0):
                    heapq.heappush(matches, 
                                   (tp + len(best_indexes) - prev_len, 
                                    best_i, 
                                    best_j,
                                    best_indexes))
            else:
                term_k = mask_term(term_i, term_j, best_indexes)
                add_to_dict(leveled_terms, term_k.level, term_k)
                for index in best_indexes:
                    term_i.edges[index] = term_k
                    term_j.edges[index] = term_k

    return leveled_terms


def correct(pyramids):
    for py in pyramids:
        for term in py.terms:
            bv = py.repr(term)
            ## check level
            if (term.level != bv.level()):
                print "unmatched level", str(id), "<->", str(bv)
                return False
            ## check subs
            if (term.subs != None):
                bv0 = py.repr(term.subs[0])
                bv1 = py.repr(term.subs[1])
                neg_bits = bv0.negate_bits(bv1)
                if (neg_bits == None or len(neg_bits) != 1):
                    print "negate wrong", str(bv0), str(bv1), "->", str(bv)
                    return False
                if (not bv.contain(bv0)):
                    print "not contain", str(bv0), str(bv)
                    return False
                if (not bv.contain(bv1)):
                    print "not contain", str(bv1), str(bv)
                    return False
            ## disjoint among atomic term
            else: 
                for term2 in py.terms:
                    if (term2.subs == None) and (term2 != term):
                        bv2 = py.repr(term2)
                        if (bv.overlap(bv2)):
                            print "overlap", str(term), bv, "<->", str(term2), bv2
                            return False
    return True
                            

def final_merge(pyramids):
    ## starts here
    root_bv = BitValue(Pyramid.nbits, None)
    term2bv = dict()
    terms = []
    final_pyramid = Pyramid(Pyramid.nbits,
                            terms,
                            set(),
                            root_bv,
                            term2bv)
    spare_bvs = [(-root_bv.level(), root_bv)]
    for py in sorted(pyramids, cmp = lambda x,y: (y.level - x.level)):
        l, sbv = heapq.heappop(spare_bvs)
        l = -l
        if (py.level > l):
            return None
        terms.extend(py.terms)
        term2bv.update(py.term2bv)
        for i in range(0, Pyramid.nbits):
            if (sbv.refs[i] != None):
                py.root.super_ref_other(term2bv, i, sbv)

        final_pyramid.bv_repr(sbv)
        final_pyramid.bv_repr(py.root)
        new_sbvs = sbv.difference(py.root)
        for new_sbv in new_sbvs:
            heapq.heappush(spare_bvs, (-new_sbv.level(), new_sbv))
        for new_sbv in py.spare_nodes:
            heapq.heappush(spare_bvs, (-new_sbv.level(), new_sbv))

    for (_, bv) in spare_bvs:
        final_pyramid.spare_nodes.add(bv)

    return final_pyramid

## merge pyramids given the term
def merge_pyramids(pyramids, term, visited_terms):

    def search_pyramid(t):
        for pyramid in pyramids:
            if (t in pyramid.terms):
                return pyramid
        return None

    ## starts here
    if (term.subs == None) or (term in visited_terms):
        return True

    if ((not merge_pyramids(pyramids, term.subs[0], visited_terms)) or
        (not merge_pyramids(pyramids, term.subs[1], visited_terms))):
        return False

    res, usedup_level = check_valid(pyramids)
    if (not res):
#        print "STOPPED!"
        return False

    py1 = search_pyramid(term.subs[0])
    py2 = search_pyramid(term.subs[1])


#    print ">> py1",
#    py1.show()
#    print ">> py2",
#    py2.show()

#    print "\n>>  merge by", str(term)
#    print py1.id, py2.id

    py_star = py1.merge(py2,
                        term.subs[0], 
                        term.subs[1],
                        term,
                        usedup_level)

    if (py_star == None):
#        print "-> None"
        return False
    else:
        py_star.repr_all()

        if (py1 in pyramids):
            pyramids.remove(py1)
        if (py2 in pyramids):
            pyramids.remove(py2)
        if (py_star not in pyramids):
            pyramids.add(py_star)
        visited_terms.add(term.subs[0])
        visited_terms.add(term.subs[1])
        visited_terms.add(term)

#        print "->", py_star.id
#        py_star.show()

        return True


def construct_pyramids(leveled_terms, nbits):
    
    ## mark the term and its subtree as visited
    def mark_visited(term):
        if (term in visited_terms):
            return
        visited_terms.add(term)
        if (term.subs != None):
            mark_visited(term.subs[0])
            mark_visited(term.subs[1])
    
    def recalc_weight(term):
        if (term in visited_terms):
            term.weight = 0
            return 0
        if (term.subs != None):
            recalc_weight(term.subs[0])
            recalc_weight(term.subs[1])
            term.weight = (term.subs[0].weight + 
                           term.subs[1].weight + 1)

    ## starts here
    pyramids = set()
    connections = []

    for level, terms in leveled_terms.items():
        for term in terms:
            if (term.subs == None):
                pyramids.add(Pyramid.one_term_pyramid(term))
            else:
                connections.append(Conn(term))

    print "all", len(pyramids) + len(connections)
    visited_terms = set()
    heapq.heapify(connections)
    while len(connections) > 0:
        conn = heapq.heappop(connections)
        if (conn.term in visited_terms):
            continue
        old_w = conn.term.weight
        recalc_weight(conn.term)
        if (old_w > conn.term.weight):
            heapq.heappush(connections, conn)
            continue
#        print "connection", conn.term

        temp_pyramids = {p.copy() for p in pyramids}
        temp_visited_terms = copy.copy(visited_terms)
        if (merge_pyramids(temp_pyramids, conn.term, temp_visited_terms)):
            res, _ = check_valid(temp_pyramids)
            if (res):
                pyramids = temp_pyramids
                visited_terms = temp_visited_terms

    for py in pyramids:
        ## single term pyramid
        if (len(py.terms) == 1):
            visited_terms.add(py.terms[0])

    print "visited", len(visited_terms)
#    print "\n".join(str(t) for t in visited_terms)
    print correct(pyramids)

    final_pyramid = final_merge(pyramids)
    if (final_pyramid == None):
        print "WRONG"
    else:
        print "FINAL"
#        final_pyramid.show()
        print correct([final_pyramid])

def check_valid(pyramids):
    spare_counts = {k : 0 for k in range(Pyramid.nbits)}
    spare_counts[Pyramid.nbits] = 1
    usedup_level = -1
    level = Pyramid.nbits
    for py in sorted(pyramids, cmp = lambda x,y: (y.level - x.level)):
        x = spare_counts[py.level]
        if (py.level < level):
            for i in range(py.level + 1, level + 1):
                x = x + (spare_counts[i] << (i - py.level))
                del spare_counts[i]
            level = py.level
        if (x < 1):
            return False, None
        spare_counts[level] = x - 1

        if (x == 0):
            usedup_level = max(usedup_level, level)

        for bv in py.spare_nodes:
            bv_level = bv.level()
            spare_counts[bv_level] = spare_counts[bv_level] + 1
    return True, usedup_level

## find the term blocks
def construct_term_blocks(leveled_terms):

    def weight_the_term(term):
        return (-term.weight, term)

    ## check whether the term and its subtree 
    ## are visited before or not
    def is_indep(term):
        if (term in visited_terms):
            return False
        if (term.subs != None):
            return is_indep(term.subs[0]) and is_indep(term.subs[1])
        return True

    ## mark the term and its subtree as visited
    def mark_visited(term):
        if (term in visited_terms):
            return
        visited_terms.add(term)
        if (term.subs != None):
            mark_visited(term.subs[0])
            mark_visited(term.subs[1])

    def get_subtree(term):
        ret = {term}
        if (term.subs != None):
            ret.update(get_subtree(term.subs[0]))
            ret.update(get_subtree(term.subs[1]))
        return ret

    ## work starts here
    visited_terms = set()
    blocks = []
    for level in sorted(leveled_terms.keys(), reverse = True):
        terms = leveled_terms[level]
        indep_terms = map(weight_the_term, terms)
        heapq.heapify(indep_terms)

        while len(indep_terms) > 0:
            _, best_term = heapq.heappop(indep_terms)
            if (not is_indep(best_term)):
                continue

            mark_visited(best_term)
            one_block = [(best_term, None)]
            blocks.append(one_block)

            continue

            ## expand
            expanded_terms = [(-best_term.weight,
                                best_term,
                                None,
                                None)]
            expanded_term_set = {best_term}
            while len(expanded_terms) > 0:
                _, cur_term, last_term, sub_index = heapq.heappop(expanded_terms)
                if (cur_term.subs == None):
                    continue

                if (sub_index != None):
                    if (not is_indep(cur_term.subs[sub_index])):
                        continue
                    mark_visited(cur_term)
                    one_block.append((cur_term, last_term))

                for k1 in range(2):
                    sub_term = cur_term.subs[k1]
                    for e, new_term in sub_term.edges.items():
                        if ((new_term in visited_terms) or
                            (new_term in expanded_term_set)):
                            continue
                        for k2 in range(2):
                            if (new_term.subs[k2] != sub_term):
                                if (is_indep(new_term.subs[k2])):
                                    heapq.heappush(expanded_terms,
                                                   (-new_term.weight,
                                                     new_term,
                                                     cur_term,
                                                     k2))
                                    expanded_term_set.add(new_term)
                
    return blocks

def wildcard(policyAll):
    leveled_terms = get_leveled_terms(policyAll)

    max_rules = 0
    min_rules = 0
    for level, terms in leveled_terms.items():
        for term in terms:
            for i in range(policyAll.n):
                if (i not in term.edges) and (term.dims[i] != '*'):
                    min_rules = min_rules + 1
            if (term.weight == 1):
                max_rules = max_rules + 1

    max_rules = max_rules * policyAll.n
    print "max_rules:", max_rules
    print "min_rules", min_rules
    print "best_reduction:", max_rules - min_rules

    nbits = 5
    construct_pyramids(leveled_terms, nbits)

#    print "After edges..."
#    for level, terms in leveled_terms.items():
#        print "level ", level
#        print "\n".join(str(t) for t in terms)
#    print ".............."

#    blocks = construct_term_blocks(leveled_terms)
#    shown_terms = set()
#    def show(term):
#        if term in shown_terms:
#            return
#        print str(term)
#        shown_terms.add(term)
#        if (term.subs != None):
#            show(term.subs[0])
#            show(term.subs[1])

#    greedy_red = sum(map(lambda(x): sum(map(lambda(y):y[0].weight, x),), blocks))
#    print "total blocks:", len(blocks), "greedy_red:", greedy_red
#    print max_rules - greedy_red
#    for block in blocks:
#        print "-------------"
#        for cur_term, last_term in block:
#            if last_term == None:
#                print "start",
#            else:
#                print "expand from", last_term.id,
#            show(cur_term)
#        print ">>>>>>>>>>>>"
#        print "-------------"

    
input = sys.argv[1]
p = readin_policies(input)
Pyramid.nbits = int(sys.argv[2])

option = "nanxi" # "ori"
#option = "ori"
if option == "nanxi":
    wildcard(p)
elif option == "ori":
    num_rules, nrules = ipam(p)
    #print "heuristics:", num_rules, " =", nrules
    print "heuristics:", sum(nrules)
#print "best:",
#for i in range(0, p.n):
#    q = p.project(i)
#    print ipam(q),
#print ""

