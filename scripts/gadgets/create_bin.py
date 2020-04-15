import cPickle as pickle
import json
import sys
import os

fname = sys.argv[1]

d = pickle.load(open(fname))
for jname in d:
   json.dump(d[jname], open(jname, 'w'))
    

