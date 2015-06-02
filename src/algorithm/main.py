import sys
import ipam

option = "ipam"
#option = "shorten"

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
