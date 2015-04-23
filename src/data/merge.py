import sys
import operator

def repeat(input):
    fin = open(input, "r")
    fin.readline()
    for line in fin:
        print line,
    fin.close()

input = sys.argv[1]
repeat(input)
