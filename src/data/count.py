import sys

def readin(input):
    fin = open(input, "r")
    fin.readline()

    counts = dict()
    config_name = ""
    acl_name = ""
    for line in fin:
        tokens = line.split(" ")
        if (tokens[0] == "config"):
            config_name = tokens[1]
            pass
        elif (tokens[0] == "ACL"):
            acl_name = tokens[1]
            pass
        elif (tokens[0] == "units"):
            unit_num = int(tokens[1])
            if (unit_num in counts):
                c, ex_config, ex_acl = counts[unit_num]
                counts[unit_num] = (c + 1, ex_config, ex_acl)
            else:
                counts[unit_num] = (1, config_name, acl_name)
    fin.close()

    for unit_num, (c, ex_config, ex_acl) in counts.items():
        print unit_num, ":", c
        print ex_config, ex_acl


def minimum(input):
    fin = open(input, "r")
    fin.readline()

    before = 0
    after = 0
    snum = 0
    dnum = 0
    cs = []
    acs = dict()
    for line in fin:
        tokens = line.split(" ")
        if (tokens[0] == "src_unit"):
            snum = int(tokens[1])
        if (tokens[0] == "dst_unit"):
            dnum = int(tokens[1])
        if (tokens[0] == "len"):
#            if (snum > 1 or dnum > 1):
            a = int(tokens[1])
            b = int(tokens[2])
            before = before + a
            after = after + b
            c = b * 1.0 / a

            cs.append(c)

            if a not in acs:
                acs[a] = []
            acs[a].append(c)

    fin.close()

    fout_template = "purdue_cdf{0}.csv"
    for a, cs in acs.items():
        print a, len(cs)
        fout_file = fout_template.format(a)
        fout = open(fout_file, "w")
        cdfs = sorted(cs)
        for i, c in enumerate(cdfs):
            fout.write("{0}, {1}\n".format(i * 1.0 / len(cdfs), c))
        fout.close()

#    cdfs = sorted(cs)
#    for i, c in enumerate(cdfs):
#        print i * 1.0 / len(cdfs), ",", c

#    print before, after

input = sys.argv[1]
#readin(input)
minimum(input)
