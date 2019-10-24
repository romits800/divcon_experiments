#!/usr/bin/python

from os import listdir

import json

import sys

import pickle
import re

import subprocess

import getopt


def improvement(lns, dfs):
    if (lns >= dfs):
        return round((float) ((lns-dfs)/dfs)*100,2)
    else:
        return -round((float) ((dfs-lns)/lns)*100,2)


pathname = "divs/"   # sys.argv[1]
s_metric = "hamming" # sys.argv[2]
s_agap = "10"        # sys.argv[3]         #
s_constant = "10000" # sys.argv[4]
s_relax = "0.8"      # sys.argv[5]
s_out = "hamming"



try:
    opts, args = getopt.getopt(sys.argv[1:],"hp:",["pathname="])
except getopt.GetoptError:
    print "$ python onlyham_test.py -p <path of the measurments>"
    # print 'test.py -i <inputfile> -o <outputfile>'
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        print "$ python onlyham_test.py -p <path of the measurments>"
        sys.exit()
    elif opt in ("-p", "--pathname"):
        pathname = arg
        print "path", opt, arg
    else:
        print "Not correct", opt

d = dict()

# if (len(sys.argv)!=6):
#     print "Give four arguments: $python onlyham_test.py <path of the measurments> <metric> <acceptable gap> <restart constant> <relax>"
#     exit(0)



#div_monolithic_lns_mips_gcc.xexit.xexit_10_100_br_hamming_0.8_10000_constant.pickle
for benchmark in listdir(pathname):
    d[benchmark] = dict()
    pat = re.compile("div_monolithic_([^_]*)_([^_]*)_%s_([0-9]+)_([0-9]+)_([^0-9]+)(_.*|).pickle"  %benchmark)
    for pfile in listdir(pathname + "/" + benchmark + "/"):
        if pfile.endswith("pickle"):
            try:
                a = re.match(pat,pfile)
                method,arch,agap,divs,metric,rest = a.groups()
            except:
                continue
            #if metric != s_metric  or agap != s_agap :
            #    continue
            relax = None
            constant = None
            # restart = None
            if method == "lns":
                try:
                    pat2 = re.compile("_(0.[0-9]+)_([0-9]+)_(.*)")
                    a = re.match(pat2,rest)
                    relax, constant, restart = a.groups() 
                    #if constant != s_constant:
                    #    continue
                except:
                    print "Exception: ", rest

            #arch = a.group(2)
            files = pickle.load(open(pathname + "/" +  benchmark + "/" + pfile))
            files = {h:files[h] for h in files if benchmark in h}
            # cycles = {h:files[h]['cycles'] for h in files if files[h].has_key('cycles')}
            brcycles = {h:[ c for  c,j  in zip(files[h]['cycles'],files[h]['type']) if j in [1,2,3]] for h in files if files[h].has_key('type') and files[h].has_key('cycles')}
            cycles = {h:[ c for  c,j  in zip(files[h]['cycles'],files[h]['type']) if j in [0,1,2,3,4,14]] for h in files if files[h].has_key('type') and files[h].has_key('cycles')}
            stime = max([ files[h]['solver_time'] for h in files if files[h].has_key('solver_time') ])/1000. # the maximum should be the last
            cost = [files[h]['cost'][0] for h in files if files[h].has_key('cost')]# the cost
            
            avgcost = 0
            if len(cost) > 0:
                avgcost = sum(cost)/(len(cost))
            fnames = [ fi for fi in cycles.keys() if fi.split(".")[0].isdigit()]


	    if not d[benchmark].has_key(arch):
                    d[benchmark][arch] = dict()
            if not d[benchmark][arch].has_key(method):
                    d[benchmark][arch][method] = dict() #{relax: {'avg': { 'num':round(sumhd/count,2),'maxnum': maxnum, 'data': intd.values()}, 'divs':len(fnames), 'cost': { 'num': avgcost, 'maxnum': 0}, 'stime': { 'num': stime, 'maxnum': 60*5.}}}
            if not d[benchmark][arch][method].has_key(metric):
                   d[benchmark][arch][method][metric] = dict()
            if not d[benchmark][arch][method][metric].has_key(agap):
                   d[benchmark][arch][method][metric][agap] = dict()
            if not d[benchmark][arch][method][metric][agap].has_key(relax):
                    d[benchmark][arch][method][metric][agap][relax] = dict()
 
            d[benchmark][arch][method][metric][agap][relax]['divs'] = len(fnames)
            d[benchmark][arch][method][metric][agap][relax]['cost'] = { 'num': avgcost, 'maxnum': 0}
            d[benchmark][arch][method][metric][agap][relax]['stime'] = { 'num': stime, 'maxnum': 0}


            ## Hamming Distance
            intd = dict()
            sumhd = 0
            count = 0
            maxnum = 0

            for i in range(len(fnames)):
                for j in range(i+1, len(fnames)):
                   f1,f2 = fnames[i],fnames[j]
                   intd[(f1,f2)] = sum([ (1. if k!=l else 0.) for (k,l) in zip(cycles[f1],cycles[f2])] ) #zip(files[f1],files[f2])
                   sumhd += intd[(f1,f2)]
                   count += 1.
                maxnum = len(cycles[fnames[i]])

            if not count == 0:
                d[benchmark][arch][method][metric][agap][relax]['avg'] = { 'num':round(sumhd/count,2),'maxnum': maxnum, 'data': intd.values()}

            ## Branch Hamming Distance
            intd = dict()
            sumhd = 0
            count = 0
            maxnum = 0
            for i in range(len(fnames)):
                for j in range(i+1, len(fnames)):
                    f1,f2 = fnames[i],fnames[j]
                    intd[(f1,f2)] = sum([ (1. if k!=l else 0.) for (k,l) in zip(brcycles[f1],brcycles[f2])] ) #zip(files[f1],files[f2])
                    sumhd += intd[(f1,f2)]
                    count += 1.
                maxnum = len(brcycles[fnames[i]])

            if not count == 0:
             	d[benchmark][arch][method][metric][agap][relax]['bravg'] = {'num': round(sumhd/count,4), 'maxnum': maxnum, 'data': intd.values()}


            ## Branch Diff Hamming Distance
            intd = dict()
            sumhd = 0
            count = 0
            maxnum = 0
            for i in range(len(fnames)):
                for j in range(i+1, len(fnames)):
                    f1,f2 = fnames[i],fnames[j]
                    brcycles1 = [c-cc for c in cycles[f1] for cc in brcycles[f1]] # '1' means branch
                    brcycles2 = [c-cc for c in cycles[f2] for cc in brcycles[f2]] # '1' means branch

                    intd[(f1,f2)] = sum([ (1. if k!=l else 0.) for (k,l) in zip(brcycles1,brcycles2)] ) #zip(files[f1],files[f2])
                    sumhd += intd[(f1,f2)]
                    count += 1.
                    maxnum = len(brcycles1)


            if not count == 0:
		d[benchmark][arch][method][metric][agap][relax][brdiff] = {'num': round(sumhd/count,2), 'maxnum': maxnum, 'data': intd.values()} 


newpath = pathname.strip("/")
initial = "/" if pathname.startswith("/") else ""
pickle.dump(d, open(initial + newpath + ".pickle","w"))


