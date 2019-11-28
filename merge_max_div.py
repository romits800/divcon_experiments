#!/usr/bin/python

from os import listdir

import json

import sys

import pickle
import re

import math
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

def checkif(d, b, arch, method, metric, agap, branch, relax, field):
    return d.has_key(b) and d[b].has_key(arch) and d[b][arch].has_key(method) and d[b][arch][method].has_key(metric) and d[b][arch][method][metric].has_key(agap) and d[b][arch][method][metric][agap].has_key(branch) and d[b][arch][method][metric][agap][branch].has_key(relax) and d[b][arch][method][metric][agap][branch][relax].has_key(field)


def avg(l):
    if len(l)!=0:
        return sum(l)/len(l)
    else: 
        return -1

def stdev(l,av):
    sl = [(i-av)**2 for i in l]
    if len(sl)!=0:
        return math.sqrt(sum(sl)/len(sl))
    else: 
        return -1


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
                    for branch in ds[0][b][arch][method][metric][agap]:
                        d[b][arch][method][metric][agap][branch] = dict()
                        for relax in ds[0][b][arch][method][metric][agap][branch]:
                            d[b][arch][method][metric][agap][branch][relax] = dict()
                            print b, arch, method, metric, agap, branch, relax
                        # get average of divs
                            num = len(ds.keys())
                            for di in ds:
                                try: 
                                    ds[di][b][arch][method][metric][agap][branch][relax]
                                except:
                                    num -= 1
                                    print "In", di, b, arch, method, metric, agap, branch, relax


                            divs = [ds[di][b][arch][method][metric][agap][branch][relax]['divs'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'divs')]
                            d[b][arch][method][metric][agap][branch][relax]['divs'] = sum(divs)/len(divs)

                            cost = [ds[di][b][arch][method][metric][agap][branch][relax]['cost']['num'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'cost')]
                            av = avg(cost)
                            std = stdev(cost, av)
                            n = len(cost)
                            d[b][arch][method][metric][agap][branch][relax]['cost'] = { 'num': av, 'stdev': std, 'n': n, 'maxnum': 0}

                            stime = [ds[di][b][arch][method][metric][agap][branch][relax]['stime']['num'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'stime')]
                            av = avg(stime)
                            std = stdev(stime, av)
                            n = len(stime)
                            d[b][arch][method][metric][agap][branch][relax]['stime'] = { 'num': av, 'stdev': std, 'n': n, 'maxnum': 0}

                            
                            hamm = {i: [ds[di][b][arch][method][metric][agap][branch][relax]['avg'][i]['num'] for di in ds ] for i in ds[di][b][arch][method][metric][agap][branch][relax]['avg'] if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'avg')}

                            mhamm = {i: [ds[di][b][arch][method][metric][agap][branch][relax]['avg'][i]['maxnum'] for di in ds] for i in  ds[di][b][arch][method][metric][agap][branch][relax]['avg'] if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'avg')}

                            dhamm = {i: [da for di in ds for da in ds[di][b][arch][method][metric][agap][branch][relax]['avg'][i]['data'] ] for i in ds[di][b][arch][method][metric][agap][branch][relax]['avg'] if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'avg') }

                            if len(hamm)>0 and len(mhamm) > 0:
                                av = {i: avg(hamm[i]) for i in hamm}
                                std = {i: stdev(hamm[i], av[i]) for i in hamm}
                                mn = {i: avg(mhamm[i]) for i in mhamm}
                                n = {i: len(hamm[i]) for i in hamm}
                                d[b][arch][method][metric][agap][branch][relax]['avg'] = {i: { 'num': av[i], 'stdev': std[i], 'n': n[i], 'maxnum': mn[i], 'data' : dhamm[i] } for i in hamm}

                            brhamm = {i: [ds[di][b][arch][method][metric][agap][branch][relax]['bravg'][i]['num'] for di in ds ] for i in ds[di][b][arch][method][metric][agap][branch][relax]['bravg'] if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'bravg')}

                            mbrhamm = {i: [ds[di][b][arch][method][metric][agap][branch][relax]['bravg'][i]['maxnum'] for di in ds] for i in  ds[di][b][arch][method][metric][agap][branch][relax]['bravg'] if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'bravg')}

                            dbrhamm = {i: [da for di in ds for da in ds[di][b][arch][method][metric][agap][branch][relax]['bravg'][i]['data'] ] for i in ds[di][b][arch][method][metric][agap][branch][relax]['bravg'] if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'bravg') }

                            if len(brhamm)>0 and len(mbrhamm) > 0:
                                av = {i: avg(brhamm[i]) for i in brhamm}
                                std = {i: stdev(brhamm[i], av[i]) for i in brhamm}
                                mn = {i: avg(mbrhamm[i]) for i in mbrhamm}
                                n = {i: len(brhamm[i]) for i in brhamm}
                                d[b][arch][method][metric][agap][branch][relax]['bravg'] = {i: { 'num': av[i], 'stdev': std[i], 'n': n[i], 'maxnum': mn[i], 'data' : dbrhamm[i] } for i in brhamm}


                            brdiff = {i: [ds[di][b][arch][method][metric][agap][branch][relax]['brdiff'][i]['num'] for di in ds ] for i in ds[di][b][arch][method][metric][agap][branch][relax]['brdiff'] if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'brdiff')}

                            mbrdiff = {i: [ds[di][b][arch][method][metric][agap][branch][relax]['brdiff'][i]['maxnum'] for di in ds] for i in  ds[di][b][arch][method][metric][agap][branch][relax]['brdiff'] if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'brdiff')}

                            dbrdiff = {i: [da for di in ds for da in ds[di][b][arch][method][metric][agap][branch][relax]['brdiff'][i]['data'] ] for i in ds[di][b][arch][method][metric][agap][branch][relax]['brdiff'] if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'brdiff') }

                            if len(brdiff)>0 and len(mbrdiff) > 0:
                                av = {i: avg(brdiff[i]) for i in brdiff}
                                std = {i: stdev(brdiff[i], av[i]) for i in brdiff}
                                mn = {i: avg(mbrdiff[i]) for i in mbrdiff}
                                n = {i: len(brdiff[i]) for i in brdiff}
                                d[b][arch][method][metric][agap][branch][relax]['brdiff'] = {i: { 'num': av[i], 'stdev': std[i], 'n': n[i], 'maxnum': mn[i], 'data' : dbrdiff[i] } for i in brdiff}


                            levenshtein = {i: [ds[di][b][arch][method][metric][agap][branch][relax]['levenshtein'][i]['num'] for di in ds ] for i in ds[di][b][arch][method][metric][agap][branch][relax]['levenshtein'] if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'levenshtein')}

                            mlevenshtein = {i: [ds[di][b][arch][method][metric][agap][branch][relax]['levenshtein'][i]['maxnum'] for di in ds] for i in  ds[di][b][arch][method][metric][agap][branch][relax]['levenshtein'] if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'levenshtein')}

                            dlevenshtein = {i: [da for di in ds for da in ds[di][b][arch][method][metric][agap][branch][relax]['levenshtein'][i]['data'] ] for i in ds[di][b][arch][method][metric][agap][branch][relax]['levenshtein'] if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'levenshtein') }

                            if len(levenshtein)>0 and len(mlevenshtein) > 0:
                                av = {i: avg(levenshtein[i]) for i in levenshtein}
                                std = {i: stdev(levenshtein[i], av[i]) for i in levenshtein}
                                mn = {i: avg(mlevenshtein[i]) for i in mlevenshtein}
                                n = {i: len(levenshtein[i]) for i in levenshtein}
                                d[b][arch][method][metric][agap][branch][relax]['levenshtein'] = {i: { 'num': av[i], 'stdev': std[i], 'n': n[i], 'maxnum': mn[i], 'data' : dlevenshtein[i] } for i in levenshtein}


                            d[b][arch][method][metric][agap][branch][relax]['num'] = num # number of iterations


pickle.dump(d, open("divs.pickle", "w"))

