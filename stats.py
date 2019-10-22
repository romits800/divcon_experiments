#! /usr/bin/python

from os import listdir

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

import json

import sys

files = dict()

if (len(sys.argv)<3):
        print "Give two arguments"
        exit(0)

for f in listdir("."):
    if f.endswith("." + sys.argv[2] + ".out.json"):
        try:
            files[f] = json.loads(open(f).read())
        except:
            continue

if (len(sys.argv) > 1) and len(files)>0:
    import pickle
    pickle.dump(files, open(sys.argv[1] + ".pickle", "w"))



