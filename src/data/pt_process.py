import sys
import math

userclass = "userclass"
status_str = "status"

def readin(file, cleanup = True):
    fin = open(file, 'r')
    hosts = []
    new_host = dict()
    for line in fin:
        if (": " not in line):
            if (len(new_host) > 0):
                if (cleanup):
                    if ("cs_owned" not in new_host):
                        new_host["cs_owned"] = "no"
                    if (userclass not in new_host):
                        new_host[userclass] = "guest"
                    elif (new_host[userclass] == "fac"):
                        new_host[userclass] = "faculty"
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
                cnts[idx] =cnts[idx] + 1
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
        key = ' '.join(str(i) for i in attr_idx)
        if (key in counts):
            counts[key] = counts[key] + 1
        else:
            counts[key] = 1
    return counts


def gen_input(info, hosts, order):
    def num2bits(n):
        return int(math.ceil(math.log(n)/math.log(2.0) - 1e-9))

    nbits = num2bits(len(hosts))
    for l in range(1, len(order) + 1):
#    if (True):
#        l = 1
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
#        print max(counts.values()), min(counts.values())
#        print l, ",", nbits, ",", bs, ",", attrs_counts
#        continue

        print nbits
#        print 16
        print len(counts), l, attrs_counts
        for (key, value) in counts.items():
            print key, value

        attr_idx = [0] * l
        for i in range(l):
            attrs = info[new_order[i]][0]
            for j in range(len(attrs)):
                attr_idx[i] = j + 1
                print " ".join(str(k) for k in attr_idx),
                print 1
            attr_idx[i] = 0
    pass


def eval(ipam_filename, ninputs):
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

file = sys.argv[1]
mode = sys.argv[2]
## g for generate, e for evaluate
order = [userclass, "csnetgroups", status_str, "style", "cs_owned", "room", "os"]
#, "manufacturer"]
order = order[:5]
if ("g" in mode):
    hosts = readin(file)
    info = analyze(hosts)
#    show_info(info)
    gen_input(info, hosts, order)
elif ('e' in mode):
    eval(file, len(order))
