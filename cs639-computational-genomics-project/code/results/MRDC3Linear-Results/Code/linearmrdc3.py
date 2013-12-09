#!/usr/bin/python
#
# linearmrdc3.py
#
# Created by Kartik Thapar on 11/28/2013 at 20:06:30
# Copyright (c) 2013 Kartik Thapar. All rights reserved.
#

"""
For C, a subset of [0, n], Sc = {Si | i in C} and C is B1 U B2.
"""

from mrjob.job import MRJob
import sys, StringIO, ast
import cProfile
import time

DEBUG_MODE = False

rPaddedText, rLength = [], []
rDigits = 0
R = []
B0, B1, B2 = [], [], []
duplicatesExist, deepestLevel = False, False
sortedSc = []
siRanks = []
rDepth = 0
rDashes = []
currentSuffixArray = None

ALPHA_NUM_MAP = {'a': '01', 'c': '03', 'b': '02', 'e': '05', 'd': '04', 'g': '07', 'f': '06', 'i': '09', 'h': '08', 'k': '11', 'j': '10', 'm': '13', 'l': '12', 'o': '15', 'n': '14', 'q': '17', 'p': '16', 's': '19', 'r': '18', 'u': '21', 't': '20', 'w': '23', 'v': '22', 'y': '25', 'x': '24', 'z': '26', '0': '00'}

def constructNumFromMap(text):
    return [ALPHA_NUM_MAP[t] for t in text]

def constructTextFromMap(numList):
    """
    Used only for logging purposes.
    """
    return [NUM_ALPHA_MAP[t] for t in numList]

def adjustWithNumberOfDigits(t):
    if rDepth == 0:
        return '0' * (2 - len(str(t))) + str(t)
    else:
        return '0' * (rDigits - len(str(t))) + str(t)

class MRProcessReferenceText(MRJob):
    """
    A map-reduce job that processes the text to initiate the process for obtaining sorted sample and non-sample suffixes.

    Using the reference text as the input, create sets of sample and non sample suffixes to sort them in the second job. After the sets
    are created, create and sort triples to create the string R' which contains the ordering for the sample suffixes. As the ordering in R'
    might have duplicates, this job accounts for all the set and R' values to be later used in the next MRSortAndMerge map-reduce job to
    unfold the recursion.
    """
    def mapperConstructSample(self, _, text):
        """
        Create B1, B2 sets of indices.

        INPUT:  (_, ReferenceText)
        OUTPUT: (_, ReferenceText)
        """
        global rDepth, rPaddedText, rLength, rDigits, duplicatesExist, B0, B1, B2
        text = constructNumFromMap(text) if rDepth == 0 else [adjustWithNumberOfDigits(i) for i in ast.literal_eval(text)]
        duplicatesExist = False
        
        rLength.append(len(text))

        if rDepth == 0:
            text = text + ['00', '00', '00']
        else:
            text = text + ['0'*rDigits] * 3
        rPaddedText.append(text)

        if rDepth == 0:
            rDigits = len(str(rLength[-1]))

        def getBSet(kval):
            return [i for i in range(0, rLength[-1] + 1) if i % 3 == kval]

        B0.append(getBSet(0))
        B1.append(getBSet(1))
        B2.append(getBSet(2))

        yield (None, None)

    def mapperGenerateTriples(self, _, __):
        """
        Create triples to construct the Rk strings for k = 1 and k = 2.

        INPUT:  (_, _)
        OUTPUT: (triples, 0)
        """
        global rPaddedText, rLength, R

        paddedText = rPaddedText[rDepth]
        R.append([paddedText[bval:bval+3] for bval in B1[rDepth]] + [paddedText[bval:bval+3] for bval in B2[rDepth]])

        for rkval in R[rDepth]:
            (a, b, c) = rkval
            rkval = [adjustWithNumberOfDigits(a), adjustWithNumberOfDigits(b), adjustWithNumberOfDigits(c)]
            yield (rkval, 0)

    def initReducerToRankTriples(self):
        """
        Reducer initalizer to start the ranking for all the triples that constitute the R string. The R string might contain duplicate triples.
        Every unique triple has a unique rank and because of the mapper->reducer step, all triples are sorted lexicographically and have incremental
        ranks.
        """
        self.rank = 1
        self.tripleRankMap = {}
    
    def reducerSortedTriples(self, triple, times):
        """
        Reducer:

        This reducer is specifically used to rank sorted triples to create a new R' string. In this step, we also check if 
        duplicates exist if the number of times the triple occurs is greater than 1. Every triple has a rank and all triples
        have different ranks. Therefore, we only need to assess one triple to decide it's rank. The actual processing of the R
        string to get R' string is done in the reduce step.

        INPUT:  (triple, numerOfOccurrencesOfTriple)
        OUTPUT: ()
        """
        global duplicatesExist
        times = [time for time in times]
        if len(times) > 1:
            """
            If duplicates, exist => for this depth, we cannot calculate the suffix array at this point yet
            so we have temporary None/null values for the sorted sample and non-sample suffixes at this point.
            """
            duplicatesExist = True
        self.tripleRankMap[str(triple)] = self.rank
        self.rank += 1

    def finalReducerToRankSortedTriples(self):
        """
        After getting all the ranks, create R' from R.
        """
        def printMap():
            for (key, val) in self.tripleRankMap.items():
                print constructTextFromMap([int(v) for v in ast.literal_eval(key)]) + ' => ' + str(val)

        # create R'
        rdash = []
        for rval in R[rDepth]:
            rdash.append(self.tripleRankMap[str(rval)])
        rDashes.append(rdash)

    def stepConstructSample(self):
        """
        Construct the sample from the reference text.
        """
        return [
            self.mr(
                    mapper = self.mapperConstructSample
                    )
        ]

    def stepProcessTriples(self):
        """
        Using the triples, create R and R'.
        """
        return [
            self.mr(
                    mapper = self.mapperGenerateTriples,
                    reducer_init = self.initReducerToRankTriples,
                    reducer = self.reducerSortedTriples,
                    reducer_final = self.finalReducerToRankSortedTriples,
                    )
        ]

    def steps(self):
        return self.stepConstructSample() + self.stepProcessTriples()

