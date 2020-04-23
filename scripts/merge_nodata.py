#!/usr/bin/python

from os import listdir, path
import json

import sys

import pickle
import re

import math
#import subprocess

import getopt

min_num_seeds = 5

d = dict()

ds = dict()

pathname = "."
savepath = "."
name = ""

try:
    opts, args = getopt.getopt(sys.argv[1:],"hp:n:s:",["pathname=", "name=", "savepath="])
except getopt.GetoptError:
    print "$ python merge_nodata.py -p <path of the measurments> -n <sufix of the pickle files>"
    # print 'test.py -i <inputfile> -o <outputfile>'
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        print "$ python calculate.py -p <path of the measurments> -n <sufix of the pickle files>"
        sys.exit()
    elif opt in ("-p", "--pathname"):
        pathname = arg
        print "path", opt, arg
    elif opt in ("-n", "--name"):
	name = arg
    elif opt in ("-s", "--savepath"):
	savepath = arg
    else:
        print "Not correct", opt



i = 0
for f in listdir(pathname):
    if f.endswith(".pickle") and f.startswith(name):
        ds[i] = pickle.load(open(f))
        i+=1 

print ds.keys()

def checkif(d, b, arch, method, metric, agap, branch, relax, mindist, field):
    return d.has_key(b) and d[b].has_key(arch) and d[b][arch].has_key(method) and d[b][arch][method].has_key(metric) and d[b][arch][method][metric].has_key(agap) and d[b][arch][method][metric][agap].has_key(branch) and d[b][arch][method][metric][agap][branch].has_key(relax) and d[b][arch][method][metric][agap][branch][relax].has_key(mindist) and d[b][arch][method][metric][agap][branch][relax][mindist].has_key(field)


def avg(l):
    if len(l)!=0:
        return sum(l)/len(l)
    else: 
        return -1

def stdev(l,av):
    sl = [(i-av)**2 for i in l]
    if len(sl)>1:
        return math.sqrt(sum(sl)/(len(sl)-1))
    else: 
        return 0

def create_dicts(ds, b, arch, method, metric, agap, branch, relax, mindist, field):
  hamm = dict()
  mhamm = dict()
  dhamm = dict()
  stime = dict()
  for di in ds:
      if checkif(ds[di], b, arch, method, metric, agap, branch, relax, mindist, field):
          if field == 'cost':
                print ds[di][b][arch][method][metric][agap][branch][relax][mindist][field]
 
          for i in ds[di][b][arch][method][metric][agap][branch][relax][mindist][field]:
              val = ds[di][b][arch][method][metric][agap][branch][relax][mindist][field][i]['num']
              mval = ds[di][b][arch][method][metric][agap][branch][relax][mindist][field][i]['maxnum']
              stval = ds[di][b][arch][method][metric][agap][branch][relax][mindist][field][i]['stime']
              #dval = [da for da in ds[di][b][arch][method][metric][agap][branch][relax]['avg'][i]['data'] ]
              if hamm.has_key(i):
                  hamm[i].append(val)
              else:
                  hamm[i] = [val]
              if mhamm.has_key(i):
                  mhamm[i].append(mval)
              else:
                  mhamm[i] = [mval]
              # if dhamm.has_key(i):
              #     dhamm[i].extend(dval)
              # else:
              #     dhamm[i] = dval
              if stime.has_key(i):
                  stime[i].append(stval)
              else:
                  stime[i] = [stval]
  return (hamm, mhamm, dhamm, stime)



benchmarks = {b for i in ds for b in ds[i]} 
arches = {arch for i in ds for b in ds[i] for arch in ds[i][b]} 
methods = {method for i in ds for b in ds[i] for arch in ds[i][b] for method in ds[i][b][arch]} 
metrics = {metric for i in ds for b in ds[i] for arch in ds[i][b] for method in ds[i][b][arch] for metric in ds[i][b][arch][method]} 
agaps = {agap for i in ds for b in ds[i] for arch in ds[i][b] for method in ds[i][b][arch] for metric in ds[i][b][arch][method] for agap in ds[i][b][arch][method][metric]} 
branches = {branch for i in ds for b in ds[i] for arch in ds[i][b] for method in ds[i][b][arch] for metric in ds[i][b][arch][method] for agap in ds[i][b][arch][method][metric] for branch in ds[i][b][arch][method][metric][agap]} 
rrates = {relax for i in ds for b in ds[i] for arch in ds[i][b] for method in ds[i][b][arch] for metric in ds[i][b][arch][method] for agap in ds[i][b][arch][method][metric] for branch in ds[i][b][arch][method][metric][agap] for relax in ds[i][b][arch][method][metric][agap][branch]} 
dists = {mdist for i in ds for b in ds[i] for arch in ds[i][b] for method in ds[i][b][arch] for metric in ds[i][b][arch][method] for agap in ds[i][b][arch][method][metric] for branch in ds[i][b][arch][method][metric][agap] for relax in ds[i][b][arch][method][metric][agap][branch] for mdist in ds[i][b][arch][method][metric][agap][branch][relax]} 

