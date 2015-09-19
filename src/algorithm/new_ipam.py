import sys
import copy
import heapq
from ipam_ds import *

## this is the ipam for prefix-based solution
def new_prefix(policies, patterns):

    ## append value to d[key]
    def add_to_dict(d, key, value):
        if (key in d):
            d[key].add(value)
        else:
            d[key] = {value}


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
    terms = set()
    repr_cnt = dict()
    for p in patterns:
        repr_cnt[p] = 0
    leveled_terms = {}
    print sum(counts.values())

    for keys, c in counts.items():
        x = 1
        l = 0
        dims = keys.split(' ')
        pattern_keys = set()
        for p in patterns:
            if (p.contain(dims)):
                pattern_keys.add(p)
        while (c >= x):
            if (c & x) > 0:
                term = Term(l, keys.split(' '), 0, 0, None, set(pattern_keys))
                terms.add(term)
                add_to_dict(leveled_terms, term.level, term)
                for p in pattern_keys:
                    repr_cnt[p] = repr_cnt[p] + 1
            l = l + 1
            x = x << 1
    while (len(terms) > 1):
        min_level = Pyramid.nbits + 1
        for term in terms:
            min_level = min(min_level, term.level)

        best_repr = -1
        best_t1 = None
        best_t2 = None
        for term1 in terms:
            if (min_level != term1.level):
                continue
            for term2 in terms:
                if (term1 == term2) or (term1.level != term2.level):
                    continue
                repr_total = 0
                for p in term1.pattern_keys:
                    if (p in term2.pattern_keys):
                        repr_total = repr_total + repr_cnt[p]
#                        repr_total = repr_total + 1
                if (repr_total > best_repr):
                    best_repr = repr_total
                    best_t1 = term1
                    best_t2 = term2

#        print min_level, best_repr
        if (best_repr < 0):
            for term1 in terms:
                if (min_level == term1.level):
                    best_t1 = term1
            best_t2 = Term(best_t1.level, [WC] * len(best_t1.dims), 0, 0, None, {})
            add_to_dict(leveled_terms, best_t2.level, best_t2)
            terms.add(best_t2)
            continue

        terms.remove(best_t1)
        terms.remove(best_t2)
        d3 = mask(best_t1.dims, best_t2.dims)
        pattern_keys= set()
        for p in best_t1.pattern_keys:
            if (p in best_t2.pattern_keys):
                pattern_keys.add(p)
        term3 = Term(best_t1.level + 1, d3, 0, 0, [best_t1, best_t2], pattern_keys)
        terms.add(term3)
#        print str(best_t1)
#        print str(best_t2)
#        print str(term3)
#        print ""
        add_to_dict(leveled_terms, term3.level, term3)

        for p in pattern_keys:
                repr_cnt[p] = repr_cnt[p] - 1
                best_t1.edges[p] = term3
                best_t2.edges[p] = term3

    print Term.id, len(terms)

    grouped_pattern_idx = [8, 24, 31, 37, 39, 42]
    curterm = 0
    idx = 0
    pfx_rules = 0
    for p in patterns:
        print "pfx_term", repr_cnt[p]
        curterm = curterm + repr_cnt[p]
        pfx_rules = pfx_rules + repr_cnt[p] * p.weight
        idx = idx + 1
        if (idx in grouped_pattern_idx):
            print "pfx_sum_term", curterm
            curterm = 0
    print "pfx_rule", pfx_rules
    print ""

    return leveled_terms



def new_wildcard(policies, patterns):
    leveled_terms = new_prefix(policies, patterns)

    final_pyramid = new_construct_pyramids(leveled_terms, patterns)

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
    grouped_pattern_idx = [8, 24, 31, 37, 39, 42]


    ##
    if (final_pyramid != None):
#        for term in final_pyramid.terms:
#            print str(term)
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
            print "wc_term", cterm
            curterm = curterm + cterm
            idx = idx + 1
            if (idx in grouped_pattern_idx):
                print "wc_sum_term", curterm
                curterm = 0
            ## 
        print ""

    print "wc_rules", use_rules
    print ""




## construct pyramids from terms
def new_construct_pyramids(leveled_terms, patterns):
    
    ## mark the term and its subtree as visited
    def mark_visited(term):
        if (term in visited_terms):
            return
        visited_terms.add(term)
        if (term.subs != None):
            mark_visited(term.subs[0])
            mark_visited(term.subs[1])
    
    ## try merging, if failed at any point, then revert
    def try_merge(conn, pyramids, visited_terms, repr_cnt):
        temp_pyramids = {p.copy() for p in pyramids}
        temp_visited_terms = copy.copy(visited_terms)
        if (merge_pyramids(temp_pyramids, conn.term, temp_visited_terms)):
            res, _ = check_valid(temp_pyramids)
            if (res):
                for p in conn.term.pattern_keys:
                    repr_cnt[p] = repr_cnt[p] - 1
                return temp_pyramids, temp_visited_terms
            else:
                print "failed", str(conn.term)
                return None
        else:
            return None

    ## find the patterns that two terms share
    def eq_patterns(term1, term2):
        ps = set()
        for p in term1.pattern_keys:
            if ((p in term2.pattern_keys) and
                (p not in term1.edges) and 
                (p not in term2.edges)):
                ps.add(p)
        return ps

    ## sum up the weights of patterns
    def sum_ps_weight(ps, repr_cnt):
        return len(ps)
