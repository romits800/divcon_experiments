#! /usr/bin/python

from os import listdir

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

import json

import sys

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

# if (len(sys.argv) > 1) and len(files)>0:
    # import pickle
    # pickle.dump(files, open(sys.argv[1] + ".pickle", "w"))

brcycles = {h:[ c for  c,j  in zip(files[h]['global_cycles'],files[h]['type']) if j in [1,2,3]] for h in files if files[h].has_key('type') and files[h].has_key('global_cycles')}

cycles = {h:[ c for  c,j  in zip(files[h]['global_cycles'],files[h]['type']) if j in [0,1,2,3,4,14]] for h in files if files[h].has_key('type') and files[h].has_key('global_cycles')}
print brcycles 
print len(brcycles)
if (len(brcycles) == 0):
    exit(0)


fnames = files.keys()
d = dict()

sumhd = 0
count = 0
for i in range(len(fnames)):
    for j in range(i+1, len(fnames)):
        f1,f2 = fnames[i],fnames[j]
        brcycles1 = [c-cc for c in cycles[f1] for cc in brcycles[f1]] # '1' means branch
        brcycles2 = [c-cc for c in cycles[f2] for cc in brcycles[f2]] # '1' means branch

        d[(f1,f2)] = sum([ (1. if k!=l else 0.) for (k,l) in zip(brcycles1,brcycles2)] ) #zip(files[f1],files[f2])
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

# x = d.values()
# num_bins = max(x) - min(x)
# n, bins, patches = plt.hist(x, num_bins, normed=1, facecolor='blue', alpha=0.5)
# plt.xlabel("Hamming Distance")
# plt.ylabel("Frequency")

# if (len(sys.argv) > 1):
#     plt.title(sys.argv[1])
#     plt.show()
#     # plt.savefig(sys.argv[1] + ".jpg")
# #    dist[files] = sum([ (1 if i!=j else 0) for (i,j) in d[files]] )

print count
print "Hdist:", (1.0*sumhd)/count