class MRSortAndMerge(MRJob):
    def mapperCreateSortedTriples(self, _, rDashString):
        """
        Mapper:

        Use the R' of a particular string in the recursion tree and create sorted sample suffixes. After sorting the sample suffixes, 
        the reducer creates the array suffix ranks that is used

        INPUT:  (_, rDashString)
        OUTPUT: (_, textRankIndexPair)
        """
        def _getSortedSc(rdash, b1, b2):
            """
            Get a sequence of suffixes where Si <= Sj where i, j belong to C.
            The number of operations are n/3 => O(n) and each operation takes constant time operations.
            """
            rdash = ast.literal_eval(rdash)
            C = b1 + b2
            sortedScSet = [-1] * len(C)
            """
            There are two cases for this; when R' has duplicates => SA(R') and R' doesn't have any duplicates.
            case 1:
                sortedScSet[rdash[i]]    = C[i]
            case 2:
                sortedScSet[i] = C[rdash[i]]
            """

            if deepestLevel == True:
                for i in range(0, len(rdash)):
                    sortedScSet[rdash[i]-1] = C[i]
            else:
                for i in range(1, len(rdash)):
                    sortedScSet[i-1] = C[rdash[i]]
            return sortedScSet

        def _getSuffixRanks(sortedSc, text, length):
            """
            For every suffix in the sorted list of suffixes of indices in C, we rank the suffixes and order them in an array
            as described in the annotated literature.
            """
            suffixRanks = [None] * (len(text) + 3) # ... import space bound efficiency here
            trank = 1

            for suffix in sortedSc:
                suffixRanks[suffix] = trank
                trank += 1
            suffixRanks[length]     = 0
            suffixRanks[length + 1] = 0
            suffixRanks[length + 2] = 0
            return suffixRanks

        """
        R' without duplicates has numbers from 1 to x exceeds the bounds for C. The ranks should have started with 0 but because,
        we are already using the value 0 as a sentinel, we avoiding using it in the ranks. Therefore, when R' doesn't have any duplicates,
        we need to adjust for 0 by -1.
        If R' however has duplicates, we create the suffix array of R' which uses 0 as the base value and can be used for indexing without
        any issue.

        - Debug: So in the example below, we demonstrate by using a fake rdashSuffixArray entity which is now 0 based manually and can be
        used for indexing.
        """

        global B0, B1, B2, sortedSc, rPaddedText, rLength, siRanks, deepestLevel
        paddedText = rPaddedText[rDepth]

        sortedSc = _getSortedSc(rDashString, B1[rDepth], B2[rDepth])
        siRanks = _getSuffixRanks(sortedSc, paddedText, rLength[rDepth])
        
        for bval in B0[rDepth]:
            nrank = '0' * (rDigits - len(str(siRanks[bval+1]))) + str(siRanks[bval+1])
            yield ((paddedText[bval], nrank), bval)

    def initReducerCreateNonSampleSuffixList(self):
        self.sortedSb0 = []

    def reducerGetSortedNonSampleSuffixes(self, tupleRank, indices):
        """
        Reducer:

        Get sorted non sample suffixes and accumulate them to finally merge the sorted sample and non sample suffixes.

        INPUT:  (tupleRank, indices)
        OUTPUT: ()
        """
        self.sortedSb0.append([index for index in indices][0])

    def finalReducerSuffixMerge(self):
        """
        After obtaining the sorted sets, merge.
        """
        global sortedSc, siRanks, currentSuffixArray, rPaddedText

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

        currentSuffixArray = merge(sortedSc, self.sortedSb0, siRanks, rPaddedText[rDepth])

    def stepsSortAndMerge(self):
        return [
            self.mr(
                    mapper = self.mapperCreateSortedTriples,
                    reducer_init = self.initReducerCreateNonSampleSuffixList,
                    reducer = self.reducerGetSortedNonSampleSuffixes,
                    reducer_final = self.finalReducerSuffixMerge
                    )
        ]
    def steps(self):
        return self.stepsSortAndMerge()

