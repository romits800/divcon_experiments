#! /usr/bin/python

from os import listdir

import json

import sys

import pickle

files = dict()

if (len(sys.argv) != 5):
    print "Give four arguments:"
    print "python stats.py <picklename> <benchname> <divsdirname> <resultdirname>"
    exit(0) 

pname,bench,ddir,rdir = tuple(sys.argv[1:])

for f in listdir(ddir):
    if f.endswith("." + bench + ".out.json"):
        try:
            files[f] = json.loads(open(ddir + "/" + f).read())
        except:
            print "Exception in file:", f
            continue


if (len(sys.argv) > 1) and len(files)>0:
    pickle.dump(files, open(rdir + "/" + pname + ".pickle", "w"))



