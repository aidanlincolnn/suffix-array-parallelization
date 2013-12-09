#!/usr/bin/python
#
# mapper-r-phase.py
#

import sys
import re, ast

ALPHA_NUM_MAP = {'a': '01', 'c': '03', 'b': '02', 'e': '05', 'd': '04', 'g': '07', 'f': '06', 'i': '09', 'h': '08', 'k': '11', 'j': '10', 'm': '13', 'l': '12', 'o': '15', 'n': '14', 'q': '17', 'p': '16', 's': '19', 'r': '18', 'u': '21', 't': '20', 'w': '23', 'v': '22', 'y': '25', 'x': '24', 'z': '26', '0': '00'}

rDigits, rDepth = 0, 0
try:
    rDigits, rDepth = int(sys.argv[1]), int(sys.argv[2])
except Exception, e:
    pass

def constructNumFromMap(text):
    return [ALPHA_NUM_MAP[t] for t in text]

def adjustWithNumberOfDigits(t):
    if rDepth == 0:
        return '0' * (2 - len(str(t))) + str(t)
    else:
        return '0' * (rDigits - len(str(t))) + str(t)

for line in sys.stdin:
    text = line.rstrip()
    content = re.split(r'\t+', text)
    if len(content) == 1:
        text = constructNumFromMap(content[0])
    else:
        flags, text = re.split(r'\t+', text)
        duplicatesExist = ast.literal_eval(flags)
        text, someOtherText = ast.literal_eval(text)
        text = [adjustWithNumberOfDigits(t) for t in text]

    rLength = len(text)
    if rDepth == 0:
        text = text + ['00', '00', '00']
    else:
        text = text + ['0' * rDigits] * 3
    rPaddedText = (text)

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

    B0, B1, B2 = getBSets()

    R = [rPaddedText[bval:bval+3] for bval in B1] + [rPaddedText[bval:bval+3] for bval in B2]
    for rkval in R:
        (a, b, c) = rkval
        rkval = [adjustWithNumberOfDigits(a), adjustWithNumberOfDigits(b), adjustWithNumberOfDigits(c)]
        print '%s\t%s' % (rkval, 0)

    print '%s\t%s' % ('l', rLength)
    print '%s\t%s' % ('p', rPaddedText)
    print '%s\t%s' % ('r', R)
