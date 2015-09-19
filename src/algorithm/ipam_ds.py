import copy
import heapq

WC = '*'
PFX = False # True

class Pattern:
    id = 1
    ## values at each dimension and the weight
    def __init__(self, dims, weight):
        self.id = Pattern.id
        Pattern.id = Pattern.id + 1
        self.dims = dims
        self.weight = weight

    def __hash__(self):
        return self.id

    def __str__(self):
        return str(self.id)

    def show(self):
        print "(pid{} [{}] : {})".format(self.id, 
                                  ",".join(self.dims),
                                  self.weight)

    def contain(self, other_dims):
        if (len(self.dims) != len(other_dims)):
            return False
        for i in range(len(self.dims)):
            if (self.dims[i] != other_dims[i]) and (self.dims[i] != WC):
                return False
        return True

class Policies:

    ## n is #dimension. m is the #hosts
    def __init__(self, n, m, values, compact):

        def compress(vs):
            counts = dict()
            for v in vs:
                if (v in counts):
                    counts[v] = counts[v] + 1
                else:
                    counts[v] = 1
            return counts


        ## starts here
        self.n = n
        ## counts store #hosts in each distinct combination of values in dims
        if (not compact): 
            self.m = m
            self.counts = compress(values)
        else:
            self.m = sum(values.values())
            if (0 in values):
                self.m = self.m - values[0]
            self.counts = values

    ## get a policy with one dimension (=nth in self)
    def project(self, nth):
        def f(line):
            tokens = line.split(' ')
            return tokens[nth]

        ## starts here
        if (nth >= self.n) or (nth < 0):
            return None
        if (self.n == 1):
            return self

        nth_counts = dict()
        for (key, value) in self.counts.items():
            nth_key = f(key)
            if (nth_key not in nth_counts):
                nth_counts[nth_key] = value
            else:
                nth_counts[nth_key] = nth_counts[nth_key] + value
        return Policies(1, self.m, nth_counts, True)

    def count_values(self):
        return self.counts #values

class Term:
    id = 1

    def __init__(self, level, dims, weight, sum_ps, subs, pattern_keys):
        self.id = Term.id
        Term.id = Term.id + 1
        self.level = level
        self.dims = dims
        ## pattern_keys are the valid key set of the edges
        if (pattern_keys == None):
            self.pattern_keys = set()
        else:
            self.pattern_keys = pattern_keys
        self.edges = dict()
        ## sum_ps is the total weights of patterns matched by this term
        self.sum_ps = sum_ps
        self.weight = weight
        self.subs = subs

    def __hash__(self):
        return self.id

    def __str__(self):
        edge_str = ';'.join("{0}->{1}".format(x, y.id) for (x,y) in self.edges.items())
        pkeys_str = ";".join(str(v.id) for v in self.pattern_keys)
        sub_str = "None"
        if self.subs:
            sub_str = "({0},{1})".format(self.subs[0].id, self.subs[1].id)
        return "id{0}, L{1}, dims=[{2}], e={3}, subs={4}, w={5}, pkeys={6}".format(self.id,
                                                                        self.level,
                                                                        ' '.join(self.dims),
                                                                        edge_str,
                                                                        sub_str,
                                                                        self.weight,
                                                                        pkeys_str)