#        return sum(map(lambda(x):repr_cnt[x], ps))
#        if (len(ps) == 0):
#            return 0
#        else:
#            return sum(map(lambda(x):x.weight, ps))

    ## aggregate two terms into a term with their
    ## common dimension values
    def mask_term(term1, term2, ps):
        dims = copy.copy(term1.dims)
        for i in range(len(term1.dims)):
            if (term1.dims[i] == term2.dims[i]):
                dims[i] = term1.dims[i]
            else:
                dims[i] = WC
 
        return Term(term1.level + 1,
                    dims,
                    0,
                    0,
                    (term1, term2),
                    copy.copy(ps))



    ## starts here
    pyramids = set()
    connections = []

    repr_cnt = dict()
    for p in patterns:
        repr_cnt[p] = 0

    ## each atomic term is a pyramid
    for level, terms in leveled_terms.items():
        for term in terms:
#            print str(term)
            if (term.subs == None):
                py = Pyramid.one_term_pyramid(term)
                pyramids.add(py)
                for p in term.pattern_keys:
                    repr_cnt[p] = repr_cnt[p] + 1
            else:
                connections.append(Conn(term))

    print "all", len(pyramids),  len(connections)

    ## use non-atomic term (i.e., connection) to merge pyramids
    visited_terms = set()
    heapq.heapify(connections)
    while len(connections) > 0:
        ## check the weight
        conn = heapq.heappop(connections)
#        print "\nconnection", str(conn.term),
        res = try_merge(conn, pyramids, visited_terms, repr_cnt)
        if (res != None):
            pyramids, visited_terms = res
 
    
    wc_terms = dict()
    for level, terms in sorted(leveled_terms.items()):
#    for level, terms in leveled_terms.items():
        for term in terms:
            if (term.subs == None):
#                print str(term)
                wc_terms[term] = {term}
                continue
#            print "nc", str(term)

            lterms = wc_terms[term.subs[0]]
            rterms = wc_terms[term.subs[1]]
            tterms = lterms.union(rterms)
            tterms.add(term)
            wc_terms[term] = tterms
            matches = []
            for lterm in lterms:
                if (lterm == term.subs[0]):
                    continue
                for rterm in rterms:
                    if (rterm == term.subs[1]):
                        continue
                    ps_lr = eq_patterns(lterm, rterm)
                    ## heapq is min heap
                    heapq.heappush(matches,
                                   (-sum_ps_weight(ps_lr, repr_cnt), lterm, rterm, ps_lr))
                
            while (len(matches) > 0):
                tp, term_i, term_j,  best_ps = heapq.heappop(matches)
                ## check the weight changes
                prev_weight = sum_ps_weight(best_ps, repr_cnt)
                if (prev_weight == 0):
                    continue
                best_ps.difference_update(set(term_i.edges))
                best_ps.difference_update(set(term_j.edges))
                best_weight = sum_ps_weight(best_ps, repr_cnt)

                ## push back the match
                if (best_weight != prev_weight):
                    if (best_weight > 0):
                        heapq.heappush(matches, 
                                       (best_weight,
                                        term_i, 
                                        term_j,
                                        best_ps))
               ## match two terms
                else:
                    term_k = mask_term(term_i, term_j, best_ps)
                    for p in best_ps:
                        term_i.edges[p] = term_k
                        term_j.edges[p] = term_k
                    conn = Conn(term_k)
                    res = try_merge(conn, pyramids, visited_terms, repr_cnt)
                    if (res != None):
#                        print str(term_i)
#                        print str(term_j)
#                        print term_k
                        pyramids, visited_terms = res
                        tterms.add(term_k)
                    else:
                        for p in best_ps:
                            del term_i.edges[p]
                            del term_j.edges[p]
    
    
    ## mark the single atomic pyramid as visited
    for py in pyramids:
        ## single term pyramid
        if (len(py.terms) == 1):
            visited_terms.add(py.terms[0])

    print "visited", len(visited_terms)
#    print "\n".join(str(t) for t in visited_terms)
    print "before final_merge:", correct(pyramids), len(pyramids)

    ## final merge
    final_pyramid = final_merge(pyramids)
    if (final_pyramid == None):
        print "WRONG FINAL"
    else:
        print "after final_merge:", correct([final_pyramid])
#        final_pyramid.show()

    return final_pyramid
