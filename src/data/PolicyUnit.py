import sys
import operator
import copy

class Entry:
    
    def __init__(self, tokens, is_acl = True, standard = False):
        self.marked = False
        if (is_acl):
            int_tokens = map(lambda(x): int(x), tokens)
            self.sip = int_tokens[0]
            self.dip = int_tokens[1]
            self.sport = (int_tokens[2], int_tokens[3])
            self.dport = (int_tokens[4], int_tokens[5])
            self.proto = 0
            self.permit = int_tokens[6]
        elif (standard):
            id = 0
            self.permit = (tokens[id] == "permit")
            id = id + 1
            if (id + 1 < len(tokens) and ("." in tokens[id + 1])):
                self.sip = strip2intip(tokens[id], tokens[id + 1])
            elif (tokens[id] == "any"):
                self.sip = 0
            else:
                self.sip = strip2intip("host", tokens[id])
            self.dip = 0
            self.proto = 0
            self.sport = self.dport = None
        else:
            id = 0
            self.permit = (tokens[id] == "permit")
            id = id + 1
            self.proto = tokens[id]
            id = id + 1
            ## parse sip
            if (tokens[id] == "any"):
                self.sip = 0
                id = id + 1
            else:
                self.sip = strip2intip(tokens[id], tokens[id + 1])
                id = id + 2

            ## sparse sport
            self.sport = None
            if (id + 1 < len(tokens)):
                if (tokens[id] == 'eq'):
                    self.sport = tokens[id + 1]
                    id = id + 2
                elif (tokens[id] == 'range'):
                    self.sport = (tokens[id + 1], tokens[id + 2])
                    id = id + 3

            ## parse dip
            if (tokens[id] == "any"):
                self.dip = 0
                id = id + 1
            else:
                self.dip = strip2intip(tokens[id], tokens[id + 1])
                id = id + 2

            self.dport = None
            if (id + 1 < len(tokens)):
                if (tokens[id] == 'eq'):
                    self.dport = tokens[id + 1]
                    id = id + 2
                elif (tokens[id] == 'range'):
                    self.dport = (tokens[id + 1], tokens[id + 2])
                    id = id + 3
                

    def eq(self, e):
        return (self.sip == e.sip and
                self.dip == e.dip and
                self.sport == e.sport and
                self.dport == e.dport and
                self.proto == e.proto and
                self.permit == e.permit)

    def src_matched(self, sip):
        while (sip > self.sip):
            sip = (sip - 1) / 2
        return sip == self.sip

    def dst_matched(self, dip):
        while (dip > self.dip):
            dip = (dip - 1) / 2
        return dip == self.dip

    def src_group(self, e):
        return (#self.sip != e.sip and
                self.dip == e.dip and
                self.sport == e.sport and
                self.dport == e.dport and
                self.proto == e.proto and
                self.permit == e.permit)

    def dst_group(self, e):
        return (self.sip == e.sip and
                #self.dip != e.dip and
                self.sport == e.sport and
                self.dport == e.dport and
                self.proto == e.proto and
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

def strip2intip(s1, s2):
    def f(s):
        ls = s.rsplit('.')
        x = 0
        for l in ls:
            x = x << 8
            x = x + int(l)
        return x
    try:
        y = 0
        if (s1 == "host"):
            y = f(s2) + (1 << 32) - 1
        else:
            base = (1<<32) / (f(s2) + 1) - 1
            y = f(s1) / (f(s2) + 1) + base
    except ValueError, e:
        print "ERROR", s1, s2
        raise e
    return y

def intip2str(ip):
    s = ""
    while (ip > 0):
        if (ip % 2 == 0):
            s = "1" + s
        else:
            s = "0" + s
        ip = (ip - 1) / 2
    s = s + "*" * (32 - len(s))
    return s

def readin(input):
    fin = open(input, "r")
    fin.readline()
    entries = []
    for line in fin:
        tokens = line.rsplit(' ')
        entry = Entry(tokens, True)
        found = False
        for e in entries:
            if (e.eq(entry)):
                found = True
        if (not found):
            entries.append(entry)
    fin.close()
    return entries

def readin_purdue(input):
    fin = open(input, "r")
    entries_list = []
    entries_name = ""
    entries = []
    is_standard = True
    for line in fin:
        tokens = line.split()

        if (("ip access-list" in line) or 
            (len(tokens) == 0) or
            (tokens[0] != "permit" and
             tokens[0] != "deny" and
             tokens[0] != "remark")):
            if (len(entries) > 0):
                entries_list.append((entries_name, entries))
                entries = []
                entries_name = ""

            if ("ip access-list" in line):
                entries_name = tokens[-1]
                is_standard = ("standard" in line)
            continue

        if (entries_name == ""):
            continue
        if (tokens[0] == "remark"):
            continue
        entry = Entry(tokens, False, is_standard)
        entries.append(entry)

    if (len(entries) > 0):
        entries_list.append((entries_name, entries))

    fin.close()
    return entries_list

## return the join of ip1 and ip2
def joint(ip1, ip2):
    if (ip1 < ip2):
        x = ip1
        ip1 = ip2
        ip2 = x
    res = ip1
    while (ip1 > ip2):
        ip1 = (ip1 - 1) / 2
    if (ip1 != ip2):
        res = -1
    return res

## keep join two sips until the set does not change
def closed_sip_set(sips):
    prev = sips
    now = set()
    while True:
        for sip1 in prev:
            if (sip1 not in now):
                now.add(sip1)
            for sip2 in prev:
                sip3 = joint(sip1, sip2)
                if (sip3 > 0) and (sip3 not in now):
                    now.add(sip3)
        if (len(now) == len(prev)):
            break
        prev = now
        now = set()

    return now

## find the unit that sip belongs to (longest matching)
def find_unit(sip, units):
    best_ip = 0
    best_unit = None
    for unit in units:
        for ip in unit:
            if (joint(ip, sip) == sip):
                if (ip >= best_ip):
                    best_ip = ip
                    best_unit = unit
                break
    return best_unit


## find the policy units. 
## use_sip=True means source policy units
def analyze(entries, use_sip):
    
    if (use_sip):
        sips = {e.sip for e in entries}
    else:
        sips = {e.dip for e in entries}

    sips = closed_sip_set(sips)

    units = []
    ## iterate over all sip prefixes
    for sip1 in sips:
        found = False
        ## examine whether sip belongs to an existing units
        for unit in units:
            sip2 = unit[0]
            equal = True
            entries_i = []
            for ei in entries:
                if ((use_sip and ei.src_matched(sip1)) or
                    ((not use_sip) and ei.dst_matched(sip1))):
                    matched = False
                    for ej in entries:
                        if ((use_sip and ei.src_group(ej) and ej.src_matched(sip2)) or
                            ((not use_sip) and ei.dst_group(ej) and ej.dst_matched(sip2))):
                            matched = True
                            break
                    if (not matched):
                        equal = False
                        break
            if (equal):
                found = True
                unit.append(sip1)
                break
        if (not found):
            units.append([sip1])

    if (0 not in sips):
        units.append([0])
        
#    print "units", len(units)
#    for unit in units:
#        print "sips", len(unit)
#        print "\n".join(intip2str(k) for k in unit)
#        print "..........."
    return units



def across_acls(units_list):

    ## starts here
    sips = set()
    for units in units_list:
        for unit in units:
            for sip in unit:
                if (sip not in sips):
                    sips.add(sip)
    sips = closed_sip_set(sips)
#    print len(sips)

    groups = []
    sip_count = 0
    ## iterate over sips
    for sip1 in sips:
        found = False
        sip_count = sip_count + 1
        print sip_count, len(groups)
        ## examine if the sip belongs to an existing group
        for group in groups:
            sip2 = group[0]
            equal = True
            for units in units_list:
                unit1 = find_unit(sip1, units)
                unit2 = find_unit(sip2, units)
                if (unit1 != unit2):
                    equal = False
                    break
            if (equal):
                found = True
                group.append(sip1)
                break
        if (not found):
            groups.append([sip1])

#    print "groups", len(groups)
#    for group in groups:
#        print "sips", len(group)
#        print "\n".join(intip2str(k) for k in group)
#        print "..........."

    return groups


def minimum_rules(entries, src_units, dst_units):
    new_entries = []
    for e in entries:
        sip = e.sip
        dip = e.dip
        sunit = find_unit(sip, src_units)
        dunit = find_unit(dip, dst_units)
        entry = copy.copy(e)
        entry.sip = sunit[0]
        entry.dip = dunit[0]

        found = False
        for ne in new_entries:
            if entry.eq(ne):
                found = True
                break
        if (not found):
            new_entries.append(entry)

    return new_entries

        
## main function
input = sys.argv[1]
## s for use_sip, d for use_dip, a for across_acls, m for minimium #rules 
mode = sys.argv[2]
use_sip = ('s' in mode)
is_purdue = (sys.argv[3] == 'p')

if is_purdue:
    entries_list = readin_purdue(input)

    if 'a' in mode:
        src_units = []
        dst_units = []
        if ('s' in mode) or ('m' in mode):
            src_units_list = []
            for name, entries in entries_list:
                units = analyze(entries, True)
                if (len(units) == 1):
                    continue
                src_units_list.append(units)
            src_units = across_acls(src_units_list)
            if ('s' in mode):
                print "unit", len(src_units)

        if ('d' in mode) or ('m' in mode):
            dst_units_list = []
            for name, entries in entries_list:
                units = analyze(entries, True)
                if (len(units) == 1):
                    continue
                dst_units_list.append(units)
            print "across"
            dst_units = across_acls(dst_units_list)
            print "across done"
            if ('d' in mode):
                print "unit", len(dst_units)
            
        if ('m' in mode):
            if ('s' in mode):
                print "src_unit", len(src_units)
                print "dst_unit", len(dst_units)
            for name, entries in entries_list:
                new_entries = minimum_rules(entries, src_units, dst_units)
                print "len", len(entries), len(new_entries)

    else:
        for name, entries in entries_list:
            print "ACL", name
            if ('s' in mode):
                units = analyze(entries, True)
                print "unit", len(units)
            elif ('d' in mode):
                units = analyze(entries, False)
                print "unit", len(units)
            elif ('m' in mode):
                src_units = analyze(entries, True)
                dst_units = analyze(entries, False)
                print "src_unit", len(src_units)
#                print src_units
                print "dst_unit", len(dst_units)
#                print dst_units
                new_entries = minimum_rules(entries, src_units, dst_units)
                print "len", len(entries), len(new_entries)
#                print "\n".join(str(e) for e in entries)
#                print "......"
#                print "\n".join(str(e) for e in new_entries)



else:
    entries = readin(input)
    analyze(entries, use_sip)
    
