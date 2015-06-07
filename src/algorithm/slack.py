import sys
import math
import heapq
import ipam
from ipam_ds import *

eps = 1e-6

def count_bits(x):
    cb = 0
    while (x > 0):
        cb = cb + (x & 1) 
        x = x >> 1
    return cb

## return y, s.t., 2^{y-1} < x <= 2^y
def power_of_two(x):
    return int(math.ceil(math.log(x) / math.log(2) - eps))

## returns min y, s.t., representing x + y as a sum of powers of two
## takes less terms than representing x
def incr(x):
    t1 = 1
    while (x > 0) and ((x & 1) == 0):
        t1 = (t1 << 1)
        x = (x >> 1)
    if (x == 0):
        return 0
    t2 = (t1 << 1)
    x = (x >> 1)
    while (x > 0) and ((x & 1) == 0):
        t2 = (t2 << 1)
        x = (x >> 1)
    if (x == 0):
        return 0
    return (t2 - t1)

## returns min y >= z, s.t., representing x + y as a sum of powers of two
## takes at most the same terms as representing x
def nochange(x, z):
    def min_nochange(xx):
        t1 = 1
        while (xx > 0) and ((xx & 1) == 0):
            t1 = (t1 << 1)
            xx = (xx >> 1)
        return t1
    y = 0
    while (y < z):
        t = min_nochange(x)
        y = y + t
        x = x + t
    return y

## match up the slack of dimensions in the slack_dict
## in each iteration, pick one attribute with non-zero
## slack in each dimension and add the hosts
## if all attributes have zero slack, then use the 
## fake attribute
def match_up(slack_dict, max_slack, fake_v, n, debug = False):
    slack_counts = dict()
    dims = [fake_v] * n
    while (True):
        deduct_slack = max_slack + 1
        for i, ith_slack in slack_dict.items():
            for v, (sl, sz) in ith_slack.items():
                if (sl > 0):
                    dims[i] = v
                    if (sl < deduct_slack):
                        deduct_slack = sl
        if (deduct_slack == max_slack + 1):
            break
        gv = " ".join(dims)
        if (gv not in slack_counts):
            slack_counts[gv] = deduct_slack
        else:
            slack_counts[gv] = slack_counts[gv] + deduct_slack

        for i, ith_slack in slack_dict.items():
            if (dims[i] != fake_v):
                (sl, sz) = ith_slack[dims[i]]
                ith_slack[dims[i]] = (sl - deduct_slack, sz)
                dims[i] = fake_v

    return slack_counts


def addup_values(d, key, value):
    if (key not in d):
        d[key] = value
    else:
        d[key] = d[key] + value

## add values of counts2 to counts1
def update_counts(counts1, counts2):
    for key, value in counts2.items():
        addup_values(counts1, key, value)


## use 1 extra bit to reduce opt_slack
## but does random slack distribution
def min_slack(policies, debug = False):
    ## stores the slack each attribute can accommodate
    slack_size = dict()
    ## create a fake index to fulfill the slack
    ## round each attribute in each dimension to nearest power-of-two
    max_v = 0
    for i in range(policies.n):
        ith_policy = policies.project(i)
        ith_counts = ith_policy.counts
        ith_slack = dict()
        for v, c in ith_counts.items():
            y = power_of_two(c)
            sl = (1 << y) - c
            sz = (1 << y)
            ith_slack[v] = (sl, sz)
            if (debug):
                print "d{0}, a{1}, sl {2}, sz {3}".format(
                    i, v, sl, sz)
            if int(v) >= max_v:
                max_v = int(v) + 1
        slack_size[i] = ith_slack
    fake_v = str(max_v)

    
    nbit = power_of_two(policies.m)
    max_slack = (1 << (nbit + 1)) - policies.m + 1

    ## main work
    slack_counts = match_up(slack_size,
                            max_slack,
                            fake_v,
                            policies.n,
                            debug)

    update_counts(slack_counts, policies.counts)
    slack_policies = Policies(policies.n,
                              len(slack_counts),
                              slack_counts,
                              True)

    return slack_policies



