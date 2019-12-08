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

                            
                            hamm = [ds[di][b][arch][method][metric][agap][branch][relax]['avg']['num'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'avg')]
                            mhamm = [ds[di][b][arch][method][metric][agap][branch][relax]['avg']['maxnum'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'avg')]
                            dhamm = [i for di in ds if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'avg') for i in ds[di][b][arch][method][metric][agap][branch][relax]['avg']['data'] ]
                            if len(hamm)>0 and len(mhamm) > 0:
                                av = avg(hamm)
                                std = stdev(hamm, av)
                                mn = avg(hamm)
                                n = len(hamm)
                                d[b][arch][method][metric][agap][branch][relax]['avg'] = { 'num': av, 'stdev': std, 'n': n, 'maxnum': mn, 'data' : dhamm}

                            brhamm = [ds[di][b][arch][method][metric][agap][branch][relax]['bravg']['num'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'bravg')]
                            mbrhamm = [ds[di][b][arch][method][metric][agap][branch][relax]['bravg']['maxnum'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'bravg')]
                            dbrhamm = [i for di in ds   if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'bravg') for i in ds[di][b][arch][method][metric][agap][branch][relax]['bravg']['data']]
                            if len(brhamm)>0 and len(mbrhamm) > 0:
                                av = avg(brhamm)
                                std = stdev(brhamm, av)
                                mn = avg(mbrhamm)
                                n = len(brhamm)
     
                                d[b][arch][method][metric][agap][branch][relax]['bravg'] = { 'num': av, 'stdev': std, 'n': n, 'maxnum': mn, 'data' : dbrhamm}


                            brdiff = [ds[di][b][arch][method][metric][agap][branch][relax]['brdiff']['num'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'brdiff')]
                            mbrdiff = [ds[di][b][arch][method][metric][agap][branch][relax]['brdiff']['maxnum'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'brdiff')]
                            dbrdiff = [i for di in ds if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'brdiff') for i in ds[di][b][arch][method][metric][agap][branch][relax]['brdiff']['data'] ]

                            if len(brdiff)>0 and len(mbrdiff) > 0:
                                av = avg(brdiff)
                                std = stdev(brdiff, av)
                                mn = avg(mbrdiff)
                                n = len(brdiff)
                                d[b][arch][method][metric][agap][branch][relax]['brdiff'] = { 'num': av, 'stdev': std, 'n': n, 'maxnum': mn, 'data' : dbrdiff}



                            lev = [ds[di][b][arch][method][metric][agap][branch][relax]['levenshtein']['num'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'levenshtein')]
                            mlev = [ds[di][b][arch][method][metric][agap][branch][relax]['levenshtein']['maxnum'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'levenshtein')]
                            dlev = [i for di in ds if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'levenshtein') for i in ds[di][b][arch][method][metric][agap][branch][relax]['levenshtein']['data'] ]

                            if len(lev)>0 and len(mlev) > 0:
                                av = avg(lev)
                                std = stdev(lev, av)
                                mn = avg(mlev)
                                n = len(lev)
                                d[b][arch][method][metric][agap][branch][relax]['levenshtein'] = { 'num': av, 'stdev': std, 'n': n, 'maxnum': mn, 'data' : dlev}

                            d[b][arch][method][metric][agap][branch][relax]['num'] = num # number of iterations


pickle.dump(d, open("divs.pickle", "w"))

