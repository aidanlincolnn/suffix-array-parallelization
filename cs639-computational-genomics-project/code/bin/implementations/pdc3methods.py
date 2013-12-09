#!/usr/bin/python
#
# raw_methods_pdc3.py
#

import operator

areRanksUnique = True

def getTrituples(text, paddedText):
    """
    Get (codon, index) type values from the padded text where index % 3 is not 0.
    """
    return {(paddedText[i:i+3], i) for i in range(0, len(text)) if i % 3 != 0}

def getSortedTrituples(trituples):
    """
    Sort trituples using the first component of the trituples of the form: {(xyz, 1),...} where xyz is the triple/codon
    from the main text string.
    """
    def _slowSort(trituples):
        return sorted(trituples, key = lambda tup: tup[0])
    return _slowSort(trituples)

def getRankIndexPairs(sortedTrituples):
    """
    Rank the sorted trituples such that each 3-character substring is a unique rank. The rank here refers to the rank of
    the trituple. For example: (xyz, 3) and (xyz, 7) are two different triples with the same rank.
    """
    def _processRankIndexPair(rankIndexPair):
        return rankIndexPair

    # At every instance of this method, we also check if the ranks collected are unique or not. We initialized 
    # areRanksUnique to True. But the IF condition in the loop changes this to False if two consecutive ranks are the same.

    global areRanksUnique
    areRanksUnique = True
    tupleCollection = []

    x = 1
    tupleCollection.append(_processRankIndexPair((x, sortedTrituples[0][1])))
    for i in range(1, len(sortedTrituples)):
        if sortedTrituples[i][0] != sortedTrituples[i-1][0]:
            x += 1
        else:
            # Because this is kind of a singleton flag, if the value is not false in one particular iteration of the pdc3 run,
            # then it can never be false again. That is where the recursion ends and we get a unique rank set.
            areRanksUnique = False
        tupleCollection.append(_processRankIndexPair((x, sortedTrituples[i][1])))
    return tupleCollection

def getSortedRankIndexPairs(rankIndexPairs):
    """
    Get unique (rank, index) pairs by permuting (rank, index) in P=names such that they are sorted by index % 3 and index / 3
    """
    def _slowSort(rankIndexPairs):
        return sorted(rankIndexPairs, key = lambda tup: (tup[1] % 3, tup[1] / 3))
    return _slowSort(rankIndexPairs)

def getIndexSortedRankIndexPairs(rankIndexPairs):
    return sorted(rankIndexPairs, key = lambda tup: tup[1])

def computeS0(indexSortedRankIndexPairs, text, paddedText):
    """
    S[0] = {(T[i], T[i+1], c', c'', i), ...} where i mod 3 = 0, where (c', i+1),(c'', i+2) are in P
    """
    s0 = OrderedSet()
    for i in range(0, len(text)):
        if i % 3 == 0:
            # calculate the value for which we are going to find i+1 and i+2 indexed tuples in the index sorted P array
            indexVal = 2 * i/3
            ti, ti1 = paddedText[i], paddedText[i+1]
            ci1, ci2 = None, None
            try:
                ci1 = indexSortedRankIndexPairs[indexVal][0]
            except:
                ci1 = 0
            try:
                ci2 = indexSortedRankIndexPairs[indexVal+1][0]
            except:
                ci2 = 0
            s0.add((ti, ti1, ci1, ci2, i))
    return s0

def computeS1(indexSortedRankIndexPairs, text, paddedText):
    """
    S[1] = {(c, T[i], c', i), ...} where i mod 3 = 1, where (c, i), (c', i+1) are in P
    """
    s1 = set()
    for i in range(0, len(text)):
        if i % 3 == 1:
            indexVal = 2*(i - 1)/3
            ti = paddedText[i]
            ci, ci1 = None, None
            try:
                ci = indexSortedRankIndexPairs[indexVal][0]
            except:
                ci = 0
            try:
                ci1 = indexSortedRankIndexPairs[indexVal+1][0]
            except:
                ci1 = 0
            s1.add((ci, ti, ci1, i))
    return s1