## all_slack, sort the slack needed for individual groups
## to reduce its representation in powers-of-two
## in descending order and reduce the slack from corresponding 
## attributes. use random match_up for the left-over slack
def all_slack(policies, debug = False):

    ## starts here
    nbit = power_of_two(policies.m)

    ## stores the slack each attribute can accommodate
    slack_size = dict()
    left_slack = dict()
    ## create a fake index to fulfill the slack
    max_v = 0
    max_slack = (1 << (nbit + 1)) - policies.m
    ## round each attribute's group size to nearest
    ## power-of-two
    if (debug):
        print "initial slack", max_slack

    for i in range(policies.n):
        ith_policy = policies.project(i)
        ith_counts = ith_policy.counts
        left_slack[i] = max_slack
        for v, c in ith_counts.items():
            y = power_of_two(c)
            sz = (1 << y)
            sl = (1 << y) - c
            slack_size[(i, v)] = (sl, sz)
            left_slack[i] = left_slack[i] - sl
            if int(v) >= max_v:
                max_v = int(v) + 1
    fake_v = str(max_v)

    ## calculate the slack needed by each group
    ## a group is associated with n attributes
    counts = policies.counts
    groups = []
    slack_groups = []
    for v, c in counts.items():
        req_slack = incr(c)
        if (req_slack > 0):
            heapq.heappush(groups, (req_slack, v, c))
        else:
            slack_groups.append((v, c))

    ## distribute slack to individual groups
    slack_counts = dict()
    scount = 0
    while (len(groups) > 0):
        req_slack, gv, c = heapq.heappop(groups)
        dims = gv.split(' ')
        success = True
        extra = 0
        ## check whether slacks are sufficient or not
        for di, dv in enumerate(dims):
            if ((di, dv) in slack_size):
                sl, sz = slack_size[(di, dv)]
                if (req_slack > sl):
                    nc = nochange(sz, req_slack - sl)
                    if (nc > left_slack[di]):
                        success = False

        if (not success):
            slack_groups.append((gv, c))
            continue

        ## deduct slack from attributes
        for di, dv in enumerate(dims):
            sl, sz = slack_size[(di, dv)]
            if (req_slack > sl):
                nc = nochange(sz, req_slack - sl)
                left_slack[di] = left_slack[di] - nc
                slack_size[(di, dv)] = (sl + nc - req_slack, sz + nc)
            else:
                slack_size[(di, dv)] = (sl - req_slack, sz)

        ## add slack (by creating new hosts)
        addup_values(slack_counts, gv, req_slack)
                
        new_c = c + req_slack
        new_req_slack = incr(new_c)
        if (new_req_slack > 0):
            heapq.heappush(groups, (new_req_slack, gv, new_c))
        else:
            ## new_c is power-of-two
            slack_groups.append((gv, new_c))

    ## match up the attributes
    slack_dict = dict()
    for ((di, dv), (sl, sz)) in slack_size.items():
        if (sl > 0):
            if (di not in slack_dict):
                slack_dict[di] = dict()
            slack_dict[di][dv] = (sl, sz)


    matched_counts = match_up(slack_dict, 
                              max_slack,
                              fake_v,
                              policies.n,
                              debug)

    ## mainly for checking purposes
    for (gv, c) in matched_counts.items():
        if (debug):
            print "left", gv, ":", c
        dims = gv.split(' ')
        for di, dv in enumerate(dims):
            if (dv != fake_v):
                sl, sz = slack_size[(di, dv)]
                slack_size[(di, dv)] = (sl - c, sz)
            else:
                left_slack[di] = left_slack[di] - c

    update_counts(slack_counts, matched_counts) 


    if (debug):
        print "final"
        for ((di, dv), (sl, sz)) in slack_size.items():
            if (sl != 0) or ((sz & (sz - 1)) != 0):
                print "non-zero slack_size", di, dv, sl, sz, "!!!!!!"
        for (di, c) in left_slack.items():
            if (c < 0):
                print "negative left_slack", di, c, "!!!!!"


    update_counts(slack_counts, policies.counts)
    slack_policies = Policies(policies.n,
                              len(slack_counts),
                              slack_counts,
                              True)

    return slack_policies



