import copy

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


class Term:
    id = 1
    def __init__(self, level, dims, subs = None, weight = 1):
        self.subs = subs
        self.level = level
        self.dims = dims
        self.edges = dict()
        self.id = Term.id
        self.weight = weight
        Term.id = Term.id + 1

    def __hash__(self):
        return self.id

    def __str__(self):
        edge_str = ';'.join("{0}->{1}".format(x, y.id) for (x,y) in self.edges.items())
        sub_str = "None"
        if self.subs:
            sub_str = "({0},{1})".format(self.subs[0].id, self.subs[1].id)
        return "id{0}, L{1}, dims=[{2}], e={3}, subs={4}, w={5}".format(self.id,
                                                                      self.level,
                                                                      ' '.join(self.dims),
                                                                      edge_str,
                                                                      sub_str,
                                                                      self.weight)

class BitValue:

    def __init__(self, nbits, term):
        self.nbits = nbits
        self.term = term
        ## assumint it is a suffix pattern
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


    def set_wildcard(self, kth):
        self.refs[kth] = None
        self.negate[kth] = False

    def set_other(self, kth, other_bv, negate = False):
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
        bv1.set_other(kth, bv2, neg)

class Pyramid:

    nbits = 2
    id = 0

    ## an initial pyramid with one term
    @classmethod
    def one_term_pyramid(cls, term):
        terms = [term]
        bv = BitValue(Pyramid.nbits,
                      term)
        root = bv.copy()
        root.term = None
        term2bv = dict()
        term2bv[term] = bv
        return Pyramid(term.level,
                       terms,
                       set(terms),
                       set(),
                       root,
                       term2bv)

    ## a pyramid with all the information given
    def __init__(self, level, terms, active_nodes, spare_nodes, root, term2bv):
        Pyramid.id = Pyramid.id + 1
        self.id = Pyramid.id
        self.level = level
        self.terms = terms ##unsure
        self.active_nodes = active_nodes ## unsure what to store in this
        self.spare_nodes = spare_nodes
        self.root = root
        self.term2bv = term2bv

    def copy(self):
        level = self.level
        terms = copy.copy(self.terms)
        active_nodes = copy.copy(self.active_nodes)
        spare_nodes = {n.copy() for n in self.spare_nodes}
        root = self.root.copy()
        term2bv = dict()
        for (t, bv) in self.term2bv.items():
            term2bv[t] = bv.copy()
        other_py = Pyramid(level, terms, active_nodes, spare_nodes, root, term2bv)
        return other_py

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
                print str(self._bv_repr(bv))
            print "--------"

    def _bv_repr(self, bits):
        ## shorten the reference chain
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
        return bits

    def repr(self, term):
        return self._bv_repr(self.term2bv[term])


    ## do not consider fill in or sparing or insufficient #bits
    def merge(self, other_py, term1, term2, term_star):
        ## skip fill_in, permutation, checking valid (enough bits)
        ## also skip finding the right bit to wildcard

        ## make sure self.level >= other.level
        if (self.level < other_py.level):
            return other_py.merge(self, term2, term1, term_star)

        ## starts here
        bv1 = self.repr(term1)
        bv2 = other_py.repr(term2)

        ## if internal, then just checking
        if (self == other_py):
            neg_bits  = bv1.negate_bits(bv2)
            if (neg_bits == None) or (len(neg_bits) != 1):
                return None
            bit_to_flip = neg_bits[0]
            bit_value_star = BitValue(Pyramid.nbits,
                                      term_star)
            bit_value_star.set_all(bv2)
            bit_value_star.set_wildcard(bit_to_flip)

            self.terms.append(term_star)
            self.active_nodes.add(term_star)
            self.term2bv[term_star] = bit_value_star
            for i in range(Pyramid.nbits):
                bv2.super_ref_other(self.term2bv,
                                    i,
                                    bv1,
                                    negate = (i == bit_to_flip))
            return self

        ## if not iternal, then assuming adding a new bit at the end
        bit_to_flip = self.level
        if (bit_to_flip >= Pyramid.nbits):
            return None
        if (bv1.conflict(bv2)):
            return None

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
        
#        print str(bit_value_star)

        new_root = self.root.copy()
        new_root.set_wildcard(bit_to_flip)

        new_active_nodes = self.active_nodes.union(other_py.active_nodes)
        new_active_nodes.add(term_star)

        new_spare_nodes = self.spare_nodes.union(other_py.spare_nodes)
        if (self.level > other_py.level):
            spare_bv = other_py.root
            for l in range(other_py.level, self.level):
                spare_bv = spare_bv.copy()
                if (l > 0):
                    spare_bv.set_wildcard(l - 1)
                spare_bv.negate[l] = not(spare_bv.negate[l])
                new_spare_nodes.add(spare_bv)

        new_pyramid = Pyramid(new_level, 
                              new_terms, 
                              new_active_nodes,
                              new_spare_nodes,
                              new_root,
                              new_term2bv)
        return new_pyramid