for b in benchmarks:
    d[b] = dict()
    for arch in arches:
        d[b][arch] = dict()
        for method in methods:
            d[b][arch][method] = dict()
            for metric in metrics:
                d[b][arch][method][metric] = dict()
                for agap in agaps:
                    d[b][arch][method][metric][agap] = dict()
                    for branch in branches:
                        d[b][arch][method][metric][agap][branch] = dict()
                        for relax in rrates:
                          d[b][arch][method][metric][agap][branch][relax] = dict()
                          for mindist in dists:  
                            d[b][arch][method][metric][agap][branch][relax][mindist] = dict()
                            print b, arch, method, metric, agap, branch, relax, mindist
                        # get average of divs
                            num = len(ds.keys())
                            for di in ds:
                                try: 
                                    ds[di][b][arch][method][metric][agap][branch][relax][mindist]
                                except:
                                    num -= 1
                                    print "In", di, b, arch, method, metric, agap, branch, relax, mindist

                            if (num==0): continue
                                

                            divs = [ds[di][b][arch][method][metric][agap][branch][relax][mindist]['divs'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, branch, relax, mindist, 'divs')]
                            if (len(divs) == 0): continue
                            d[b][arch][method][metric][agap][branch][relax][mindist]['divs'] = sum(divs)/len(divs)

                            # cost = [ds[di][b][arch][method][metric][agap][branch][relax]['cost']['num'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'cost')]
                            #av = avg(cost)
                            #std = stdev(cost, av)
                            #n = len(cost)
                            #d[b][arch][method][metric][agap][branch][relax]['cost'] = { 'num': av, 'stdev': std, 'n': n, 'maxnum': 0}


