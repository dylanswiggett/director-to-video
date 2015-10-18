#!/usr/bin/python

# This will direct your movies
# They will be so good, you won't know what to do
# watch out hollywood

import star_trek_parse as parser

TESTFILE_PATH = "the-defector.txt"

def main():
    script = parser.parse(TESTFILE_PATH)
    
if __name__=="__main__":
    main()    
