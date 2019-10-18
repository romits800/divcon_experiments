#!/usr/bin/python

from os import listdir

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

import json

import sys

import pickle
import re

import subprocess

import getopt


def improvement(lns, dfs):
    return round((float) ((lns-dfs)/dfs)*100,2)

def create_tex(texname, ind, field, title, d):
    names = sorted(d.keys())
    with open(texname + '.tex', 'w') as f:
        print >> f, "\\documentclass{standalone}"
        print >> f, "\\usepackage{multirow}"
        print >> f, "\\begin{document}"
        print >> f, "\\begin{tabular}{|l|cc|c|cc|c|}" 
        print >> f, "\\hline" 
        print >> f, "\\multicolumn{7}{|c|}{%s}\\\\" %title.replace("_","")
        print >> f, "\\hline" 
        print >> f, "\\multirow{2}{*}{benchmark}&\\multicolumn{3}{|c|}{mips}&\\multicolumn{3}{|c|}{hexagon}\\\\"
        print >> f, "\\cline{2-7}" 
        print >> f, "&\\footnotesize dfs (%s\\textbackslash maxd (N))&\\footnotesize  lns (%s\\textbackslash maxd (N))&\\footnotesize  improv. \\%% &\\footnotesize dfs (%s\\textbackslash maxd (N))&\\footnotesize lns (%s\\textbackslash maxd (N)) & \\footnotesize improv. \\%% \\\\" %( ind, ind, ind, ind) 
        print >> f, "\\hline" 

        c = dict()
        c["mips"] = dict()
        c["mips"]["dfs"] = {'sum':0.,'count':0.}
        c["mips"]["lns"] = {'sum':0.,'count':0.}
        c["hexagon"] = dict()
        c["hexagon"]["dfs"] = {'sum':0.,'count':0.}
        c["hexagon"]["lns"] = {'sum':0.,'count':0.}

        for benchmark in names:
            mipsdfs = d[benchmark].has_key("mips") and d[benchmark]["mips"].has_key("dfs")
            mipslns = d[benchmark].has_key("mips") and d[benchmark]["mips"].has_key("lns")
            hexagondfs = d[benchmark].has_key("hexagon") and d[benchmark]["hexagon"].has_key("dfs")
            hexagonlns = d[benchmark].has_key("hexagon") and d[benchmark]["hexagon"].has_key("lns")

            arg1 = "-"
            arg2 = "-"
            if mipsdfs: 
                dfsnum = d[benchmark]["mips"]["dfs"][field]['num']
                dfsmaxnum = d[benchmark]["mips"]["dfs"][field]['maxnum']
                dfsdivs = d[benchmark]["mips"]["dfs"]["divs"]
                arg1 = "%.2f\\textbackslash %d (%d)" %(dfsnum, dfsmaxnum, dfsdivs)

                c["mips"]["dfs"]["sum"] += d[benchmark]["mips"]["dfs"][field]['num']
                c["mips"]["dfs"]["count"] += 1
                
            if mipslns: 
                lnsnum = d[benchmark]["mips"]["lns"][field]['num']
                lnsmaxnum = d[benchmark]["mips"]["lns"][field]['maxnum']
                lnsdivs = d[benchmark]["mips"]["lns"]["divs"]
                arg2 = "%.2f\\textbackslash %d (%d)" %(lnsnum, lnsmaxnum, lnsdivs)
                c["mips"]["lns"]["sum"]+= d[benchmark]["mips"]["lns"][field]['num']
                c["mips"]["lns"]["count"] += 1

            impr1 = "-"
            if mipslns and mipsdfs:
                lnsnum = d[benchmark]["mips"]["lns"][field]['num']
                dfsnum = d[benchmark]["mips"]["dfs"][field]['num']
                impr1 = "%.2f" %improvement(lnsnum, dfsnum)

            #arg2 = str(d[benchmark]["mips"]["lns"][field]['num']) + "\\textbackslash " + str(d[benchmark]["mips"]["lns"][field]['maxnum']) + " (" + str(d[benchmark]["mips"]["lns"]["divs"]) + ")" if mipslns and mipsdfs else "-" 

            arg3 = "-"
            arg4 = "-"
            if hexagondfs: 
                dfsnum = d[benchmark]["hexagon"]["dfs"][field]['num']
                dfsmaxnum = d[benchmark]["hexagon"]["dfs"][field]['maxnum']
                dfsdivs = d[benchmark]["hexagon"]["dfs"]["divs"]
                arg3 = "%.2f\\textbackslash %d (%d)" %(dfsnum, dfsmaxnum, dfsdivs)

                c["hexagon"]["dfs"]["sum"] += d[benchmark]["hexagon"]["dfs"][field]['num']
                c["hexagon"]["dfs"]["count"] += 1
                
            if hexagonlns: 
                lnsnum = d[benchmark]["hexagon"]["lns"][field]['num']
                lnsmaxnum = d[benchmark]["hexagon"]["lns"][field]['maxnum']
                lnsdivs = d[benchmark]["hexagon"]["lns"]["divs"]
                arg4 = "%.2f\\textbackslash %d (%d)" %(lnsnum, lnsmaxnum, lnsdivs)
                c["hexagon"]["lns"]["sum"]+= d[benchmark]["hexagon"]["lns"][field]['num']
                c["hexagon"]["lns"]["count"] += 1

            impr2 = "-"
            if hexagonlns and hexagondfs:
                lnsnum = d[benchmark]["hexagon"]["lns"][field]['num']
                dfsnum = d[benchmark]["hexagon"]["dfs"][field]['num']
                impr2 = "%.2f" %improvement(lnsnum, dfsnum)


            print >> f, "%s&%s&%s&%s&%s&%s&%s\\\\"%(benchmark.replace("_","\\_"), arg1, arg2, impr1, arg3, arg4, impr2)


        arg1 = round(c["mips"]["dfs"]["sum"]/c["mips"]["dfs"]["count"],2)
        arg2 = round(c["mips"]["lns"]["sum"]/c["mips"]["lns"]["count"],2)
        arg3 = round(c["hexagon"]["dfs"]["sum"]/c["hexagon"]["dfs"]["count"],2)
        arg4 = round(c["hexagon"]["lns"]["sum"]/c["hexagon"]["lns"]["count"],2)
        impr1 = improvement(arg2, arg1)
        impr2 = improvement(arg4, arg3)
        print >> f, "\\hline" 
        print >> f, "%s&%s&%s&%s&%s&%s&%s\\\\"%("average", arg1, arg2, impr1, arg3, arg4, impr2)
        print >> f, "\\hline" 
        print >> f, "\\end{tabular}" 
        print >> f, "\\end{document}" 

    p = subprocess.Popen(["pdflatex", texname + ".tex"], stdout=subprocess.PIPE)
    p.communicate()
    p = subprocess.Popen(["evince", texname + ".pdf"], stdout=subprocess.PIPE)
    p.communicate()

 

