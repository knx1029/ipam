import sys
from utils import *

class Input:
    threshold = (1<<32) - 1

    def __init__(self, name, sunit, dunit, entries):
        if ("ACL" in name):
            name = name.replace("ACL", "")
            self.name = name.replace("", "")
        else:
            self.name = "GaTech"+name.split("/")[-1]
        self.sunit = sunit
        self.dunit = dunit
        self.entries = entries

    def _get_ips(self):
        def expand(p):
            if (p >= Input.threshold):
                return {p}
            else:
                s1 = expand((p << 1) + 1)
                s2 = expand((p << 1) + 2)
                s1.update(s2)
                return s1

        ips = set()
        for unit in self.sunit:
            for p in unit:
                if (p > 0):
                    ips.update(expand(p))
        for unit in self.dunit:
            for p in unit:
                if (p > 0):
                    ips.update(expand(p))

        return ips


    ## show the disjoint input
    def show_disjoint(self, ext):
        def find_best(ip, units):
            best_i, best_pi = -1, None
            for i in range(len(units)):
                unit = units[i]
                for p in unit:
                    if (ip_contain(p, ip) and 
                        ((best_pi == None) or (p > best_pi))):
                        best_i = i
                        best_pi = p
            return best_i

        def count_weight(p, use_sip):
            w = 0
            for e in self.entries:
                if ((use_sip and e.sip == p) or
                    ((not use_sip) and e.dip == p)):
                    w = w + 1
            return w

        ## starts here
        fout = open(self.name + ext, "w")

        ips = self._get_ips()
        line = "{0} {1} {2}\n".format(str(len(ips)), 
                                    2,
                                    str(len(self.sunit) + len(self.dunit)))
        fout.write(line)

        for ip in ips:
            best_i = find_best(ip, self.sunit)
            best_j = find_best(ip, self.dunit)
            line = "{0} {1}\n".format(str(best_i + 1),
                                      str(best_j + 1))
            fout.write(line)

        for i in range(len(self.sunit)):
            w = count_weight(self.sunit[i][0], True)
            line = "{0} 0 {1}\n".format(str(i + 1), str(w))
            fout.write(line)
        for i in range(len(self.dunit)):
            w = count_weight(self.dunit[i][0], False)
            line = "0 {0} {1}\n".format(str(i + 1), str(w))
            fout.write(line)

        fout.close()

    ## show the joint input
    def show_joint(self, ext):
        def find_all(ip, units):
            iset = set()
            for i in range(len(units)):
                unit = units[i]
                for p in unit:
                    if (ip_contain(p, ip)):
                        iset.add(i)
            return iset

        def count_weight(p, use_sip):
            w = 0
            for e in self.entries:
                if ((use_sip and e.sip == p) or
                    ((not use_sip) and e.dip == p)):
                    w = w + 1
            return w

        ## starts here
        filename = self.name + ext
        fout = open(filename, "w")
        ips = self._get_ips()
        ls = len(self.sunit)
        ndims = len(self.sunit) + len(self.dunit)
        line = "{0} {1} {2}\n".format(str(len(ips)),
                                      str(ndims),
                                      str(ndims))
        fout.write(line)
        values = [0] * ndims
        for ip in ips:
            iset = find_all(ip, self.sunit)
            jset = find_all(ip, self.sunit)
            for i in range(ndims):
                if (((i < ls) and (i in iset))
                    or ((i >= ls) and ((i - ls) in jset))):
                    values[i] = 2
                else:
                    values[i] = 1
            line = " ".join(str(v) for v in values)
            fout.write(line + "\n")

        for i in range(len(self.sunit)):
            w = count_weight(self.sunit[i][0], True)
            for j in range(ndims):
                if (j == i):
                    values[i] = 2
                else:
                    values[i] = 0
            line = " ".join(str(v) for v in values)
            line = "{0} {1}\n".format(line, w)
            fout.write(line)

        for i in range(len(self.dunit)):
            w = count_weight(self.dunit[i][0], False)
            for j in range(ndims):
                if (j == i + ls):
                    values[i] = 2
                else:
                    values[i] = 0
            line = " ".join(str(v) for v in values)
            line = "{0} {1}\n".format(line, w)
            fout.write(line)

        fout.close()



def gen_inputs(acl_str, snum_str, sunit_str, dnum_str, dunit_str, len_str, rules):
    def parse_int_list_list(str):
        strp = str.replace("\n", "")
        strp = str.replace("[[", "")
        strp = strp.replace("]]", "")
        tokens = strp.split('], [')
        lists = []
        for token in tokens:
            one_list = map(int, token.split(', '))
            lists.append(one_list)
        return lists

    snum = int(snum_str.split(' ')[1])
    sunit = parse_int_list_list(sunit_str)

    dnum = int(dnum_str.split(' ')[1])
    dunit = parse_int_list_list(dunit_str)
    if ((len(sunit) != snum) or (len(dunit) != dnum)):
        return None

    entries = map(lambda(x):Entry.parse(x), rules)
#    print "\n".join(e.readable_str() for e in entries)
    return Input(acl_str, sunit, dunit, entries)



def readin(filename):
    fin = open(filename, "r")
    fin.readline()

    acl_str = None
    snum_str = None
    sunit_str = None
    dnum_str = None
    dunit_str = None
    len_str = None
    rules = None
    inputs = []
    while (True):
        line = fin.readline()
        if (line == None) or (len(line) == 0):
            break
        line = line.replace("\n", "")
        if ('>' in line):
            rules.append(line)
        elif ("ACL" in line) or ("GaTech" in line):
            if (snum_str != None):
                input = gen_inputs(acl_str,
                                   snum_str,
                                   sunit_str,
                                   dnum_str,
                                   dunit_str,
                                   len_str,
                                   rules)
                inputs.append(input)
                acl_str = None
                snum_str = None
                sunit_str = None
                dnum_str = None
                dunit_str = None
                len_str = None
                rules = None
                break
            acl_str = line
            snum_str = fin.readline()
            sunit_str = fin.readline()
            dnum_str = fin.readline()
            dunit_str = fin.readline()
            len_str = fin.readline()
            rules = []

    if (snum_str != None):
        input = gen_inputs(acl_str,
                           snum_str,
                           sunit_str,
                           dnum_str,
                           dunit_str,
                           len_str,
                           rules)
        inputs.append(input)
    fin.close()
    return inputs



filename = sys.argv[1]
mode = sys.argv[2]
inputs = readin(filename)
for input in inputs:
    if (mode == "d"):
        input.show_disjoint(".dpu")
    else:
        input.show_joint(".jpu")
