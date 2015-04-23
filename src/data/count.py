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


input = sys.argv[1]
readin(input)