def computeS2(indexSortedRankIndexPairs, text, paddedText):
    """
    S[2] = {(c, T[i], T[i+1], c'', i), ...} where i mod 3 = 2, where (c, i), (c', i+2) are in P
    """
    s2 = set()
    for i in range(0, len(text)):
        if i % 3 == 2:
            indexVal = (2 * i - 1)/3
            ti, ti1 = paddedText[i], paddedText[i+1]
            ci, ci2 = None, None
            try:
                ci = indexSortedRankIndexPairs[indexVal][0]
            except:
                ci = 0
            try:
                ci2 = indexSortedRankIndexPairs[indexVal+1][0]
            except:
                ci2 = 0
            s2.add((ci, ti, ti1, ci2, i))
    return s2

def computeSortedSetUnion(s0, s1, s2):
    """
    Compute the union based on the given comparison.
    Sort S0 U S1 U S2 using the comparison function:
        (c, ...) in S1 U S2 <= (d, ...) in S1 U S2 <=> c <= d
        (t, t', c', c'', i) in S0 <= (u, u', d', d'', j) in S0 <=> (t, c') <= (u, d')
        (t, t', c', c'', i) in S0 <= (d, u,      d', j) in S1 <=> (t, c') <= (u, d')
        (t, t', c', c'', i) in S0 <= (d, u, u', d'', j) in S2 <=> (t, t', c'') <= (u, u', d'')
    """

    sorted12 = set(sorted(s1.union(s2), key = operator.itemgetter(0)))
    sorted0 = set(sorted(s0, key = operator.itemgetter(0, 2)))
    sorted01 = set(sorted(s0.union(s1), key = operator.itemgetter(0, 2)))
    sorted02 = set(sorted(s0.union(s2), key = operator.itemgetter(0, 2)))

    return sorted12.union(sorted0).union(sorted01).union(sorted02)
    
# ----- PDC3 -----

def runPDC3(text):
    # --- STEP 1: Build Trituples ---
    """
    Line 1 extracts the information needed for building the recursive subproblem which consists of two concatenated substrings of length n/3
    representing the mod 1 suffixes and mod 2 suffixes respectively.
    """

    # get all codons from i mod 3 != 0 and add them to a set
    # Triple = (xyz, 1) but is referred to as a trituple

    paddedText = text + '0' * 2;
    trituples = getTrituples(text, paddedText)
    print 'Text                           ' + text
    print 'Padded Text                    ' + paddedText
    print 'Trituples:                     ' + str(trituples)

    # --- STEP 2: Rank, Index ---
    """
    To find these ranks, the triples (annotated with their position in the input) are sorted in Line 2. Sorted Triples are named/ranked in Line 3.
    """

    sortedTrituples = getSortedTrituples(trituples)
    print 'Sorted Trituples:              ' + str(sortedTrituples)

    rankIndexPairs = getRankIndexPairs(sortedTrituples)
    print 'Rank Index Pairs:              ' + str(rankIndexPairs)

    # --- STEP 3: RECURSION ---
    """
    If all triples are unique, no recursion is necessary (Line 4). Otherwise, Line 5 assembles the recursive sub- problem, Line 6 solves it, 
    and Line 7 brings it into a form compatible with the output of the naming routine. In particular, function mapBack maps a position 
    in the recursive subproblem back to a position in the input.
    """

    sortedRankIndexPairs = getSortedRankIndexPairs(rankIndexPairs)
    print 'Sorted Rank Index Pairs:       ' + str(sortedRankIndexPairs)
    # if areRanksUnique == False:
    #     runPDC3(str(''.join([str(name) for (name, index) in sortedRankIndexPairs])))

    indexSortedRankIndexPairs = getIndexSortedRankIndexPairs(rankIndexPairs)
    print 'Index Sorted Rank Index Pairs: ' + str(indexSortedRankIndexPairs)

    # --- STEP 4: Finding Sets ----

    s0 = computeS0(indexSortedRankIndexPairs, text, paddedText)
    print 'Set0:                          ' + str(s0)

    s1 = computeS1(indexSortedRankIndexPairs, text, paddedText)
    print 'Set1:                          ' + str(s1)

    s2 = computeS2(indexSortedRankIndexPairs, text, paddedText)
    print 'Set2:                          ' + str(s2)

    # --- STEP 4: Sorting Sets ----

    sortedSets = computeSortedSetUnion(s0, s1, s2)
    print sortedSets

text = 'yabbadabbado'

runPDC3(text)
