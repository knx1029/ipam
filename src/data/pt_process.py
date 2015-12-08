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
    def countones(x):
        c = 0
        while (x):
            if (x & 1):
                c = c + 1
            x = x >> 1
        return c

    def round_pow2(x):
        c = 1
        while (c < x):
            c = c << 1
        return c

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
    ghost_overflow = 0
    ghost_new= 0
    for key, value in a1.items():
        if (key not in a2):
            l = value
        else:
            l = a1[key] - a2[key]

        tokens = key.split(' ')
        tmp = int(tokens[1])
        tokens[1] = "17"
        ghost_key = ' '.join(tokens)

        
        if (l > 0):
            if (ghost_key in a2):
                g = a2[ghost_key]
                if (g > l):
                    a2[ghost_key] = g - l
                    print ghost_key, ":", tmp, g - l, countones(g - l), "gl", g, l
                    if (tmp > 11):
                        ghost_new = ghost_new + 1 #countones(g - l)
                    else:
                        ghost_overflow = ghost_overflow + 1 #countones(g - l)
                    l = 0
                else:
                    a2[ghost_key] = 0
                    print ghost_key, ":", tmp, l - g, countones(l - g), "gl", g, l
                    if (tmp > 11):
                        ghost_new = ghost_new + 1 #countones(l - g)
                    else:
                        ghost_overflow = ghost_overflow + 1 #countones(l - g)
                    l = l - g
        '''
        if (l > 0):
#            r = round_pow2(l)
            r = l
            if (ghost_key in lefts):
                lefts[ghost_key] = lefts[ghost_key] + r
            else:
                lefts[ghost_key] = r
#            lefts[key] = r
        '''
#    print sum(a1.values())
#    print sum(a2.values())
#    print "----"
    print sum(lefts.values())
    print len(lefts)
    print ghost_new , "-----", ghost_overflow

    for key, value in a2.items():
        if ("17" in key):
            print key, value
#    for key, value in lefts.items():
#        print key, value
#        print key, round_pow2(value)
    return lefts


def opt_wildcard(rules):
    def num2bit(n, l):
        s = "*" * l
        for i in range(maxl - l):
            s = str(n & 1) + s
            n = n >> 1
        return s

    def one_bit_diff(s1, s2):
        diff_found = False
        for i, c in enumerate(s1):
            if (s1[i] != s2[i]):
                if (not diff_found):
                    diff_found = True
                else:
                    return False
        return diff_found

    def one_bit_merge(s1, s2):
        s3 = ""
        diff_found = False
        for i, c in enumerate(s1):
            if (s1[i] != s2[i]):
                if (not diff_found):
                    diff_found = True
                    s3 = s3 + "*"
                else:
                    return None
            else:
                s3 = s3 + s1[i]
        if (diff_found):
            return s3
        else:
            return None


    ## work starts here
    maxl = max(map(lambda(x):x[0], rules))
    bitrules = map(lambda(x):(x[0], num2bit(x[1], x[0]), x[2]), rules)

#    print bitrules
    merged = [False] * len(bitrules)
    while (True):
        found = False
        for i in range(len(bitrules)):
            if (merged[i]):
                continue
            brule1 = bitrules[i]
            for j in range(i + 1, len(bitrules)):
                if (merged[j]):
                    continue
                brule2 = bitrules[j]
                if (brule1[0] == brule2[0]) and (brule1[2] == brule2[2]):
                    if (one_bit_diff(brule1[1], brule2[1])):
                        brule3 = (brule1[0] + 1,
                                  one_bit_merge(brule1[1], brule2[1]),
                                  brule1[2])
#                        print brule1, brule2, brule3
                        found = True
                        merged[j] = True
                        bitrules[i] = brule3
                        break
        if (not found):
            break

    bitrule = 0
    for m in merged:
        if (not m):
            bitrule = bitrule + 1
    print bitrule
    return bitrule

def opt_prefix(values, segs):

    def get_rules(i, vi, res_idx, res, reslr, rules):
        if (res_idx == 0):
            if (res[res_idx][i][vi] == 2):
                rules.append((res_idx, i, reslr[res_idx][i]))
            return
        vj, vk = reslr[res_idx][i][vi]
        j = i << 1
        k = j + 1

        get_rules(j, vj, res_idx - 1, res, reslr, rules)
        get_rules(k, vk, res_idx - 1, res, reslr, rules)

        if (vj != vi):
            rules.append((res_idx - 1, j, vj))

        if (vk != vi):
            rules.append((res_idx - 1, k, vk))

    ## work starts here
    lenv = 1
    while (lenv < len(values)):
        lenv = (lenv << 1)
    maxv = max(values) + 1
    lenv = lenv * 2
    last_f = [None] * lenv
    for i in range(lenv):
        last_f[i] = [1] * maxv

    i = 0
    lrf = [0] * lenv
    for k in range(len(segs)):
        for j in range(segs[k][0]):
            for v in range(maxv):
                if (v != values[i]):
                    last_f[j + segs[k][1]][v] = 2
            lrf[j + segs[k][1]] = values[i]
            i = i + 1

    res = []
    res.append(last_f)
    reslr = []
    reslr.append(lrf)

    lenv_ = lenv
    while (lenv_ > 1):
        lenv = lenv_ >> 1