def createRDashStringMRJob():
    inputText = StringIO.StringIO(sys.stdin.readline().rstrip())
    mrPRTJob = MRProcessReferenceText(['-r', 'inline', '--no-conf', '-'])
    mrPRTJob.sandbox(stdin=inputText)
    with mrPRTJob.make_runner() as runner:
        runner.run()

def createSuffixArrayMRJob(text):
    inputText = StringIO.StringIO(text)
    mrSAMJob = MRSortAndMerge(['-r', 'inline', '--no-conf', '-'])
    mrSAMJob.sandbox(stdin=inputText)
    with mrSAMJob.make_runner() as runner:
        runner.run()

def calc(text):
    global rDepth, duplicatesExist, deepestLevel

    # ----- CREATE RECURSION -----
    rDepth = -1
    duplicatesExist = True
    while duplicatesExist:
        rDepth += 1
        inputText = text if rDepth == 0 else rDashes[-1]
        inputText = StringIO.StringIO(inputText)
        mrPRTJob = MRProcessReferenceText(['-r', 'inline', '--no-conf', '-'])
        mrPRTJob.sandbox(stdin=inputText)
        with mrPRTJob.make_runner() as runner:
            runner.run()

    # ----- UNFOLD RECURSION -----
    maxDepth = rDepth
    while rDepth >= 0:
        inputText = ''
        if rDepth == maxDepth:
            # if at the last level, use the R' string available to create the suffix array
            deepestLevel = True
            inputText = StringIO.StringIO(rDashes[-1])
        else:
            # if not at the last level, use the current suffix array as R' => gives ordering for Sc
            deepestLevel = False
            inputText = StringIO.StringIO(currentSuffixArray)
        mrSAMJob = MRSortAndMerge(['-r', 'inline', '--no-conf', '-'])
        mrSAMJob.sandbox(stdin=inputText)
        with mrSAMJob.make_runner() as runner:
            runner.run()
        rDepth -= 1
    return currentSuffixArray

if __name__ == '__main__':
    try:
        if sys.argv[1] == '-d':
            DEBUG_MODE = True
    except Exception, e:
        pass
    start = time.time()
    SA= calc(sys.stdin.readline().rstrip())
    end = time.time()
    print("Total Time: "+ str(end-start))
    print("SA: "+ str(SA))