## enum_slack, enumerate powers-of-two for groups to
## use slack of attributes. use match_up for the left-over
def enum_slack(policies, debug = False):

    def extra_slack(dims, req_slack):
        ## deduct slack
        for di, dv in enumerate(dims):
            sl, sz = slack_size[(di, dv)]
            if (req_slack > sl):
                nc = nochange(sz, req_slack - sl)
                left_slack[di] = left_slack[di] - nc
                slack_size[(di, dv)] = (sl + nc - req_slack, sz + nc)
            else:
                slack_size[(di, dv)] = (sl - req_slack, sz)

        ## add slack to the group
        slack_groups[gv] = slack_groups[gv] + req_slack

        ## add slack (by creating new hosts)
        addup_values(slack_counts, gv, req_slack)

    ## try to make the size of each attribute closer, by
    ## doubling the smallest
    def adjust_slack_size(slack_size, ith, ith_counts, left_slack):
        init_size = dict()
        for v, c in ith_counts.items():
            y = power_of_two(c)
            sz = (1 << y)
            sl = (1 << y) - c
            init_size[v] = (sl, sz)
            left_slack[ith] = left_slack[ith] - sl

        while (True):
            best_v = -1
            best_nc = 0
            max_sz = 0
            for v, (sl, sz) in init_size.items():
                if (sz > max_sz):
                    max_sz = sz
                nc = nochange(sz, 1)
                if (nc <= left_slack[ith]):
                    if (best_v < 0) or (nc < best_nc):
                        best_v, best_nc = v, nc
            if (best_v < 0):
                break
#            if (sz == max_sz):
            if (sz <= max_sz / 2):
                break
            best_sl, best_sz = init_size[best_v]
            init_size[best_v] = (best_sl + best_nc, best_sz + best_nc)
            left_slack[ith] = left_slack[ith] - best_nc

        for v, (sl, sz) in init_size.items():
            slack_size[(ith, v)] = (sl, sz)


    def update_slack_size(slack_size, ith, ith_counts, left_slack):
        for v, c in ith_counts.items():
            y = power_of_two(c)
            sz = (1 << y)
            sl = (1 << y) - c
            slack_size[(ith, v)] = (sl, sz)
            left_slack[ith] = left_slack[ith] - sl



    ## starts here
    nbit = power_of_two(policies.m)
#    nbit = 15

    ## stores the slack each attribute can accommodate
    slack_size = dict()
    left_slack = dict()
    ## create a fake index to fulfill the slack
    max_v = 0
    max_slack = (1 << (nbit + 1)) - policies.m
    ## round each attribute's group size to nearest
    ## power-of-two
    if (debug):
        print "initial slack", max_slack

    for i in range(policies.n):
        ith_policy = policies.project(i)
        ith_counts = ith_policy.counts
        left_slack[i] = max_slack
        max_v = max(max_v, max(map(lambda(x): int(x), ith_counts.keys())) + 1)
        ## TRY
        if (False):
            adjust_slack_size(slack_size, i, ith_counts, left_slack)
        else:
            update_slack_size(slack_size, i, ith_counts, left_slack)
    fake_v = str(max_v)
    if (debug):
        print "fake_v", fake_v

    ## calculate the slacked group size
    ## a group is associated with n attributes
    slack_groups = dict()
    for gv, c in policies.counts.items():
        slack_groups[gv] = c

    ## distribute slack to individual groups
    slack_counts = dict()
    ## enumerate the slack in powers-of-two
    for i in range(nbit + 1):
        req_slack = (1 << i)

        ## construct a heap of groups, sorted on 
        ## the reduction of representing the sizes
        ## as sums of powers of two
        heaped_groups = []
        for (gv, c) in slack_groups.items():
            cb1 = count_bits(c)
            cb2 = count_bits(c + req_slack)
            if (cb2 <= cb1):
                heapq.heappush(heaped_groups, (cb2 - cb1, gv))

        ## pop the group, satisfy the need
        while (len(heaped_groups) > 0):
            red, gv = heapq.heappop(heaped_groups)
            dims = gv.split(' ')
            success = True
            extra = 0
            ## check whether slacks are sufficient or not
            for di, dv in enumerate(dims):
                if ((di, dv) in slack_size):
                    sl, sz = slack_size[(di, dv)]
                    if (req_slack > sl):
                        nc = nochange(sz, req_slack - sl)
                        if (nc > left_slack[di]):
                            success = False
                        
            if (not success):
                continue

            if (debug):
                pass
