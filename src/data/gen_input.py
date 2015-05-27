import sys
import math
from utils import *

class Input:
    threshold = (1<<32) - 1

    def __init__(self, name, sunit, dunit, entries, len_str):
        if ("ACL" in name):
            name = name.replace("ACL", "")
            self.name = name.replace("", "")
        else:
            self.name = "GaTech"+name.split("/")[-1]
        self.sunit = sunit
        self.dunit = dunit
        self.entries = entries
        self.len_remark = len_str

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

    def show_sizes(self):
        ips = self._get_ips()
        nbits = int(math.ceil(math.log(len(ips))/math.log(2.0) - 1e-9))
        _, _, acount = self.show_unit_size()
        print len(ips), ",", nbits, ",", len(self.sunit), ",", len(self.dunit), ",", acount[0], ",", acount[-1],

    def show_unit_size(self):
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

        def add_one(d, k):
            if (k in d):
                d[k] = d[k] + 1
            else:
                d[k] = 1

        ## starts here
        ips = self._get_ips()
        if len(ips) == 0:
            return
        scount = dict()
        dcount = dict()
        acount = dict()
        for ip in ips:
            best_i = find_best(ip, self.sunit)
            best_j = find_best(ip, self.dunit)
            add_one(scount, best_i)
            add_one(dcount, best_j)
            add_one(acount, (best_i, best_j))

        outputs = sorted(scount.values())
        outputd = sorted(dcount.values())
        outputa = sorted(acount.values())
        return outputs, outputd, outputa


    ## show the disjoint input
    def show_disjoint(self, fout):
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
        ips = self._get_ips()
        if len(ips) == 0:
            return
        print len(ips)
        nbits = int(math.ceil(math.log(len(ips))/math.log(2.0) - 1e-9))
        line = str(nbits) + "\n"
        fout.write(line)
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


    ## show the joint input
    def show_joint(self, fout):
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
        ips = self._get_ips()
        if (len(ips) == 0):
            return
        print len(ips)
        nbits = int(math.ceil(math.log(len(ips))/math.log(2.0) - 1e-9))
        line = str(nbits) + "\n"
        fout.write(line)

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
                    values[j] = 2
                else:
                    values[j] = 0
            line = " ".join(str(v) for v in values)
            line = "{0} {1}\n".format(line, w)
            fout.write(line)

        for i in range(len(self.dunit)):
            w = count_weight(self.dunit[i][0], False)
            for j in range(ndims):
                if (j == i + ls):
                    values[j] = 2
                else:
                    values[j] = 0
            line = " ".join(str(v) for v in values)
            line = "{0} {1}\n".format(line, w)
            fout.write(line)



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
    return Input(acl_str, sunit, dunit, entries, len_str)



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
#                break
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


def eval(inputs, ipam_filename):
    print "name, original_rules, bitsegmentation, opt, prefix, wildcard, ips, bits, sunit, dunit, min_group_size, max_group_size"

    fipam = open(ipam_filename, "r")
    for input in inputs:
        ipam_pcount = []
        min_pcount = []
        max_pcount = []
        while (True):
            line = fipam.readline()
            if (line == None) or (len(line) == 0):
                break
            if ("max_rules" in line) and (len(ipam_pcount) > 0):
                break
            if ("min_pattern" in line):
                pc = int(line.split(" ")[1])
                min_pcount.append(pc)
            if ("max_pattern" in line):
                pc = int(line.split(" ")[1])
                max_pcount.append(pc)
            if ("ipam_pattern" in line):
                pc = int(line.split(" ")[1])
                ipam_pcount.append(pc)

        ipam_w = 0
        min_w = 0
        max_w = 0
        for e in input.entries:
            for si in range(len(input.sunit)):
                for di in range(len(input.dunit)):
                    if ((e.sip == input.sunit[si][0]) and 
                        (e.dip == input.dunit[di][0])):
                        ipam_w = ipam_w + ipam_pcount[si] * ipam_pcount[di - len(input.sunit)]
                        min_w = min_w + min_pcount[si] * min_pcount[di - len(input.sunit)]
                        max_w = max_w + max_pcount[si] * max_pcount[di - len(input.sunit)]

        print input.name, ",",
        original = input.len_remark.split(" ")[1]
        print original, ",",
        bitseg = input.len_remark.split(" ") [2].replace("\n", "")
        print bitseg, ",",
        print min_w, ",",
        print max_w, ",",
        print ipam_w, ",",
        input.show_sizes()
        print ""
                        
                
    fipam.close()



input_filename = sys.argv[1]
mode = sys.argv[2]
inputs = readin(input_filename)

if ("s" in mode):
    if (mode == "d"):
        output_filename = input_filename + ".dpu"
    else:
        output_filename = input_filename + ".jpu"
    fout = open(output_filename, "w")
    for input in inputs:
        if (mode == "d"):
            input.show_disjoint(fout)
        else:
            input.show_joint(fout)
    fout.close()
elif ("e" in mode):
    ipam_filename = sys.argv[3]
    eval(inputs, ipam_filename)
elif ("c" in mode):
    def writelists(file, osl):
        fout = open(file, "w")
        x = max(map(lambda(l): len(l), osl))
        for i in range(x):
            for os in osl:
                if (i < len(os)):
                    fout.write("{1},{0},".format(str(i * 1.0 / len(os)),
                                                str(os[i])))
                else:
                    fout.write(",,")
            fout.write("\n")
        fout.close()

    osl =[]
    odl = []
    oal = []
    for input in inputs:
        os, od, oa = input.show_unit_size()
        osl.append(os)
        odl.append(od)
        oal.append(oa)
    writelists(input_filename + ".scount.csv", osl)
    writelists(input_filename + ".dcount.csv", odl)
    writelists(input_filename + ".acount.csv", oal)
    pass
