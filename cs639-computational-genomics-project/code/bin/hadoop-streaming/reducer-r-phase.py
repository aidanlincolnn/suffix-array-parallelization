#!/usr/bin/python
#
# reducer-r-phase.py
#

from operator import itemgetter
import sys
from ast import literal_eval

rank = 1
tripleRankMap = {}
lastTriple = []

duplicatesExist, rLength, R, rPaddedText = False, 0, None, None

for line in sys.stdin:
    line = line.strip()

    # R is the last value for (key, value) of type ('z', R)
    triple, waste = line.split('\t', 1)

    if triple == 'l':
        rLength = int(waste)
    elif triple == 'p':
        rPaddedText = waste
    elif triple == 'r':
        R = waste
    
    if triple == lastTriple:
        """
        If duplicates, exist => for this depth, we cannot calculate the suffix array at this point yet
        so we have temporary None/null values for the sorted sample and non-sample suffixes at this point.
        """
        duplicatesExist = True
    else:
        lastTriple = triple
        tripleRankMap[str(triple)] = rank
        rank += 1

R = literal_eval(R)
rdash = []
for rval in R:
    rdash.append(tripleRankMap[str(rval)])

print '%s\t%s' % ((duplicatesExist, rLength), (rdash, rPaddedText))
