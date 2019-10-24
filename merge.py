#!/usr/bin/python

from os import listdir

import json

import sys

import pickle
import re

#import subprocess

#import getopt


d = dict()

ds = dict()

i = 0
for f in listdir("."):
    if f.endswith(".pickle") and f.startswith("divs_"):
        ds[i] = pickle.load(open(f))
        i+=1 

print ds.keys()

def checkif(d, b, arch, method, metric, agap, relax, field):
    return d.has_key(b) and d[b].has_key(arch) and d[b][arch].has_key(method) and d[b][arch][method].has_key(metric) and d[b][arch][method][metric].has_key(agap) and d[b][arch][method][metric][agap].has_key(relax) and d[b][arch][method][metric][agap][relax].has_key(field)


for b in ds[0]:
    d[b] = dict()
    for arch in ds[0][b]:
        d[b][arch] = dict()
        for method in ds[0][b][arch]:
            d[b][arch][method] = dict()
            for metric in ds[0][b][arch][method]:
                d[b][arch][method][metric] = dict()
                for agap in ds[0][b][arch][method][metric]:
                    d[b][arch][method][metric][agap] = dict()
                    for relax in ds[0][b][arch][method][metric][agap]:
                        d[b][arch][method][metric][agap][relax] = dict()
                        print b, arch, method, metric, agap, relax
                        # get average of divs
                        num = len(ds.keys())
                        for di in ds:
                            try: 
                                ds[di][b][arch][method][metric][agap][relax]
                            except:
                                num -= 1
                                print "In", di, b, arch, method, metric, agap, relax


                        divs = [ds[di][b][arch][method][metric][agap][relax]['divs'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, relax, 'divs')]
                        d[b][arch][method][metric][agap][relax]['divs'] = sum(divs)/len(divs)

                        cost = [ds[di][b][arch][method][metric][agap][relax]['cost']['num'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, relax, 'cost')]
                        d[b][arch][method][metric][agap][relax]['cost'] = { 'num': sum(cost)/len(cost), 'maxnum': 0}

                        stime = [ds[di][b][arch][method][metric][agap][relax]['stime']['num'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, relax, 'stime')]
                        d[b][arch][method][metric][agap][relax]['stime'] = { 'num': sum(stime)/len(stime), 'maxnum': 0}

                        
                        hamm = [ds[di][b][arch][method][metric][agap][relax]['avg']['num'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, relax, 'avg')]
                        mhamm = [ds[di][b][arch][method][metric][agap][relax]['avg']['maxnum'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, relax, 'avg')]
                        dhamm = [i for di in ds if checkif(ds[di], b, arch, method, metric, agap, relax, 'avg') for i in ds[di][b][arch][method][metric][agap][relax]['avg']['data'] ]
                        if len(hamm)>0 and len(mhamm) > 0:
                            d[b][arch][method][metric][agap][relax]['avg'] = { 'num': sum(hamm)/len(hamm), 'maxnum': sum(mhamm)/len(mhamm), 'data' : dhamm}

                        brhamm = [ds[di][b][arch][method][metric][agap][relax]['bravg']['num'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, relax, 'bravg')]
                        mbrhamm = [ds[di][b][arch][method][metric][agap][relax]['bravg']['maxnum'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, relax, 'bravg')]
                        dbrhamm = [i for di in ds   if checkif(ds[di], b, arch, method, metric, agap, relax, 'bravg') for i in ds[di][b][arch][method][metric][agap][relax]['bravg']['data']]
                        if len(brhamm)>0 and len(mbrhamm) > 0:
                            d[b][arch][method][metric][agap][relax]['bravg'] = { 'num': sum(brhamm)/len(brhamm), 'maxnum': sum(mbrhamm)/len(mbrhamm), 'data' : dbrhamm}


                        brdiff = [ds[di][b][arch][method][metric][agap][relax]['brdiff']['num'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, relax, 'brdiff')]
                        mbrdiff = [ds[di][b][arch][method][metric][agap][relax]['brdiff']['maxnum'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, relax, 'brdiff')]
                        dbrdiff = [i for di in ds if checkif(ds[di], b, arch, method, metric, agap, relax,'brdiff') for i in ds[di][b][arch][method][metric][agap][relax]['brdiff']['data'] ]

                        if len(brdiff)>0 and len(mbrdiff) > 0:
                            d[b][arch][method][metric][agap][relax]['brdiff'] = { 'num': sum(brdiff)/len(brdiff), 'maxnum': sum(mbrdiff)/len(mbrdiff), 'data' : dbrdiff}

                        d[b][arch][method][metric][agap][relax]['num'] = num # number of iterations

pickle.dump(d, open("divs.pickle", "w"))