class BitValue:

    ## n-bit value corresponding to a term
    ## refs[i] = null means the i-th bit is wildcard
    ## if negate[i] = True, then
    ## the i-th bit equals the i-th bit of refs[i]
    ## otherwise they are negation
    def __init__(self, nbits, term):
        self.nbits = nbits
        self.term = term
        ## assumint it is a suffix pattern
        if (term == None):
            self.refs = [None] * nbits
        else:
            self.refs = [None] * term.level + [term] * (nbits - term.level)
        self.negate = [False] * nbits

    def __str__(self):
        def s(o, n):
            if (o == None):
                return '/\\'
            elif (n):
                return "-{0}".format(o.id)
            else:
                return "+{0}".format(o.id)

        return ",".join(s(self.refs[k], self.negate[k])
                        for k in range(self.nbits))
        pass

    def level(self):
        return self.refs.count(None)

    def copy(self):
        bv = copy.copy(self)
        ## need to create new ref and negate lists
        bv.refs = copy.copy(self.refs)
        bv.negate = copy.copy(self.negate)
        return bv

    ## check whether they conflict (* <-> non*)
    def conflict(self, other_bv):
        if (self.nbits != other_bv.nbits):
            return True
        ## assuming bv and other_bv already points to the end
        for i in range(self.nbits):
            ## if one is wildcard, the other is not
            if (((self.refs[i] == None) and (other_bv.refs[i] != None))
                or ((self.refs[i] != None) and (other_bv.refs[i] == None))):
                return True
        return False

    ## check whether they overlap
    def overlap(self, other_bv):
        if (self.nbits != other_bv.nbits):
            return False
        ## assuming bv and other_bv already points to the end
        for i in range(self.nbits):
            ## if one is wildcard, the other is not
            if ((self.refs[i] != None) and (other_bv.refs[i] != None)):
                if ((self.refs[i] != other_bv.refs[i]) or
                    (self.negate[i] != other_bv.negate[i])):
                    return False
        return True

    ## check whether self contains other_bv
    def contain(self, other_bv):
        if (self.nbits != other_bv.nbits):
            return True
        ## assuming bv and other_bv already points to the end
        for i in range(self.nbits):
            if (self.refs[i] == None):
                continue
            if (other_bv.refs[i] == None):
                return False
            if ((self.refs[i] != other_bv.refs[i]) or 
                (self.negate[i] != other_bv.negate[i])):
                return False
        return True


    ## return the bits that two bvs negate
    def negate_bits(self, other_bv):
        if (self.nbits != other_bv.nbits):
            return True
        ## assuming bv and other_bv already points to the end
        neg_bits = []
        for i in range(self.nbits):
            bv1 = self
            neg1 = bv1.negate[i]
            bv2 = other_bv
            neg2 = bv2.negate[i]

            ## if one is wildcard, the other is not
            if (((self.refs[i] == None) and (other_bv.refs[i] != None))
                or ((self.refs[i] != None) and (other_bv.refs[i] == None))):
                return None
            if ((self.refs[i] == other_bv.refs[i]) and 
                (self.negate[i] != other_bv.negate[i])):
                neg_bits.append(i)
        return neg_bits


    ## return the difference self\other_bv
    ## not neccessary that both bv already points to the end
    def difference(self, other_bv, bit_to_flip = -1):
        if (self.nbits != other_bv.nbits):
            return None
        if (not self.contain(other_bv)):
            return None

        bvs = []
        new_sbv = other_bv.copy()
        for i in range(self.nbits):
            if (self.refs[i] == None) and (new_sbv.refs[i] != None):
                if (i == bit_to_flip):
                    continue
                new_sbv.negate[i] = not(new_sbv.negate[i])
                bvs.append(new_sbv)
                new_sbv = new_sbv.copy()
                new_sbv.set_wildcard(i)
        return bvs


    def set_wildcard(self, kth):
        self.refs[kth] = None
        self.negate[kth] = False

    def set_ref(self, kth, other_bv, negate = False):
        if (kth >= self.nbits) or (self.refs[kth] == None):
            return
        if (other_bv == None):
            self.refs[kth] = None
            self.negate[kth] = False
        else:
            self.refs[kth] = other_bv.term
            self.negate[kth] = negate

    def set_all(self, other_bv):
        for i in range(self.nbits):
            self.refs[i] = other_bv.term
            self.negate[i] = False

    ## set the ref[kth] of this value to other_bv's ref[kth]
    def super_ref_other(self, ref2bv, kth, other_bv, negate = False):
        if (kth >= self.nbits) or (self.refs[kth] == None):
            return
        neg = negate
        bv1 = self
        while (bv1.refs[kth] != None) and (bv1.refs[kth] != bv1.term):
            neg = (neg != bv1.negate[kth])
            bv1 = ref2bv[bv1.refs[kth]]
        bv2 = other_bv
        while (bv2 != None) and (bv2.refs[kth] != bv2.term):
            neg = (neg != bv2.negate[kth])
            bv2 = ref2bv[bv2.refs[kth]]
        bv1.set_ref(kth, bv2, neg)


