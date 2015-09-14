import sys
import ipam
import vlan

option = "ipam"
#option = "shorten"
#option = "vlan"

if (option == "ipam"):
    input_filename = sys.argv[1]
    mode = sys.argv[2]
    nbits = None
    if (len(sys.argv) > 3):
        nbits = sys.argv[3]
    ipam.ipam(input_filename, mode, nbits)
## to check the new input format by ../data/gen_input.py
elif (option == "shorten"):
    input_filename = sys.argv[1]
    ipam.shorten(input_filename)
elif (option == "vlan"):
    input_filename = sys.argv[1]
    inputs = ipam.readin(input_filename, True, True)
    vlan.num_bits(inputs)
