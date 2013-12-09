#!/usr/bin/python
#
# reducer-sortedall.py
#

import sys
import ast

sortedSb0 = []

def merge(sortedScIndices, sortedSb0Values, suffixRanks, paddedText):
    def _getCSetIndex(cIndex):
        """
        Get the next index for the sortedSc array.
        """
        return cIndex + 1

    def _getB0SetIndex(b0Index):
        """
        Get the next index for the sortedSb0 array.
        """
        return b0Index + 1

    def _set01CompareFunction(cIndex, b0Index):
        # get the suffix index for the index in sortedSc array
        cSuffixIndex = sortedScIndices[cIndex]
        setCElement = paddedText[cSuffixIndex], suffixRanks[cSuffixIndex+1]

        # get the suffix index from sortedSb0 array
        b0SuffixIndex = int(sortedSb0Values[b0Index])
        setb0Element = paddedText[b0SuffixIndex], suffixRanks[b0SuffixIndex+1]
        return setCElement < setb0Element

    def _set02CompareFunction(cIndex, b0Index):
        # get the suffix index for the index in sortedSc array
        cSuffixIndex = sortedScIndices[cIndex]
        setCElement = paddedText[cSuffixIndex], paddedText[cSuffixIndex+1], suffixRanks[cSuffixIndex+2]
        
        # get the suffix index from sortedSb0 array
        b0SuffixIndex = int(sortedSb0Values[b0Index])
        setb0Element = paddedText[b0SuffixIndex], paddedText[b0SuffixIndex+1], suffixRanks[b0SuffixIndex+2]
        return setCElement < setb0Element

    def _mergefunction():
        suffixArray = []
        b0Index = 0
        cIndex = 0
        cIndexMax = len(sortedScIndices)
        b0IndexMax = len(sortedSb0Values)

        while b0Index < b0IndexMax or cIndex < cIndexMax:
            if cIndex < cIndexMax and b0Index < b0IndexMax:
                if sortedScIndices[cIndex] % 3 == 1:
                    smaller = _set01CompareFunction(cIndex, b0Index)
                    if smaller:
                        suffixArray.append(sortedScIndices[cIndex])
                        cIndex = _getCSetIndex(cIndex)
                    else:
                        suffixArray.append(sortedSb0Values[b0Index])
                        b0Index = _getB0SetIndex(b0Index)
                elif sortedScIndices[cIndex] % 3 == 2:
                    smaller = _set02CompareFunction(cIndex, b0Index)
                    if smaller:
                        suffixArray.append(sortedScIndices[cIndex])
                        cIndex = _getCSetIndex(cIndex)
                    else:
                        suffixArray.append(sortedSb0Values[b0Index])
                        b0Index = _getB0SetIndex(b0Index)
            elif cIndex < cIndexMax:
                suffixArray.append(sortedScIndices[cIndex])
                cIndex = _getCSetIndex(cIndex)
            elif b0Index < b0IndexMax:
                suffixArray.append(int(sortedSb0Values[b0Index]))
                b0Index = _getB0SetIndex(b0Index)
        return suffixArray
    return _mergefunction()

sortedSc = []
siRanks = []
rPaddedText = ''

for line in sys.stdin:
    text = line.rstrip()
    info, value = text.split('\t', 1)

    if info == 'p':
        rPaddedText = ast.literal_eval(value)
    elif info == 's':
        sortedSc = ast.literal_eval(value)
    elif info == 'r':
        siRanks = ast.literal_eval(value)
    else:
        sortedSb0.append(int(value))

print merge(sortedSc, sortedSb0, siRanks, rPaddedText)