class Pyramid:

    nbits = 2
    id = 0

    ## an initial pyramid with one term
    @classmethod
    def one_term_pyramid(cls, term):
        bv = BitValue(Pyramid.nbits,
                      term)
        root = bv.copy()
        root.term = None
        return Pyramid(term.level,
                       [term],
                       set(),
                       root,
                       {term:bv})

    ## a pyramid with all the information given
    def __init__(self, level, terms, spare_nodes, root, term2bv):
        Pyramid.id = Pyramid.id + 1
        self.id = Pyramid.id
        self.level = level
        self.terms = terms
        self.spare_nodes = spare_nodes
        self.root = root
        self.term2bv = term2bv

    def __hash__(self):
        return self.id

    def copy(self):
        level = self.level
        terms = copy.copy(self.terms)
        spare_nodes = {n.copy() for n in self.spare_nodes}
        root = self.root.copy()
        term2bv = dict()
        for (t, bv) in self.term2bv.items():
            term2bv[t] = bv.copy()
        other_py = Pyramid(level, terms, spare_nodes, root, term2bv)
        other_py.id = self.id
        return other_py

    def repr_all(self):
        for term in self.terms:
            self.repr(term)
        if (len(self.spare_nodes) > 0):
            for bv in self.spare_nodes:
                self.bv_repr(bv)


    def show(self):
        print "id", self.id, "level", self.level, "root", str(self.root)
        print "terms"
        for term in self.terms:
            print str(term)
            bit = self.repr(term)
            print str(bit)
        if (len(self.spare_nodes) > 0):
            print "spare_bvs"
            for bv in self.spare_nodes:
                self.bv_repr(bv)
                print str(bv)
            print "--------"

    ## shorten the reference chain
    def bv_repr(self, bits):
        def dfs(bits, kth):
            if (bits.refs[kth] == None):
                return None
            elif (bits.refs[kth] == bits.term):
                return bits

            other_bv = self.term2bv[bits.refs[kth]]
            new_other_bv = dfs(other_bv, kth)
            bits.negate[kth] = (other_bv.negate[kth] != bits.negate[kth])
            if (new_other_bv == None):
                bits.refs[kth] = None
            else:
                bits.refs[kth] = new_other_bv.term
            return other_bv

        for i in range(Pyramid.nbits):
            dfs(bits, i)

    ## shorten the reference chain for the bitvalue of the given term
    def repr(self, term):
        bv = self.term2bv[term]
        self.bv_repr(bv)
        return bv


    ## merge internally
    def _internal_merge(self, term1, term2, term_star):
#        print "INTERNAL"

        bv1 = self.repr(term1)
        bv2 = self.repr(term2)

        ## check must have exactly 1 bit difference
        ## there is at least 1 bit differ for bv1 and bv2
        neg_bits  = bv1.negate_bits(bv2)
        if (neg_bits == None) or (len(neg_bits) != 1):
            return None

        ## if it is prefix, then only negating at the 
        ## first non-* bit is permitted
        if (PFX):
            pfx_idx = -1
            for pfx_i in range(Pyramid.nbits):
                if (bv1.refs[pfx_i] == None):
                    pfx_idx = pfx_i
                else:
                    break
            if (pfx_idx + 1 != neg_bits[0]):
                return None
        ##

        bit_to_flip = neg_bits[0]
        bit_value_star = BitValue(Pyramid.nbits,
                                  term_star)
        bit_value_star.set_all(bv2)
        bit_value_star.set_wildcard(bit_to_flip)
        
        self.terms.append(term_star)
        self.term2bv[term_star] = bit_value_star
        for i in range(Pyramid.nbits):
            bv2.super_ref_other(self.term2bv,
                                i,
                                bv1,
                                negate = (i == bit_to_flip))
        return self

    ## fill one spare bv for other_py
    def _fillin_merge(self, other_py, term1, term2, term_star, mlevel):
        if (len(self.spare_nodes) == 0):
            return None
