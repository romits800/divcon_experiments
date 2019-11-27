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
    print "$ python calculate.py -p <path of the measurments>"
    # print 'test.py -i <inputfile> -o <outputfile>'
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        print "$ python calculate.py -p <path of the measurments>"
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


def reverse_order(c):
        # print c
        # exit(0)
        d = [0 for _ in range(max(c))]
        for i,ci in enumerate(c):
                if (ci == -1):
                        continue
                d[ci-1] = i
        return d


#div_monolithic_lns_mips_gcc.xexit.xexit_10_100_br_hamming_0.8_10000_constant.pickle
for benchmark in listdir(pathname):
    print benchmark
    d[benchmark] = dict()
    pat = re.compile("div_monolithic_([^_]*)_([^_]*)_%s_([0-9]+)_([0-9]+)_([^0-9]*hamming|levenshtein)_([^_]+)(_.*|).pickle"  %benchmark)
    for pfile in listdir(pathname + "/" + benchmark + "/"):
        if pfile.endswith("pickle"):
            try:
                a = re.match(pat,pfile)
                method,arch,agap,divs,metric,branch,rest = a.groups()
            except:
                print "Exception: ", pfile
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
                    print "Exception: ", rest, branch, pfile

            #arch = a.group(2)
            files = pickle.load(open(pathname + "/" +  benchmark + "/" + pfile))
            files = {h:files[h] for h in files if benchmark in h}
            # cycles = {h:files[h]['cycles'] for h in files if files[h].has_key('cycles')}
            #####################
            precycles = {h:[ (c,j) for  c,j  in zip(files[h]['global_cycles'],files[h]['type']) if j in [0,1,2,3,4,14]] for h in files if files[h].has_key('type') and files[h].has_key('global_cycles')}
            cycles = {h: [c for c,j in precycles[h]] for h in precycles}
            prebrcycles = {h:[ (i,c) for  i,(c,j)  in enumerate(precycles[h]) if j in [1,2,3]] for h in precycles}

            doublebrcycles = {h:{j:(prebrcycles[h][j-1][0] if j>0 else 0)  for  j,(i,c)  in enumerate(prebrcycles[h]) } for h in prebrcycles}

            brcycles = {h:[ c for  i,c  in prebrcycles[h]] for h in prebrcycles}
            #####################
            
            solver_times = {h:files[h]['solver_time'] for h in files if files[h].has_key('solver_time')}
            levcycles = {h:reverse_order(cycles[h]) for h in cycles }
            stime = max([ files[h]['solver_time'] for h in files if files[h].has_key('solver_time') ])/1000. # the maximum should be the last
            cost = [files[h]['cost'][0] for h in files if files[h].has_key('cost')]# the cost
            
            avgcost = 0
            if len(cost) > 0:
                avgcost = sum(cost)/(len(cost))
            fnames_sorted = sorted([fi for fi in cycles.keys() if fi.split(".")[0].isdigit()], key=lambda x: int(x.split(".")[0]))


	    if not d[benchmark].has_key(arch):
                d[benchmark][arch] = dict()
            if not d[benchmark][arch].has_key(method):
                d[benchmark][arch][method] = dict() #{relax: {'avg': { 'num':round(sumhd/count,2),'maxnum': maxnum, 'data': intd.values()}, 'divs':len(fnames), 'cost': { 'num': avgcost, 'maxnum': 0}, 'stime': { 'num': stime, 'maxnum': 60*5.}}}
            if not d[benchmark][arch][method].has_key(metric):
                d[benchmark][arch][method][metric] = dict()
            if not d[benchmark][arch][method][metric].has_key(agap):
                d[benchmark][arch][method][metric][agap] = dict()
            if not d[benchmark][arch][method][metric][agap].has_key(branch):
                d[benchmark][arch][method][metric][agap][branch] = dict()
            if not d[benchmark][arch][method][metric][agap][branch].has_key(relax):
                d[benchmark][arch][method][metric][agap][branch][relax] = dict()
 
            d[benchmark][arch][method][metric][agap][branch][relax]['divs'] = len(fnames_sorted)
            d[benchmark][arch][method][metric][agap][branch][relax]['cost'] = { 'num': avgcost, 'maxnum': 0}
            d[benchmark][arch][method][metric][agap][branch][relax]['stime'] = { 'num': stime, 'maxnum': 0}


            ## Hamming Distance
            d[benchmark][arch][method][metric][agap][branch][relax]['avg'] = dict()
            for ii in range(2,len(fnames_sorted)):
                intd = dict()
                sumhd = 0
                count = 0
                maxnum = 0
                fnames = fnames_sorted[:ii]

                stime = solver_times[fnames[-1]]

                for i in range(len(fnames)):
                    for j in range(i+1, len(fnames)):
                       f1,f2 = fnames[i],fnames[j]
                       intd[(f1,f2)] = sum([ (1. if k!=l else 0.) for (k,l) in zip(cycles[f1],cycles[f2])] ) #zip(files[f1],files[f2])
                       sumhd += intd[(f1,f2)]
                       count += 1.
                    maxnum = len(cycles[fnames[i]])

                if not count == 0:
                    d[benchmark][arch][method][metric][agap][branch][relax]['avg'][ii] = { 'num': round(sumhd/count,2), 'maxnum': maxnum, 'data': intd.values(), 'stime': stime }

            ## Branch Hamming Distance
            d[benchmark][arch][method][metric][agap][branch][relax]['bravg'] = dict()

            for ii in range(2,len(fnames_sorted)):
                intd = dict()
                sumhd = 0
                count = 0
                maxnum = 0
                fnames = fnames_sorted[:ii]
                stime = solver_times[fnames[-1]]
                for i in range(len(fnames)):
                    for j in range(i+1, len(fnames)):
                        f1,f2 = fnames[i],fnames[j]
                        intd[(f1,f2)] = sum([ (1. if k!=l else 0.) for (k,l) in zip(brcycles[f1],brcycles[f2])] ) #zip(files[f1],files[f2])
                        sumhd += intd[(f1,f2)]
                        count += 1.
                    maxnum = len(brcycles[fnames[i]])

                if not count == 0:
                    d[benchmark][arch][method][metric][agap][branch][relax]['bravg'][ii] = {'num': round(sumhd/count,4), 'maxnum': maxnum, 'data': intd.values(), 'stime': stime}


            ## Branch Diff Hamming Distance
	    d[benchmark][arch][method][metric][agap][branch][relax]['brdiff'] = dict()

            for ii in range(2,len(fnames_sorted)):
                intd = dict()
                sumhd = 0
                count = 0
                maxnum = 0
                fnames = fnames_sorted[:ii]
                stime = solver_times[fnames[-1]]
                for i in range(len(fnames)):
                    for j in range(i+1, len(fnames)):
                        f1,f2 = fnames[i],fnames[j]

                        brcycles1 = [c-cc for jj,(iii,cc) in enumerate(prebrcycles[f1]) for c in cycles[f1][doublebrcycles[f1][jj]:iii-1] ] 
                        brcycles2 = [c-cc for jj,(iii,cc) in enumerate(prebrcycles[f2]) for c in cycles[f2][doublebrcycles[f1][jj]:iii-1] ] 
                    #

                        intd[(f1,f2)] = sum([ (1. if k!=l else 0.) for (k,l) in zip(brcycles1,brcycles2)] ) #zip(files[f1],files[f2])
                        sumhd += intd[(f1,f2)]
                        count += 1.
                        maxnum = len(brcycles1)


                if not count == 0:
                    d[benchmark][arch][method][metric][agap][branch][relax]['brdiff'][ii] = {'num': round(sumhd/count,2), 'maxnum': maxnum, 'data': intd.values(), 'stime': stime} 

            ## Levenshtein Distance
            d[benchmark][arch][method][metric][agap][branch][relax]['levenshtein'] = dict()
            for ii in range(2,len(fnames_sorted)):
                intd = dict()
                sumhd = 0
                count = 0
                maxnum = 0
                fnames = fnames_sorted[:ii]
                stime = solver_times[fnames[-1]]
                for i in range(len(fnames)):
                    for j in range(i+1, len(fnames)):
                        f1,f2 = fnames[i],fnames[j]

                        intd[(f1,f2)] = levenshtein_distance(levcycles[f1], levcycles[f2])
                        sumhd += intd[(f1,f2)]
                        count += 1.
                        maxnum = len(levcycles[fnames[i]])


                if not count == 0:
                    d[benchmark][arch][method][metric][agap][branch][relax]['levenshtein'][ii] = {'num': round(sumhd/count,2), 'maxnum': maxnum, 'data': intd.values(), 'stime': stime}


newpath = pathname.strip("/")
print newpath
initial = "/" if pathname.startswith("/") else ""
pickle.dump(d, open(initial + newpath + ".pickle","w"))


