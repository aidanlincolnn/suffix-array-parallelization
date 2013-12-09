#!/usr/bin/python
#
# non-recursive-dc3.py
#

import sys

class DC3NonRecursive(object):
    """
    Non recursive DC3
    """
    def __init__(self, text):
        self.text = text
        self.textlen = len(text)

    def getbset(self, kval):
        bset = []
        for i in range(0, self.textlen):
            if i % 3 == kval:
                bset.append(i)
        return bset

    def yieldrkstrings(self, kval):
        r = []
        for i in range(kval, self.textlen, 3):
            r.append(self.text[i:i+3])
        return r

    def getrdash(self, r, sortedr):
        trmap = {}
        trank = 0
        for rval in sortedr:
            trmap[rval] = trank
            trank += 1
    
        # get r'
        rdash = []
        for rval in r:
            rdash.append(trmap[rval])
        return rdash

    def getsortedsc(self, rdash):
        c = self.b1 + self.b2
        sortedsc = [-1] * len(rdash)
        for i in range(0, len(rdash)):
            sortedsc[rdash[i]] = c[i]
        return sortedsc

    def getsuffixranks(self, sortedsc):
        # get suffix ranks
        suffixranks = [None] * (len(self.text) + 3)
        trank = 1
        for si in sortedsc:
            suffixranks[si] = trank
            trank += 1
        suffixranks[self.textlen] = 0
        suffixranks[self.textlen + 1] = 0
        suffixranks[self.textlen + 2] = 0
        return suffixranks

    def getsortedsb0(self, suffixranks):
        sordering = []
        for bval in self.b0:
            sordering.append(((self.text[bval], suffixranks[bval + 1]), bval))
        return sorted(sordering, key = lambda tup: (tup[0]))

    def merge(self, sortedsc, sortedsb0, suffixranks, paddedText):
        def _getcindex(cindex):
            return cindex + 1

        def _getb0index(b0index):
            return b0index + 1

        def _bc1cmp(cindex, b0index):
            csuffixindex = sortedsc[cindex]
            celement = paddedText[csuffixindex], suffixranks[csuffixindex+1]
            rb0index = sortedsb0[b0index][1]
            b0element = paddedText[rb0index], suffixranks[rb0index+1]
            return celement < b0element

        def _bc2cmp(cindex, b0index):
            csuffixindex = sortedsc[cindex]
            celement = paddedText[csuffixindex], paddedText[csuffixindex+1], suffixranks[csuffixindex + 2]
            rb0index = sortedsb0[b0index][1]
            b0element = paddedText[rb0index], paddedText[rb0index+1], suffixranks[rb0index+2]
            return celement < b0element

        def _mergefunction():
            sa = []
            b0index = 0
            cindex = 0
            cindexmax = len(sortedsc)
            b0indexmax = len(sortedsb0)
            while b0index < b0indexmax or cindex < cindexmax:
                if cindex < cindexmax and b0index < b0indexmax:
                    if sortedsc[cindex] % 3 == 1:
                        smaller = _bc1cmp(cindex, b0index)
                        if smaller:
                            sa.append(sortedsc[cindex])
                            cindex = _getcindex(cindex)
                        else:
                            sa.append(sortedsb0[b0index][1])
                            b0index = _getb0index(b0index)
                    elif sortedsc[cindex] % 3 == 2:
                        smaller = _bc2cmp(cindex, b0index)
                        if smaller:
                            sa.append(sortedsc[cindex])
                            cindex = _getcindex(cindex)
                        else:
                            sa.append(sortedsb0[b0index][1])
                            b0index = _getb0index(b0index)
                elif cindex < cindexmax:
                    sa.append(sortedsc[cindex])
                    cindex = _getcindex(cindex)
                elif b0index < b0indexmax:
                    sa.append(sortedsb0[b0index][1])
                    b0index = _getb0index(b0index)
            return sa
        return _mergefunction()

    def getsuffixarray(self):
        # get bsets
        self.b0 = self.getbset(0)
        self.b1 = self.getbset(1)
        self.b2 = self.getbset(2)

        # get R and R'
        r1 = self.yieldrkstrings(1)
        r2 = self.yieldrkstrings(2)
        r = r1 + r2

        # get sorted r
        sortedr = sorted(r)

        # get sorted r'
        rdash = self.getrdash(r, sortedr)
        print rdas
        # get sorted Sc
        sortedsc = self.getsortedsc(rdash)

        # get suffix ranks
        suffixranks = self.getsuffixranks(sortedsc)

        # get sorted sb0
        sortedsb0 = self.getsortedsb0(suffixranks)

        # merge
        return self.merge(sortedsc, sortedsb0, suffixranks, self.text + '00')

try:
    s = DC3NonRecursive(sys.argv[1])
    suffixarray = s.getsuffixarray()
    print suffixarray
except:
    exit()