#                print "add", req_slack, "to", gv

            extra_slack(dims, req_slack)
        ## ---- end of the while loop ----- #


    ## match up the attributes
    slack_dict = dict()
    for ((di, dv), (sl, sz)) in slack_size.items():
        if (di not in slack_dict):
            slack_dict[di] = dict()
        if (sl > 0):
            slack_dict[di][dv] = (sl, sz)

    matched_counts = match_up(slack_dict, 
                              req_slack,
                              fake_v,
                              policies.n,
                              debug)

    ## mainly for checking purposes
    for (gv, c) in matched_counts.items():
        if (debug):
            print "left", gv, ":", c
        dims = gv.split(' ')
        for di, dv in enumerate(dims):
            if (dv != fake_v):
                sl, sz = slack_size[(di, dv)]
                slack_size[(di, dv)] = (sl - c, sz)
            else:
                left_slack[di] = left_slack[di] - c

    update_counts(slack_counts, matched_counts)
    ## ----- end of the for loop ----- #

    if (debug):
        print "final"
        for ((di, dv), (sl, sz)) in slack_size.items():
            if (sl != 0) or ((sz & (sz - 1)) != 0):
                print "non-zero slack_size", di, dv, sl, sz, "!!!!!!"
        for (di, c) in left_slack.items():
            if (c < 0):
                print "negative left_slack", di, c, "!!!!!"

    update_counts(slack_counts, policies.counts)
    slack_policies = Policies(policies.n,
                              len(slack_counts),
                              slack_counts,
                              True)

    return slack_policies



def writeout_policies(policies, patterns):
    def rev_strd(s):
        if s == WC:
            return '0'
        return s

    print len(policies.counts), policies.n, len(patterns)
    for key in sorted(policies.counts.keys()):
        print key, policies.counts[key]
#    return
    for p in patterns:
        l = map(rev_strd, p.dims)
        print " ".join(l), p.weight


## {s,m} + {c} + {i, a, e}
def main(input_filename, mode):
    debug = 'd' in mode
    if ('s' in mode):
        input = ipam.readin(input_filename, 'c' in mode, False)
        policies, patterns = input
        if ('i' in mode):
            slack_policies = min_slack(policies, debug)
        elif ('a' in mode):
            slack_policies = all_slack(policies, debug)
        elif ('e' in mode):
            slack_policies = enum_slack(policies, debug)
        if (not debug):
            writeout_policies(slack_policies, patterns)
    elif ('m' in mode):
        inputs = ipam.readin(input_filename, 'c' in mode, True)
        for policies, patterns, nbits in inputs:
#        if (True):
#            policies, patterns, nbits = inputs[1]
            if ('i' in mode):
                slack_policies = min_slack(policies, debug)
            elif ('a' in mode):
                slack_policies = all_slack(policies, debug)
            elif ('e' in mode):
                slack_policies = enum_slack(policies, debug)
            if (not debug):
                print nbits + 1
#                print 16
                writeout_policies(slack_policies, patterns)
            else:
                print ""
#            break

main(sys.argv[1], sys.argv[2])
