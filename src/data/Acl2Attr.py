import sys
import operator

class Entry:
    def __init__(self, tokens):
        int_tokens = map(lambda(x): int(x), tokens)
        self.sip = int_tokens[0]
        self.dip = int_tokens[1]
        self.sport = (int_tokens[2], int_tokens[3])
        self.dport = (int_tokens[4], int_tokens[5])
        self.permit = int_tokens[6]
        self.marked = False

    def eq(self, e):
        return (self.sip == e.sip and
                self.dip == e.dip and
                self.sport == e.sport and
                self.dport == e.dport and
                self.permit == e.permit)

    def src_group(self, e):
        return (self.sip != e.sip and
                self.dip == e.dip and
                self.sport == e.sport and
                self.dport == e.dport and
                self.permit == e.permit)

    def dst_group(self, e):
        return (self.sip == e.sip and
                self.dip != e.dip and
                self.sport == e.sport and
                self.dport == e.dport and
                self.permit == e.permit)
        
    def __str__(self):
        if self.permit:
            return "%d:%s -> %d:%s" % (self.sip, 
                                       str(self.sport),
                                       self.dip,
                                       str(self.dport))
        else:
            return "%d:%s \> %d:%s" % (self.sip, 
                                       str(self.sport),
                                       self.dip,
                                       str(self.dport))


class Group:
    def __init__(self, e, l):
        self.entry = e
        self.list = l
        self.marked = False


def ip2str(ip):
    s = ""
    while (ip > 0):
        if (ip % 2 == 0):
            s = "1" + s
        else:
            s = "0" + s
        ip = (ip - 1) / 2
    s = s + "*" * (32 - len(s))
    return s


def agg_groups(groups):
    ip_list = []

    ## aggregate by ips
    optimal = 0
    for gi in groups:
        if (gi.marked):
            continue
        eq_groups = [gi.entry]
        for gj in groups:
            if (gi.list == gj.list):
                eq_groups.append(gj.entry)
                gj.marked = True

        optimal = optimal + 1
#        ip_list.extend(gi.list)
        ip_list.append(gi.list)

        if False:
            print "eq_group %d : ip %d" % (len(eq_groups), len(gi.list))
            print "eq_group:"
            print "\n".join(str(k) for k in eq_groups)
            print "ip:"
            print "\n".join(ip2str(k) for k in gi.list)

    print "optimal = %d" % optimal

    return ip_list


def final_intersect(ip_list):

    def intersect(ip1_list, ip2_list):
        a, b, c = [], [], []
        for ip in ip1_list:
            if ip in ip2_list:
                c.append(ip)
            else:
                a.append(ip)
        for ip in ip2_list:
            if ip not in c:
                b.append(ip)
        return a, b, c

    def insert(lists, list):
        if (len(list) > 0):
            found = False
            for l in lists:
                if l == list:
                    found = True
            if (not found):
                lists.append(list)


    ## work starts here
    prev = ip_list
    next = []
    end = False
    while (not end):
        end = True
        for idx, ip1_list in enumerate(prev):
            for idx2, ip2_list in enumerate(prev):
                if (idx2 > idx):
                    a, b, c = intersect(ip1_list, ip2_list)
                    insert(next, a)
                    insert(next, b)
                    insert(next, c)
                    if (len(c) > 0):
                        end = False
        prev = next
        next = []
    return prev


def count_ip(ip_list):
    ip_count = {}
    for list in ip_list:
        for ip in list:
            if ip in ip_count:
                ip_count[ip] = ip_count[ip] + 1
            else:
                ip_count[ip] = 1
    sorted_ip_count = sorted(ip_count.items(),
                             key = operator.itemgetter(1),
                             reverse = True)

    print "ip_counts:"
    print "\n".join("{} : {}".format(ip2str(k1), k2)
                    for (k1, k2) in sorted_ip_count)


def parse(input, use_sip):
    fin = open(input, "r")
    fin.readline()
    entries = []
    for line in fin:
        tokens = line.rsplit(' ')
        entry = Entry(tokens)
        entries.append(entry)
    fin.close()

    ## group acl rules by fields except sip
    groups = []
    num_rules = 0
    for ei in entries:
        if (ei.marked):
            continue
        ip_count = 1
        ip_list = []
        if (use_sip):
            ip_list.append(ei.sip)
        else:
            ip_list.append(ei.dip)
            
        ei.marked = True

        for ej in entries:
            if (ei.eq(ej)):
                ej.marked = True
            if (use_sip):
                if (ei.src_group(ej)):
                    ip_count = ip_count + 1
                    ej.marked = True
                    ip_list.append(ej.sip)
            else:
                if (ei.dst_group(ej)):
                    ip_count = ip_count + 1
                    ej.marked = True
                    ip_list.append(ej.dip)
                
        if (ip_count > 1):
            ip_list = sorted(set(ip_list))
            groups.append(Group(ei, ip_list))
        num_rules = num_rules + len(ip_list)

    print "#Entries = %d, Unique = %d" % (len(entries), num_rules)
    print "#Groups = %d" % len(groups)

    ip_list = agg_groups(groups)
#    count_ip(ip_list)
    units = final_intersect(ip_list)
    print "units", len(units)
    for unit in units:
        print "sips", len(unit)
        print "\n".join(ip2str(k) for k in unit)
        print "..........."

input = sys.argv[1]
use_sip = (sys.argv[2] == 's')
parse(input, use_sip)
