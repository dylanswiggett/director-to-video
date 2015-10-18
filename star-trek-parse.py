#!/usr/bin/python

import script as s
import sys

def parse(path):
    f = open(path, 'r')

    # Get characters!
    for line in f:
        if "CAST" in line: break
    print "Cast:"

    for line in f:
        if ("STAR TREK" in line):
            break
        line = line.strip()
        if line == "": continue

    # Get sets!
    for line in f:
        if "SETS" in line: break
    print "Sets:"
    
    # Get scenes!

if __name__=="__main__":

    if len(sys.argv) != 2:
        print "USAGE: ./star-trek-parse <scriptpath>"
        exit(1)

    print "Parsing script from %s" % sys.argv[1]
    parse(sys.argv[1])
