import sys
import math

userclass = "userclass"
status_str = "status"
room_str = "room"
os_str = "os"
group_str = "csnetgroups"
cs_str = "cs_owned"
style_str = "style"

def readin(file, cleanup = True):
    fin = open(file, 'r')
    hosts = []
    new_host = dict()
    for line in fin:
        if (": " not in line):
            if (len(new_host) > 0):
                if (cleanup):
                    if (cs_str not in new_host):
                        new_host[cs_str] = "no"
                    if (userclass not in new_host):
                        new_host[userclass] = "guest"
                    elif (new_host[userclass] == "fac"):
                        new_host[userclass] = "faculty"

                    if (room_str not in new_host):
                        new_host[room_str] = "unknown"
                    elif (new_host[room_str] =="other/unknown"):
                        new_host[room_str] = "unknown"

                    if (os_str in new_host):
#                    if (False):
                        os = new_host[os_str]
                        if ("linux" in os) or ("ubuntu" in os):
                            new_host[os_str] = "linux"
                        elif ("osx" in os) or ("os-x" in os) or ("mac" in os) or ("apple" in os):
                            new_host[os_str] = "mac-os"
                        elif ("windows" in os):
                            new_host[os_str] = "windows"
                        else:
                            new_host[os_str] = "other"
                hosts.append(new_host)
                new_host = dict()
        else:
            tokens = line.split(": ")
            if (len(tokens) < 2):
                print len(line)
                print line
            else:
                key = tokens[0].lower()
                value = tokens[1].lower()
                value = value.replace('\n', '')
                value = value.replace('\r', '')
                ## try to merge
                if (cleanup):
                    if (key == status_str):
                        if (value == "testing" or value == "test"):
                            value = "in testing"
                        elif (value == "in use" or value == "production"):
                            value = "in service"
                        elif (value == "spare"):
                            value = "surplus"

                new_host[key] = value
    fin.close()
    return hosts

def sort_dates(host_set, nblock, block_no_st, block_no_ed):
    def compare(h1, h2):
        return h1[date_str] < h2[date_str]

    date_str = "datecreated"
    
    host_list = list(host_set)
    host_list.sort(cmp = compare)

    block_size = len(host_set) / nblock

    st = block_no_st * block_size
    ed = min(block_no_ed * block_size, len(host_set))
    return host_list[st:ed]

    '''
    keys = [userclass, group_str, os_str,  status_str, cs_str,
            room_str, style_str, "manufacturer", #"datelastchanged", 
            "datecreated"]

    if True:
        st = block_no_st * block_size
        ed = min(block_no_ed * block_size, len(host_set))
        for i in range(st, ed):
            host = host_list[i]
            for key in keys:
                if (key not in host):
                    host[key] = "EMPTY"
                print "{0}: {1}".format(key, host[key])
            print ""
        print "---------------------"
    '''

def analyze(hosts):
    info = dict()
    for host in hosts:
        for dim, attr in host.items():
            if ('date' in dim):
                continue
            if (dim not in info):
                info[dim] = ([], [])

    empty_attr = "EMPTY"
    for dim, (attrs, cnts) in info.items():
        for host in hosts:
            if (dim not in host):
                host[dim] = empty_attr
            attr = host[dim]
            if (attr not in attrs):
                attrs.append(attr)
                cnts.append(1)
            else:
                idx = attrs.index(attr)
                cnts[idx] = cnts[idx] + 1
    return info

def show_info(info):
    for dim, (cnts, attrs) in info.items():
        print dim ,"(", len(attrs), ") :"
        for i in range(len(cnts)):
            print attrs[i], cnts[i]
        print ""

    return info


def count_hosts(info, hosts, dims):
    attr_idx = [0] * len(dims)
    counts = dict()
    for host in hosts:
        for idx, dim in enumerate(dims):
            attr = host[dim]
            attrs = info[dim][0]
            attr_idx[idx] = attrs.index(attr) + 1
            ## print by string or number
#            attr_idx[idx] = attr
        key = ' '.join(str(i) for i in attr_idx)
#        key = ';'.join(str(i) for i in attr_idx)
        if (key in counts):
            counts[key] = counts[key] + 1
        else:
            counts[key] = 1
    return counts


def gen_input(info, hosts, order, start = 1, scales = [1], add_on = 0):
    def num2bits(n):
        return int(math.ceil(math.log(n)/math.log(2.0) - 1e-9))

    for scale in scales:
        nbits = num2bits(len(hosts) * scale)
        for l in range(start, len(order) + 1):
            attr_value = [None] * l
            attr_idx = [-1] * l
            new_order = order[: l]
            attrs_counts = sum(map(lambda(x): len(info[x][0]), new_order))
            counts = count_hosts(info, hosts, new_order)

            bs = num2bits(max(counts.values()))
            for i in range(l):
                attrs = info[new_order[i]][0]
                nunits = num2bits(len(attrs))
                bs = bs + nunits
#            print max(counts.values()), min(counts.values())
#            print l, ",", nbits, ",", bs, ",", attrs_counts
#            continue

            print nbits
#           print 16
            print len(counts), l, attrs_counts
            for (key, value) in counts.items():
                print key, max(int(math.ceil(1.0 * value * scale)), value + add_on)
#                print key, int(math.ceil(1.0 * value * scale))

            attr_idx = [0] * l
            for i in range(l):
                attrs = info[new_order[i]][0]
                for j in range(len(attrs)):
                    attr_idx[i] = j + 1
                    ## print by string or number
#                    attr_idx[i] = "{0}.{1}".format(str(j + 1), attrs[j])
                    print " ".join(str(k) for k in attr_idx),
                    print 1
                attr_idx[i] = 0


