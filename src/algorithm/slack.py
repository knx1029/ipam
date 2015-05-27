import sys
import math
import heapq
import ipam
from ipam_ds import *

eps = 1e-6

def slack(policies, debug = False):
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
        def nochange(xx):
            t1 = 1
            while (xx > 0) and ((xx & 1) == 0):
                t1 = (t1 << 1)
                xx = (xx >> 1)
            return t1
        y = 0
        while (y < z):
            t = nochange(x)
            y = y + t
            x = x + t
        return y

    ## starts here
    nbit = power_of_two(policies.m)

    ## stores the slack each attribute can accommodate
    slack_size = dict()
    left_slack = (1 << (nbit + 1)) - policies.m
    ## create a fake index to fulfill the slack
    max_v = 0
    for i in range(policies.n):
        ith_policy = policies.project(i)
        ith_counts = ith_policy.count_values()
        for v, c in ith_counts.items():
            y = power_of_two(c)
            sz = (1 << y)
            sl = sz - c
            slack_size[(i, v)] = (sl, sz)
            left_slack = left_slack - sl
            if int(v) >= max_v:
                max_v = int(v) + 1
    fake_v = str(max_v)

    ## calculate the slack needed by each group
    ## a group is associated with n attributes
    counts = policies.count_values()
    groups = []
    slack_groups = []
    for v, c in counts.items():
        req_slack = incr(c)
        if (req_slack > 0):
            heapq.heappush(groups, (req_slack, v, c))
        else:
            slack_groups.append((v, c))

    if (debug):
        print "nbits", nbit, policies.m
        print "left_slack", left_slack

    ## distribute slack to individual groups
    slack_values = []
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
                    success = False
                    nc = nochange(sz, req_slack - sl)
                    extra = extra + nc
                    if (debug):
                        print "sz, req_slack, sl, nc", sz, req_slack, sl, nc

        if (not success) and (debug):
            print "extra", extra, left_slack

        if (not success) and (extra <= left_slack):
            success = True
            left_slack = left_slack - extra
            for di, dv in enumerate(dims):
                if ((di, dv) in slack_size):
                    sl, sz = slack_size[(di, dv)]
                    if (req_slack > sl):
                        nc = nochange(sz, req_slack - sl)
                        slack_size[(di, dv)] = (sl + nc, sz + nc)
                        
        if (success):
            ## deduct slack
            for di, dv in enumerate(dims):
                sl, sz = slack_size[(di, dv)]
                slack_size[(di, dv)] = (sl - req_slack, sz)
            ## add slack (by creating new hosts)
            slack_values.extend([gv] * req_slack)
            new_c = c + req_slack
            new_req_slack = incr(new_c)
            scount = scount + 1
            if (new_req_slack > 0):
                heapq.heappush(groups, (new_req_slack, gv, new_c))
            else:
                slack_groups.append((gv, new_c))
        else:
            slack_groups.append((gv, c))

    if (debug):
        print "scount", scount

    dims = [fake_v] * policies.n
    for ((di, dv), (sl, sz)) in slack_size.items():
        if (sl > 0):
            dims[di] = dv
            gv = " ".join(dims)
            slack_values.extend([gv] * sl)
            dims[di] = fake_v
            slack_groups.append((gv, sl))

    if (debug):
        print "final"
#        print "\n".join("{0} {1}".format(x[0], str(x[1]))
#                        for x in slack_groups)

    slack_values.extend(policies.values)

    slack_policies = Policies(policies.n,
                              len(slack_values),
                              slack_values)

    return slack_policies

def writeout_policies(policies, patterns):
    def rev_strd(s):
        if s == WC:
            return '0'
        return s

    print policies.m, policies.n, len(patterns)
    for i in range(policies.m):
        print policies.values[i]
    for p in patterns:
        l = map(rev_strd, p.dims)
        print " ".join(l), p.weight


def main(input_filename, mode):
    if (mode == 's'):
        input = ipam.readin(input_filename, False)
        policies, patterns = input
        slack_policies = slack(policies)  
        writeout_policies(slack_policies, patterns)
    else:
        inputs = ipam.readin(input_filename, True)
        for policies, patterns, nbits in inputs:
            slack_policies = slack(policies, False)
            print nbits + 1
            writeout_policies(slack_policies, patterns)

main(sys.argv[1], 'm')