#        print "FILL IN"

        max_level = max(map(lambda(x):x.level(), self.spare_nodes))
        if (max_level < other_py.level):
            return None
        
        bv1 = self.repr(term1)
        bv2 = other_py.repr(term2)
        bit_to_flip = -1

        ## if it is prefix, then only negating at the 
        ## first non-* bit is permitted
        pfx_idx = -1
        if (PFX):
            for pfx_i in range(Pyramid.nbits):
                if (bv2.refs[pfx_i] == None):
                    pfx_idx = pfx_i
                else:
                    break
        ##

        ## enumerate the bit_to_flip
        for i in range(self.level):
            ## if it is prefix, then only negating at the 
            ## first non-* bit is permitted
            if (PFX) and (i != pfx_idx + 1):
                continue
            ##

            if (bv1.refs[i] != None):
                ## calculate the bitvalue after flipping
                bv_prime = other_py.root.copy()
                for j in range(Pyramid.nbits):
                    if (bv_prime.refs[j] != None):
                        if (bv_prime.refs[j] != bv2.refs[j]):
                            raise ValueError("{0} <-> {1}".format(
                                    str(bv_prime), str(bv2)))
                        else:
                            bv_prime.set_ref(j, bv1, 
                                             negate = (i == j))
                self.bv_repr(bv_prime)

                ## check whether the bitvalue is contained in a spare bv
                for sbv in self.spare_nodes:
                    if (sbv.level() >= mlevel):
                        continue
                    if (sbv.contain(bv_prime) and
                        (bit_to_flip < 0 or
                         sbv.level() < spare_bv.level())):
#                        print str(sbv), "contains", str(bv_prime)
                        bit_to_flip = i
                        spare_bv = sbv
#                        break

        if (bit_to_flip < 0):
            return None

        ## union terms
        self.terms.extend(other_py.terms)
        self.terms.append(term_star)

        ## update term2bv
        self.term2bv.update(other_py.term2bv)
        for i in range(Pyramid.nbits):
            bv2.super_ref_other(self.term2bv,
                                i,
                                bv1,
                                negate = (i == bit_to_flip))
        bit_value_star = BitValue(Pyramid.nbits,
                                  term_star)
        bit_value_star.set_all(bv1)
        bit_value_star.set_wildcard(bit_to_flip)
        self.term2bv[term_star] = bit_value_star

        ## update spare_nodes
        self.spare_nodes.update(other_py.spare_nodes)
        self.spare_nodes.remove(spare_bv)
        ## add back the leftover
        if (spare_bv.level() > other_py.level):
            self.bv_repr(spare_bv)
            self.bv_repr(other_py.root)
            new_sbvs = spare_bv.difference(other_py.root)
            for new_sbv in new_sbvs:
                self.spare_nodes.add(new_sbv)
        return self


    ## merge two pyramids
    def merge(self, other_py, term1, term2, term_star, mlevel):
        ## skip permutation
        ## also skip finding the right bit to wildcard

        ## make sure self.level >= other.level
        if (self.level < other_py.level):
            return other_py.merge(self, term2, term1, term_star, mlevel)

        ## if internal, then just checking
        if (self == other_py):
            return self._internal_merge(term1, term2, term_star)

        ## check whether their wildcard positions conflict
        bv1 = self.repr(term1)
        bv2 = other_py.repr(term2)
        if (bv1.conflict(bv2)):
            return None

        ## try fill in 
        py_star = self._fillin_merge(other_py, term1, term2, term_star, mlevel)
        if (py_star != None):
            return py_star

        ## assuming adding a new bit at the end
        bit_to_flip = self.level
        if (bit_to_flip >= Pyramid.nbits):
            return None

        ## if it is prefix, then only negating at the 
        ## first non-* bit is permitted
        pfx_idx = -1
        if (PFX):
            for pfx_i in range(Pyramid.nbits):
                if (bv1.refs[pfx_i] == None):
                    pfx_idx = pfx_i
                else:
                    break
            if (pfx_idx + 1 != bit_to_flip):
                return None
        ##


        ## merge
        new_level = max(self.level, other_py.level) + 1
        new_terms = self.terms + other_py.terms
        new_terms.append(term_star)

        new_term2bv = copy.copy(self.term2bv)
        new_term2bv.update(other_py.term2bv)

        bit_value_star = BitValue(Pyramid.nbits,
                                  term_star)
        bit_value_star.set_all(bv2)
        bit_value_star.set_wildcard(bit_to_flip)
        new_term2bv[term_star] = bit_value_star
        for i in range(Pyramid.nbits):
            bv2.super_ref_other(new_term2bv,
                                i,
                                bv1,
                                negate = (i == bit_to_flip))
        
        new_root = self.root.copy()
        new_root.set_wildcard(bit_to_flip)

        new_spare_nodes = self.spare_nodes.union(other_py.spare_nodes)
        ## create the pyramid to call by_repr
        new_pyramid = Pyramid(new_level, 
                              new_terms, 
                              new_spare_nodes,
                              new_root,
                              new_term2bv)

        ## update spare nodes
        if (self.level > other_py.level):
            new_pyramid.bv_repr(new_root)
            new_pyramid.bv_repr(other_py.root)
            spare_bvs = new_root.difference(other_py.root, bit_to_flip)
            for spare_bv in spare_bvs:
                new_spare_nodes.add(spare_bv)


        return new_pyramid


