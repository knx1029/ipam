import sys
import ipam

option = "ipam"

if (option == "ipam"):
    input_filename = sys.argv[1]
    mode = sys.argv[2]
    nbits = None
    if (len(sys.argv) > 3):
        nbits = sys.argv[3]
    ipam.ipam(input_filename, mode, nbits)
