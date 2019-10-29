#! /usr/bin/python

from os import listdir

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

import json

import sys

def levenshtein_distance(s, t):
        d = [[0 for i in range(len(s)+1)] for j in range(len(t)+1)]
        for i in range(1, len(s)+1):
                d[0][i] = i
        for i in range(1, len(t)+1):
                d[i][0] = i

        for i in range(1, len(s)+1):
                for j in range(1, len(t)+1):
                        subcost = 0 if s[i-1] == t[j-1] else 1
                        d[j][i] = min( d[j-1][i] + 1, d[j][i-1] +1 , d[j-1][i-1] + subcost)

        return d[-1][-1]

files = dict()

if (len(sys.argv)<2):
        print "Give as argument the benchmark name"
        exit(0)

for f in listdir("."):
    if f.endswith("." + sys.argv[1] + ".out.json"):
        try:
            files[f] = json.loads(open( f).read())
        except:
            continue

def reverse_order(c):
        print c
        # exit(0)
        d = [0 for _ in range(max(c))]
        for i,ci in enumerate(c):
                if (ci == -1):
                        continue
                d[ci-1] = i
        return d
# if (len(sys.argv) > 1) and len(files)>0:

cycles = {h:[ c for  c,j  in zip(files[h]['global_cycles'],files[h]['type']) if j in [0,1,2,3,4,14]] for h in files if files[h].has_key('type') and files[h].has_key('global_cycles')}

exorder = {h:reverse_order(cycles[h]) for h in cycles }

if (len(cycles) == 0):
    exit(0)


fnames = files.keys()
d = dict()
sumhd = 0
count = 0
maxnum = 0
for i in range(len(fnames)):
    for j in range(i+1, len(fnames)):
        f1,f2 = fnames[i],fnames[j]
        d[(f1,f2)] = levenshtein_distance(exorder[f1],exorder[f2]) #zip(files[f1],files[f2])
        sumhd += d[(f1,f2)]
        count += 1.

freq = dict()
for di in d:
        if freq.has_key(d[di]):
                freq[d[di]].append(di)
        else:
                freq[d[di]] = [di]

for fi in freq:
        print fi, len(freq[fi])

mink = min(freq.keys())
maxk = max(freq.keys())
print mink
print freq[mink][0]
print maxk
print freq[maxk][0]


print count
print "Hdist:", (1.0*sumhd)/count