class Conn:

    def __init__(self, term):
        self.term = term

    def __cmp__(self, other_conn):
        if (self.term.weight != other_conn.term.weight):
            return other_conn.term.weight - self.term.weight
        else:
            return self.term.level - other_conn.term.level


### operators on Pyramid

## merge pyramids given the term
def merge_pyramids(pyramids, term, visited_terms):
    ## return the pyramid that contains the given term
    def search_pyramid(t):
        for pyramid in pyramids:
            if (t in pyramid.terms):
                return pyramid
        return None
    ## work starts here
    if (term.subs == None) or (term in visited_terms):
        return True
    ## first merge pyramids for the sub-terms
    if ((not merge_pyramids(pyramids, term.subs[0], visited_terms)) or
        (not merge_pyramids(pyramids, term.subs[1], visited_terms))):
        return False

    ## check valid
    res, usedup_level = check_valid(pyramids)
    if (not res):
        return False

    ## get two pyramids
    py1 = search_pyramid(term.subs[0])
    py2 = search_pyramid(term.subs[1])

#    print ">> py1",
#    py1.show()
#    print ">> py2",
#    py2.show()

#    print "\n>>  merge by", str(term)
#    print py1.id, py2.id,

    ## merge pyramids
    py_star = py1.merge(py2,
                        term.subs[0], 
                        term.subs[1],
                        term,
                        usedup_level)

    if (py_star == None):
#        print "-> None"
        return False
    else:
        ## remove py1, py2 and add py_star
        py_star.repr_all()

#        print "->", py_star.id
#        py_star.show()

        if (py1 in pyramids):
            pyramids.remove(py1)
        if (py2 in pyramids):
            pyramids.remove(py2)
        if (py_star not in pyramids):
            pyramids.add(py_star)
        visited_terms.add(term.subs[0])
        visited_terms.add(term.subs[1])
        visited_terms.add(term)
        return True


## merge all pyramids into a single one
def final_merge(pyramids):
    ## construct the final pyramid
    root_bv = BitValue(Pyramid.nbits, None)
    term2bv = dict()
    terms = []
    final_pyramid = Pyramid(Pyramid.nbits,
                            terms,
                            set(),
                            root_bv,
                            term2bv)
    spare_bvs = [(-root_bv.level(), root_bv)]

    ## merge pyramids in decreasing level
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

## check whether the pyramids are valid
def check_valid(pyramids):
    ## spare_count stores the pyramid_level -> #available pyramids
    ## initially, there is only one pyramid with the max level
    spare_counts = {k : 0 for k in range(Pyramid.nbits)}
    spare_counts[Pyramid.nbits] = 1
    usedup_level = Pyramid.nbits + 1
    level = Pyramid.nbits
    ## browse through all pyramids with descending levels
    for py in sorted(pyramids, cmp = lambda x,y: (y.level - x.level)):
        ## calculate #available pyramids
        x = spare_counts[py.level]
        if (py.level < level):
            for i in range(py.level + 1, level + 1):
                x = x + (spare_counts[i] << (i - py.level))
                del spare_counts[i]
            level = py.level

        if (x < 1):
            return False, None
        spare_counts[level] = x - 1
#        spare_counts[level] = x
        x = x - 1
        if (x == 0) and (usedup_level > Pyramid.nbits):
            usedup_level = level

        for bv in py.spare_nodes:
            bv_level = bv.level()
            spare_counts[bv_level] = spare_counts[bv_level] + 1

    return True, usedup_level


## check the correctness of pyramids
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


def assign_bits(pyramid):
    pyramid.repr_all()

    term2value = dict()
    for term, bv in pyramid.term2bv.items():
        def f(r, n):
            if (r == None):
                return WC
            elif (n):
                return '1'
            else:
                return '0'
        vs = ""
        for kth in range(bv.nbits):
            vs = vs + f(bv.refs[kth], bv.negate[kth])
        term2value[term] = vs
    return term2value