def plot_all(field, d, yvalue, title):

    def plot_arch(d, arch, ax):

        def autolabel(rects):
            """Attach a text label above each bar in *rects*, displaying its height."""
            for rect in rects:
                height = rect.get_height()
                ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        rotation=90,
                        ha='center', va='bottom')


        labels = d.keys()
        dfs_means = [d[b][arch]["dfs"][field]['num'] if d[b].has_key(arch) and d[b][arch].has_key("dfs") else 0 for b in d]
        lns_means = [d[b][arch]["lns"][field]['num'] if d[b].has_key(arch) and d[b][arch].has_key("lns") else 0 for b in d]

        x = np.arange(len(labels))  # the label locations
        width = 0.35  # the width of the bars

        #fig, ax = plt.subplots()
        rects1 = ax.bar(x - width/2, dfs_means, width, color = 'blue', label='DFS')
        rects2 = ax.bar(x + width/2, lns_means, width, color = 'green', label='LNS')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel(yvalue)
        ax.set_title(title + " (%s)"%arch)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=6)
        ax.legend()

            
        autolabel(rects1)
        autolabel(rects2)

        #fig.tight_layout()

        #plt.show()

    #plt.plot([1,2,3])
    # now create a subplot which represents the top plot of a grid
    # with 2 rows and 1 column. Since this subplot will overlap the
    # first, the plot (and its axes) previously created, will be removed
    ax = plt.subplot(2, 1, 1)
    plot_arch(d, "mips", ax)
    ax = plt.subplot(2, 1, 2)
    plot_arch(d, "hexagon", ax)
    plt.show()





pathname = "divs/"   # sys.argv[1]
s_metric = "hamming" # sys.argv[2]
s_agap = "10"        # sys.argv[3]         #
s_constant = "10000" # sys.argv[4]
s_relax = "0.8"      # sys.argv[5]
s_out = "hamming"



try:
    opts, args = getopt.getopt(sys.argv[1:],"hp:m:g:c:r:o:",["pathname=","metric=","agap=", "constant=", "relax=", "outmetric="])