#                            (stime, _, _) = create_dicts(ds, b, arch, method, metric, agap, branch, relax, 'stime')
#                            stime = [ds[di][b][arch][method][metric][agap][branch][relax]['stime']['num'] for di in ds if checkif(ds[di], b, arch, method, metric, agap, branch, relax, 'stime')]
#                            if len(stime)>0:
#                                av = {i: avg(stime[i]) for i in stime}
#                                std = {i: stdev(stime[i], av[i]) for i in stime}
#                                n = {i: len(stime[i]) for i in hamm}
#                                d[b][arch][method][metric][agap][branch][relax]['stime'] = {i: { 'num': av[i], 'stdev': std[i], 'n': n[i], 'maxnum': 0} for i in stime}

                            
                            (cost, _, _, stime) = create_dicts(ds, b, arch, method, metric, agap, branch, relax, mindist, 'cost')


                            if len(cost)>0:
                                av = {i: avg(cost[i]) for i in cost}
                                std = {i: stdev(cost[i], av[i]) for i in cost}
                                n = {i: len(cost[i]) for i in cost}
                                m = {i: 0 for i in cost}
                                #d = {i: [] for i in cost}
                                st = {i: 0 for i in stime}
                                d[b][arch][method][metric][agap][branch][relax][mindist]['cost'] = {i: { 'num': av[i], 'stdev': std[i], 'n': n[i], 'maxnum': m[i],  'stime': st} for i in cost if n[i] >= min_num_seeds}

 
                            
                            (hamm, mhamm, dhamm, stime) = create_dicts(ds, b, arch, method, metric, agap, branch, relax, mindist, 'avg')


                            if len(hamm)>0 and len(mhamm) > 0:
                                av = {i: avg(hamm[i]) for i in hamm}
                                std = {i: stdev(hamm[i], av[i]) for i in hamm}
                                mn = {i: avg(mhamm[i]) for i in mhamm}
                                n = {i: len(hamm[i]) for i in hamm}
                                st = {i: avg(stime[i]) for i in stime}
                                ststd = {i: stdev(stime[i],st[i]) for i in stime}
                                d[b][arch][method][metric][agap][branch][relax][mindist]['avg'] = {i: { 'num': av[i], 'stdev': std[i], 'n': n[i], 'maxnum': mn[i],  'stime': st[i], 'stime_stdev': ststd[i]} for i in hamm if n[i] >= min_num_seeds}

                            (brhamm, mbrhamm, dbrhamm, stime) = create_dicts(ds, b, arch, method, metric, agap, branch, relax, mindist, 'bravg')


                            if len(brhamm)>0 and len(mbrhamm) > 0:
                                av = {i: avg(brhamm[i]) for i in brhamm}
                                std = {i: stdev(brhamm[i], av[i]) for i in brhamm}
                                mn = {i: avg(mbrhamm[i]) for i in mbrhamm}
                                n = {i: len(brhamm[i]) for i in brhamm}
                                st = {i: avg(stime[i]) for i in stime}
                                ststd = {i: stdev(stime[i],st[i]) for i in stime}
                                d[b][arch][method][metric][agap][branch][relax][mindist]['bravg'] = {i: { 'num': av[i], 'stdev': std[i], 'n': n[i], 'maxnum': mn[i],  'stime': st[i], 'stime_stdev': ststd[i] } for i in brhamm if n[i] >= min_num_seeds}


                            (brdiff, mbrdiff, dbrdiff, stime) = create_dicts(ds, b, arch, method, metric, agap, branch, relax, mindist, 'brdiff')

                            if len(brdiff)>0 and len(mbrdiff) > 0:
                                av = {i: avg(brdiff[i]) for i in brdiff}
                                std = {i: stdev(brdiff[i], av[i]) for i in brdiff}
                                mn = {i: avg(mbrdiff[i]) for i in mbrdiff}
                                n = {i: len(brdiff[i]) for i in brdiff}
                                st = {i: avg(stime[i]) for i in stime}
                                ststd = {i: stdev(stime[i],st[i]) for i in stime}
                                d[b][arch][method][metric][agap][branch][relax][mindist]['brdiff'] = {i: { 'num': av[i], 'stdev': std[i], 'n': n[i], 'maxnum': mn[i],  'stime': st[i], 'stime_stdev': ststd[i]} for i in brdiff if n[i] >= min_num_seeds}


                            (levenshtein, mlevenshtein, dlevenshtein, stime) = create_dicts(ds, b, arch, method, metric, agap, branch, relax, mindist, 'levenshtein')

                            if len(levenshtein)>0 and len(mlevenshtein) > 0:
                                av = {i: avg(levenshtein[i]) for i in levenshtein}
                                std = {i: stdev(levenshtein[i], av[i]) for i in levenshtein}
                                mn = {i: avg(mlevenshtein[i]) for i in mlevenshtein}
                                n = {i: len(levenshtein[i]) for i in levenshtein}
                                st = {i: avg(stime[i]) for i in stime}
                                ststd = {i: stdev(stime[i],st[i]) for i in stime}
                                d[b][arch][method][metric][agap][branch][relax][mindist]['levenshtein'] = {i: { 'num': av[i], 'stdev': std[i], 'n': n[i], 'maxnum': mn[i],  'stime': st[i] , 'stime_stdev': ststd[i]} for i in levenshtein if n[i] >= min_num_seeds}


                            d[b][arch][method][metric][agap][branch][relax][mindist]['num'] = num # number of iterations

                            (reghamm, mreghamm, dreghamm, stime) = create_dicts(ds, b, arch, method, metric, agap, branch, relax, mindist, 'reghamm')

                            if len(reghamm)>0 and len(mreghamm) > 0:
                                av = {i: avg(reghamm[i]) for i in reghamm}
                                std = {i: stdev(reghamm[i], av[i]) for i in reghamm}
                                mn = {i: avg(mreghamm[i]) for i in mreghamm}
                                n = {i: len(reghamm[i]) for i in reghamm}
                                st = {i: avg(stime[i]) for i in stime}
                                ststd = {i: stdev(stime[i],st[i]) for i in stime}
                                d[b][arch][method][metric][agap][branch][relax][mindist]['reghamm'] = {i: { 'num': av[i], 'stdev': std[i], 'n': n[i], 'maxnum': mn[i],  'stime': st[i], 'stime_stdev': ststd[i]} for i in reghamm if n[i] >= min_num_seeds}



pickle.dump(d, open(path.join(savepath, name + "_divs.pickle"), "w"))

