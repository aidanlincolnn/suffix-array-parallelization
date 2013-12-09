#!/usr/bin/python
#
# mapper-sortedall.py
#

import sys
import re
import ast

sortedSc = []
suffixRanks = []

maxDepth, rDepth, rDigits = 0, 0, 0
currentSuffixArray = ''
deepestLevel = False

# send max depth using a command line argument to the mapper
try:
    maxDepth, rDepth, rDigits = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    currentSuffixArray = sys.argv[4]
except Exception, e:
    pass

# create b0, b1 and b2
def getBSets():
    b0, b1, b2 = [], [], []
    for i in range(0, rLength + 1):
        if i % 3 == 0:
            b0.append(i)
        elif i % 3 == 1:
            b1.append(i)
        elif i % 3 == 2:
            b2.append(i)
    return b0, b1, b2

def getSortedSc(rdash, b1, b2):
    C = b1 + b2
    sortedScSet = [-1] * len(C)

    if deepestLevel == True:
        for i in range(0, len(rdash)):
            sortedScSet[rdash[i]-1] = C[i]
    else:
        for i in range(1, len(rdash)):
            sortedScSet[i-1] = C[rdash[i]]
    return sortedScSet

def getSuffixRanks(sortedSc, text, length):
    suffixRanks = [None] * (len(text) + 3) # ... import space bound efficiency here
    trank = 1

    for suffix in sortedSc:
        suffixRanks[suffix] = trank
        trank += 1
    suffixRanks[length]     = 0
    suffixRanks[length + 1] = 0
    suffixRanks[length + 2] = 0
    return suffixRanks

for line in sys.stdin:
    text = line.rstrip()
    content = re.split('\t', text)
    duplicatesExist, rLength = ast.literal_eval(content[0])
    rDashString, rPaddedText = ast.literal_eval(content[1])

    if currentSuffixArray != '':
        rDashString = ast.literal_eval(currentSuffixArray)

    rPaddedText = ast.literal_eval(rPaddedText)

    if rDepth == maxDepth:
        # R' is the suffix array because there are no duplicates at the last level
        deepestLevel = True
    else:
        deepestLevel = False

    B0, B1, B2 = getBSets()

    sortedSc = getSortedSc(rDashString, B1, B2)
    siRanks = getSuffixRanks(sortedSc, rPaddedText, rLength)

    for bval in B0:
        nrank = '0' * (rDigits - len(str(siRanks[bval+1]))) + str(siRanks[bval+1])
        print "%s\t%s" % ((rPaddedText[bval], nrank), bval)

    print "%s\t%s" % ('p', rPaddedText)
    print "%s\t%s" % ('s', sortedSc)
    print "%s\t%s" % ('r', siRanks)