def eval(ipam_filename, info, order, ninputs):
    fipam = open(ipam_filename, "r")
    print "index, opt, prefix, wildcard"
    for i in range(ninputs):
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

        print i, ",", sum(min_pcount), ",", sum(max_pcount), ",", sum(ipam_pcount)
        last = 0
        for dim in order:
            attrs, counts = info[dim]
            ndim = len(attrs)
            print dim, ",", sum(min_pcount[last:last+ndim]), 
            print ",", sum(max_pcount[last:last+ndim]), 
            print ",", sum(ipam_pcount[last:last+ndim]),
            print ",", len(hosts)
            last = last + ndim


def vlan_rt(hosts):
    def vlan_no(host):
        u = host[userclass]
        if ("fac" in u):
            return 0
        elif ("grad" in u) :
            return 1
        elif ("research" in u):
            return 4
        elif ("staff" in u):
            return 2
        else:
            return 3

    def add_one(dd, key):
        if (key not in dd):
            dd[key] = 1
        else:
            dd[key] = dd[key] + 1

    stretch_counts = dict()
    pair_counts = dict()
    for i1 in range(len(hosts)):
        for i2 in range(i1 + 1, len(hosts)):
            host1 = hosts[i1]
            host2 = hosts[i2]
            v1 = vlan_no(host1)
            v2 = vlan_no(host2)
            r1 = host1[room_str]
            r2 = host2[room_str]
            if (v1 != v2) and (r1 == r2):
                if (v1 < v2):
                    add_one(stretch_counts, (v1, v2))
                else:
                    add_one(stretch_counts, (v2, v1))
            if (v1 < v2):
                add_one(pair_counts, (v1, v2))
            else:
                add_one(pair_counts, (v2, v1))

    for  vp, pc in pair_counts.items():
        sc = 0
        if (vp in stretch_counts):
            sc = stretch_counts[vp]
            print vp, " : ", sc, "/", pc


def left_over(file1, file2):
    def readin(file):
        fin = open(file, 'r')
        hosts = []
        new_host = dict()
        line = fin.readline()
        line = fin.readline()
        tokens = line.split(' ')
        m = int(tokens[0])
        amount = dict()
        for i in range(m):
            line = fin.readline()
            tokens = line.split(' ')
            key = ' '.join(tokens[:len(tokens) - 1])
            value = int(tokens[-1])
            amount[key] = value
        fin.close()
        return amount

    ## work starts here
    a1 = readin(file1)
    a2 = readin(file2)
    lefts = dict()
    for key, value in a1.items():
        if (key not in a2):
            l = value
        else:
            l = a1[key] - a2[key]

        tokens = key.split(' ')
        tmp = tokens[1]
        tokens[1] = "17"
        ghost_key = ' '.join(tokens)

        if (l > 0):
            if (ghost_key in a2):
                g = a2[ghost_key]
                if (g > l):
                    a2[ghost_key] = g - l
                    l = 0
                    print ghost_key, ":", tmp, g - l
                else:
                    a2[ghost_key] = 0
                    l = l - g
                    print ghost_key, ":", tmp, l - g

        if (l > 0):
#            if (ghost_key in lefts):
#                lefts[ghost_key] = lefts[ghost_key] + l
#            else:
#                lefts[ghost_key] = l
            lefts[key] = l

#    print sum(a1.values())
#    print sum(a2.values())
#    print "----"
    print sum(lefts.values())
    print len(lefts)

    for key, value in a2.items():
        if ("17" in key):
            print key, value
#    for key, value in lefts.items():
#        print key, value
    return lefts


file = sys.argv[1]
mode = sys.argv[2]
## g for generate, e for evaluate
#order = [userclass, group_str, os_str,  status_str, cs_str, room_str, style_str, "manufacturer"]
#order = [userclass, group_str, os_str, status_str, cs_str, room_str, style_str]
#order = [userclass, group_str, os_str, status_str, cs_str, style_str]
order = [userclass, group_str, room_str, status_str]
#order = [userclass, group_str, room_str, status_str, cs_str, style_str]
#order = order[:6]
#order = [userclass, group_str, room_str]
#status_str, 

if ("g" in mode):
    hosts = readin(file)
    orders = [[userclass, group_str, room_str],
              [userclass, group_str, os_str],
              [userclass, cs_str, os_str],
              [group_str, status_str, cs_str],
              [room_str, status_str, style_str],
              [room_str, cs_str, os_str],
              [status_str, cs_str, os_str]]
    info = analyze(hosts)
#    for order in orders:
#        gen_input(info, hosts, order, len(order))
#    print len(hosts)
#    show_info(info)
#    gen_input(info, hosts, order)
    gen_input(info, hosts, order, len(order))
#    gen_input(info, hosts, order, len(order), [2, 4, 6, 8, 10])
elif ('e' in mode):
    hosts = readin(file)
    ipamfile = sys.argv[3]
    info = analyze(hosts)
    eval(ipamfile, info, order, 1)
elif ('v' in mode):
    hosts = readin(file)
    vlan_rt(hosts)
## update
elif ('u' in mode):
    hosts = readin(file)
    info = analyze(hosts)
    block_no = 2
    block_hosts = sort_dates(hosts, block_no, 0, block_no - 1)
#        info = analyze(block_hosts)
    gen_input(info, block_hosts, order, len(order), [1], 10)
    block_hosts = sort_dates(hosts, block_no, 0, block_no)
    gen_input(info, block_hosts, order, len(order))

## left over
elif ('l' in mode):
    left_over(file, sys.argv[3])