except getopt.GetoptError:
    print "$ python onlyham_test.py -p <path of the measurments> -m <metric=hamming|br_hamming|diff_br_hamming> -g <acceptable gap>  -c <restart constant> -r <relax> -o <output metric = hamming|br_hamming|diff_br_hamming|extime|all>"
    # print 'test.py -i <inputfile> -o <outputfile>'
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        print "$ python onlyham_test.py -p <path of the measurments> -m <metric=hamming|br_hamming|diff_br_hamming> -g <acceptable gap>  -c <restart constant> -r <relax> -o <output metric = hamming|br_hamming|diff_br_hamming|extime|all>"
        sys.exit()
    elif opt in ("-m", "--metric"):
        s_metric = arg
        print "metric ", opt, arg
    elif opt in ("-g", "--agap"):
        s_agap = arg
        print "agap", opt, arg
    elif opt in ("-p", "--pathname"):
        pathname = arg
        print "path", opt, arg
    elif opt in ("-c", "--constant"):
        s_constant = arg
        print "c", opt, arg
    elif opt in ("-r", "--relax"):
        print "relax", opt, arg
        s_relax = arg
    elif opt in ("-o", "--outmetric"):
        print "out", opt, arg
        s_out = arg
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
    for pfile in listdir(pathname + benchmark + "/"):
        if pfile.endswith("pickle"):
            try:
                a = re.match(pat,pfile)
                method,arch,agap,divs,metric,rest = a.groups()
            except:
                continue
            if metric != s_metric  or agap != s_agap :
                continue
            if method == "lns":
                try:
                    pat2 = re.compile("_(0.[0-9]+)_([0-9]+)_(.*)")
                    a = re.match(pat2,rest)
                    relax, constant, restart = a.groups() 
                    if constant != s_constant or s_relax != relax:
                        continue
                except:
                    print rest

            #arch = a.group(2)
            files = pickle.load(open(pathname + benchmark + "/" + pfile))
            files = {h:files[h] for h in files if benchmark in h}
            # cycles = {h:files[h]['cycles'] for h in files if files[h].has_key('cycles')}
            brcycles = {h:[ c for  c,j  in zip(files[h]['cycles'],files[h]['type']) if j == 1] for h in files if files[h].has_key('type') and files[h].has_key('cycles')}
            cycles = {h:[ c for  c,j  in zip(files[h]['cycles'],files[h]['type']) if j in [0,1,2,3,14]] for h in files if files[h].has_key('type') and files[h].has_key('cycles')}
            extime = max([ files[h]['solver_time'] for h in files if files[h].has_key('solver_time') ])/1000. # the maximum should be the last
            fnames = [ fi for fi in cycles.keys() if fi.split(".")[0].isdigit()]

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
                if not d[benchmark].has_key(arch):
                    d[benchmark][arch] = dict()
                d[benchmark][arch][method] = {'avg': { 'num':round(sumhd/count,2),'maxnum': maxnum}, 'divs':len(fnames), 'extime': { 'num': extime, 'maxnum': 60*5.}}


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
                if not d[benchmark].has_key(arch):
                    d[benchmark][arch] = dict()
                    d[benchmark][arch][method] = {'bravg': {'num': round(sumhd/count,4), 'maxnum': maxnum}, 'divs': len(fnames), 'extime': { 'num': extime, 'maxnum': 60*5.}}
                else:
                    d[benchmark][arch][method]['bravg']  = {'num': round(sumhd/count,4), 'maxnum': maxnum}


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
                if not d[benchmark].has_key(arch):
                    d[benchmark][arch] = dict()
                    d[benchmark][arch][method] = {'brdiff': {'num': round(sumhd/count,2), 'maxnum': maxnum} , 'divs':len(fnames), 'extime': { 'num': extime, 'maxnum': 60*5.}}
                else:
                    d[benchmark][arch][method]['brdiff']  = {'num': round(sumhd/count,2), 'maxnum': maxnum}


# Table
if (s_out in ["hamming", "all"]):
    title = "Hamming distance for %s, %s, %s, %s" %(s_metric, s_agap, s_constant, s_relax)
    create_tex("out_hamming",       "hamm",     "avg", title, d)

if (s_out in ["br_hamming", "all"]):
    title = "Hamming distance of branch instructions for %s, %s, %s, %s" %(s_metric, s_agap, s_constant, s_relax)
    create_tex("out_brhamming",     "brhamm",    "bravg",  title, d)

if (s_out in ["diff_br_hamming", "all"]):
    title = "Hamming distance of difference to branch instructions for %s, %s, %s, %s" %(s_metric, s_agap, s_constant, s_relax)
    create_tex("out_diffbrhamming", "diffhamm",  "brdiff",  title, d)

# if (s_out in ["extime", "all"]):
#     title = "Execution time (s) of the generation of the last variant for %s, %s, %s, %s" %(s_metric, s_agap, s_constant, s_relax)
#     create_tex("out_extime",        "ms",        "extime",  title, d)

# Plot
if (s_out in ["hamming", "all"]):
    plot_all("avg",    d, "Hamming Distance", 'Hamming Distance between DFS LNS')

if (s_out in ["br_hamming", "all"]):
    plot_all("bravg",  d, "Hamming Distance", 'Branch Hamming Distance between DFS LNS')

if (s_out in ["diff_br_hamming", "all"]):
    plot_all("brdiff", d, "Hamming Distance", 'Diff Branch Hamming Distance between DFS LNS')

if (s_out in ["extime", "all"]):
    plot_all("extime", d, "Execution Time", 'Execution time')
