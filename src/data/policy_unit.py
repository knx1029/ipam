import sys
import operator
import copy
from utils import *

def readin_gatech_s(input):
    fin = open(input, "r")
    fin.readline()
    entries = []
    for line in fin:
        tokens = line.rsplit(' ')
        entry = Entry()
        entry.set_fields(tokens, True)
        found = False
        for e in entries:
            if (e.eq(entry)):
                found = True
        if (not found):
            entries.append(entry)
    fin.close()
    return entries

def readin_gatech_m(input):
    fin = open(input, "r")
    entries = None
    entries_list = []
    while (True):
        line = fin.readline()
        if (line == None) or (len(line) == 0):
            break
        if ("GaTechAcl" in line):
            if (entries != None):
                entries_list.append((name, entries))
            name = line
            entries = []
            fin.readline()
#            if (len(entries_list) > ):
#                break
        else:
            tokens = line.rsplit(' ')
            entry = Entry()
            entry.set_fields(tokens, True)
            found = False
            for e in entries:
                if (e.eq(entry)):
                    found = True
            if (not found):
                entries.append(entry)
    if (entries != None) and (len(entries) > 0):
        entries_list.append((name, entries))
    fin.close()
    return entries_list


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
        entry = Entry()
        entry.set_fields(tokens, False, is_standard)
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
    unit_entries = []
    ## iterate over all sip prefixes
    for sip1 in sips:
        matched_entries = []
        ## find all the matching rules
        for ei in entries:
            if ((use_sip and ei.src_matched(sip1)) or
                ((not use_sip) and ei.dst_matched(sip1))):
                shadowed = False
                for ej in matched_entries:
                    if ((use_sip and ei.src_shadow(ej)) or
                        ((not use_sip) and ei.dst_shadow(ej))):
                        shadowed = True
                        break
                if (not shadowed):
                    matched_entries.append(ei)
                    
#        print intip2ip(sip1)
#        print "\n".join(str(e) for e in matched_entries)
#        print ""

        found = False
        ## examine whether sip belongs to an existing units
        for ui in range(len(units)):
            unit = units[ui]
            uentries = unit_entries[ui]
            if (len(uentries) != len(matched_entries)):
                continue

            equal = True
            ## priority must match
            for index in range(len(uentries)):
                ei = uentries[index]
                ej = matched_entries[index]
                if ((use_sip and (not ei.src_group(ej))) or
                    ((not use_sip) and (not ei.dst_group(ej)))):
                    equal = False
            if (equal):
                found = True
                unit.append(sip1)
                break
        if (not found):
            units.append([sip1])
            unit_entries.append(matched_entries)

    if (0 not in sips):
        units.append([0])
        unit_entries.append([])
        
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
#        print sip_count, len(groups)
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
else:
    if 'a' in mode:
        entries_list = readin_gatech_m(input)
    else:
        entries_list = [("", readin_gatech_s(input))]

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
            units = analyze(entries, False)
            if (len(units) == 1):
                continue
            dst_units_list.append(units)
            dst_units = across_acls(dst_units_list)
        if ('d' in mode):
            print "unit", len(dst_units)

    if ('s' in mode):
        print "src_unit", len(src_units)
    elif ('d' in mode):
        print "dst_unit", len(dst_units)
    elif ('m' in mode):
        for name, entries in entries_list:
            if (is_purdue):
                print name
            else:
                print name,
            print "src_unit", len(src_units)
            print src_units
            print "dst_unit", len(dst_units)
            print dst_units
            new_entries = minimum_rules(entries, src_units, dst_units)
            print "len", len(entries), len(new_entries)
            print "\n".join(str(e) for e in new_entries)

else:
    for name, entries in entries_list:
        if (is_purdue):
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
            print src_units
            print "dst_unit", len(dst_units)
            print dst_units
            new_entries = minimum_rules(entries, src_units, dst_units)
            print "len", len(entries), len(new_entries)
            print "\n".join(str(e) for e in new_entries)
    