#        print lenv_, len(last_f)
        f = [None] * lenv
        lrf = [None] * lenv
        for i in range(lenv):
            f[i] = [0] * maxv
            lrf[i] = [None] * maxv
            j = (i << 1)
            k = j + 1
            for vi in range(maxv):
                f[i][vi] = last_f[j][vi] + last_f[k][vi] - 1
                lrf[i][vi] = (vi, vi)
                for vj in range(maxv):
                    for vk in range(maxv):
                        if (vj == vi) or (vk == vi):
                            if (last_f[j][vj] + last_f[k][vk] < f[i][vi]):
                                f[i][vi] = last_f[j][vj] + last_f[k][vk]
                                lrf[i][vi] = (vj, vk)
                        else:
                            if (last_f[j][vj] + last_f[k][vk] + 1 < f[i][vi]):
                                f[i][vi] = last_f[j][vj] + last_f[k][vk] +1
                                lrf[i][vi] = (vj, vk)
        lenv_ = lenv
        last_f = f
        res.append(f)
        reslr.append(lrf)

    best_v = 0
    for v in range(maxv):
        if (last_f[0][v] < last_f[0][best_v]):
            best_v = v

    rules = []
    get_rules(0, best_v, len(res) - 1, res, reslr, rules)
    rules.append((len(res) - 1, 0, best_v))

    lenw = opt_wildcard(rules)
    print "wildcard", lenw
    print "prefix", len(rules), last_f[0][best_v]
#    print rules
    return len(rules), lenw

def print_hosts(hosts, info, dims):

    def produce_segs(hosts):
        numbers = []
        last = None
        for h in hosts:
            if (h[userclass] == last):
                count = count + 1
            else:
                if (last != None):
                    numbers.append(count)
                last = h[userclass]
                count = 1
        numbers.append(count)

        start = [-1] * len(numbers)
        cur_idx = 0
        for i in range(len(numbers)):
            best = -1
            for j in range(len(numbers)):
                if (start[j] < 0):
                    if (best < 0 or numbers[j] > numbers[best]):
                            best = j
            best_pow2 = 1
            while (best_pow2 < numbers[best]):
                best_pow2 = best_pow2 << 1
            if (cur_idx % best_pow2 == 0):
                start[best] = cur_idx
            else:
                cur_idx = (cur_idx / best_pow2 + 1) * best_pow2
                start[best] = cur_idx
            cur_idx = cur_idx + best_pow2

        return zip(numbers,start)

    ## work starts here
    sorted_hosts = sorted(hosts, key=(lambda(h):h[userclass]))
    values = [0] * len(hosts)
    total_rules_prefix = 0
    total_rules_wildcard = 0


#    segs = [(294, 512), (298, 0), (167, 1792), (50, 2048),
#            (17, 2112), (188, 1536), (473, 1024), (4, 2144)]
#    print segs
    segs = produce_segs(sorted_hosts)
#    print segs

    for idx, dim in enumerate(dims):
        attrs = info[dim][0]
        for jdx, host in enumerate(sorted_hosts):
            attr = host[dim]
            values[jdx] = attrs.index(attr) + 1
        dim_rules_prefix, dim_rules_wildcard = opt_prefix(values, segs)
        total_rules_prefix = total_rules_prefix + dim_rules_prefix
        total_rules_wildcard = total_rules_wildcard + dim_rules_wildcard
        print idx, ":", total_rules_prefix, total_rules_wildcard
        



file = sys.argv[1]
mode = sys.argv[2]
## g for generate, e for evaluate
#order = [userclass, group_str, os_str,  status_str, cs_str, room_str, style_str, "manufacturer"]
#order = [userclass, group_str, os_str, status_str, cs_str, room_str, style_str]
#order = [userclass, group_str, os_str, status_str, cs_str, style_str]
####order = [userclass, group_str, room_str, status_str]
#order = [userclass, group_str, room_str, status_str, cs_str, style_str]
#order = order[:6]
#order = [userclass, group_str, room_str]
order = [userclass, group_str, status_str, style_str]
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
#    gen_input(info, hosts, order, len(order))
    gen_input(info, hosts, order, len(order), [2, 4, 6, 8, 10])
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
    gen_input(info, block_hosts, order, len(order), [1], 0)
    block_hosts = sort_dates(hosts, block_no, 0, block_no)
    gen_input(info, block_hosts, order, len(order))

## left over
elif ('l' in mode):
    left_over(file, sys.argv[3])
#hosts
elif ('h' in mode):
    hosts = readin(file)
    info = analyze(hosts)
    scales = [1]
    scales = [1, 2, 4, 6, 8, 10]
    last_scale = 0
    scaled_hosts = []
    scales.sort()
    for scale in scales:
        for i in range(last_scale, scale):
            for host in hosts:
                scaled_hosts.append(host)
        print "scale", scale
        print_hosts(scaled_hosts, info, order)
        last_scale = scale
