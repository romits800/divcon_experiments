#!/usr/bin/python

from os import listdir

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import json

import sys

import pickle
import re

import subprocess

import getopt

import math


def improvement(lns, dfs):
    if (lns > dfs):
	if dfs == 0:
		return  -round((float) ((dfs - lns)/lns)*100,2)
        return round((float) ((lns-dfs)/dfs)*100,2)
    elif (dfs > lns):
        if lns == 0:
		return  -round((float) ((lns - dfs)/dfs)*100,2)
	return -round((float) ((dfs-lns)/lns)*100,2)
    else:
        return 0.0

def get_ind(field):
    if field == 'avg':
        return 'hamm'
    elif field == 'bravg':
        return 'brhamm'
    elif field == 'brdiff':
        return 'brdiffhamm'
    elif field == 'cost':
        return 'cycles'
    elif field == 'stime':
        return 'ms'


def create_tex(d, metric, field, relax, agap, branch, texname='outfile'):
    '''
	d: the dictionary with the measurements
		e.g. d = pickle.load(open("divs.pickle"))
	metric: the metric of the measurement (from divcon - unison)
	field: 'avg', 'bravg', 'brdiff' output metric
	relax: 0.4, 0.45, ..., 0.95 the relax rate
	agap: 10, 20 allowed gap from the optimal solution
	branch: original, random, cloriginal, clrandom
        texname: name of the output .tex file - default = 'outfile'
    ''' 
    agap = str(agap)
    relax = str(relax)

    ind = get_ind(field)

    title = "%s for measurements of (%s, %s, %s%%, %s)" %(ind.capitalize(), str(relax), metric, str(agap), branch)

    names = sorted(d.keys())
    with open(texname + '.tex', 'w') as f:
        print >> f, "\\documentclass{standalone}"
        print >> f, "\\usepackage{multirow}"
        print >> f, "\\begin{document}"
        print >> f, "\\begin{tabular}{|l|cc|c|cc|c|}" 
        print >> f, "\\hline" 
        print >> f, "\\multicolumn{7}{|c|}{%s}\\\\" %title.replace("_","").replace("%", "\\%")
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
            mipsdfs = d[benchmark].has_key("mips") and d[benchmark]["mips"].has_key("dfs") and d[benchmark]["mips"]["dfs"].has_key(metric) and d[benchmark]["mips"]["dfs"][metric].has_key(agap) and d[benchmark]["mips"]["dfs"][metric][agap].has_key(branch) and d[benchmark]["mips"]["dfs"][metric][agap][branch][None].has_key(field)
	    mipslns = d[benchmark].has_key("mips") and d[benchmark]["mips"].has_key("lns") and d[benchmark]["mips"]["lns"].has_key(metric) and d[benchmark]["mips"]["lns"][metric].has_key(agap) and d[benchmark]["mips"]["lns"][metric][agap].has_key(branch) and d[benchmark]["mips"]["lns"][metric][agap][branch].has_key(relax) and d[benchmark]["mips"]["lns"][metric][agap][branch][relax].has_key(field)

            hexagondfs = d[benchmark].has_key("hexagon") and d[benchmark]["hexagon"].has_key("dfs") and d[benchmark]["hexagon"]["dfs"].has_key(metric) and d[benchmark]["hexagon"]["dfs"][metric].has_key(agap) and d[benchmark]["hexagon"]["dfs"][metric][agap].has_key(branch) and d[benchmark]["hexagon"]["dfs"][metric][agap][branch][None].has_key(field)
            hexagonlns = d[benchmark].has_key("hexagon") and d[benchmark]["hexagon"].has_key("lns") and d[benchmark]["hexagon"]["lns"].has_key(metric) and d[benchmark]["hexagon"]["lns"][metric].has_key(agap) and d[benchmark]["hexagon"]["lns"][metric][agap].has_key(branch) and d[benchmark]["hexagon"]["lns"][metric][agap][branch].has_key(relax) and d[benchmark]["hexagon"]["lns"][metric][agap][branch][relax].has_key(field)

            arg1 = "-"
            arg2 = "-"
            if mipsdfs:
                nrelax = None
                dfsnum = d[benchmark]["mips"]["dfs"][metric][agap][branch][nrelax][field]['num']
                dfsmaxnum = d[benchmark]["mips"]["dfs"][metric][agap][branch][nrelax][field]['maxnum']
                dfsdivs = d[benchmark]["mips"]["dfs"][metric][agap][branch][nrelax]["divs"]
                arg1 = "%.2f\\textbackslash %d (%d)" %(dfsnum, dfsmaxnum, dfsdivs)

                c["mips"]["dfs"]["sum"] += d[benchmark]["mips"]["dfs"][metric][agap][branch][nrelax][field]['num']
                c["mips"]["dfs"]["count"] += 1

            if mipslns:
                lnsnum = d[benchmark]["mips"]["lns"][metric][agap][branch][relax][field]['num']
                lnsmaxnum = d[benchmark]["mips"]["lns"][metric][agap][branch][relax][field]['maxnum']
                lnsdivs = d[benchmark]["mips"]["lns"][metric][agap][branch][relax]["divs"]
                arg2 = "%.2f\\textbackslash %d (%d)" %(lnsnum, lnsmaxnum, lnsdivs)
                c["mips"]["lns"]["sum"]+= d[benchmark]["mips"]["lns"][metric][agap][branch][relax][field]['num']
                c["mips"]["lns"]["count"] += 1

            impr1 = "-"
            if mipslns and mipsdfs:
                nrelax = None
                lnsnum = d[benchmark]["mips"]["lns"][metric][agap][branch][relax][field]['num']
                dfsnum = d[benchmark]["mips"]["dfs"][metric][agap][branch][nrelax][field]['num']
                impr1 = "%.2f" %improvement(lnsnum, dfsnum)

            #arg2 = str(d[benchmark]["mips"]["lns"][relax][field]['num']) + "\\textbackslash " + str(d[benchmark]["mips"]["lns"][relax][field]['maxnum']) + " (" + str(d[benchmark]["mips"]["lns"]["divs"]) + ")" if mipslns and mipsdfs else "-"

            arg3 = "-"
            arg4 = "-"
            if hexagondfs:
                nrelax = None
                dfsnum = d[benchmark]["hexagon"]["dfs"][metric][agap][branch][nrelax][field]['num']
                dfsmaxnum = d[benchmark]["hexagon"]["dfs"][metric][agap][branch][nrelax][field]['maxnum']
                dfsdivs = d[benchmark]["hexagon"]["dfs"][metric][agap][branch][nrelax]["divs"]
                arg3 = "%.2f\\textbackslash %d (%d)" %(dfsnum, dfsmaxnum, dfsdivs)

                c["hexagon"]["dfs"]["sum"] += d[benchmark]["hexagon"]["dfs"][metric][agap][branch][nrelax][field]['num']
                c["hexagon"]["dfs"]["count"] += 1
                
            if hexagonlns: 
                lnsnum = d[benchmark]["hexagon"]["lns"][metric][agap][branch][relax][field]['num']
                lnsmaxnum = d[benchmark]["hexagon"]["lns"][metric][agap][branch][relax][field]['maxnum']
                lnsdivs = d[benchmark]["hexagon"]["lns"][metric][agap][branch][relax]["divs"]
                arg4 = "%.2f\\textbackslash %d (%d)" %(lnsnum, lnsmaxnum, lnsdivs)
                c["hexagon"]["lns"]["sum"]+= d[benchmark]["hexagon"]["lns"][metric][agap][branch][relax][field]['num']
                c["hexagon"]["lns"]["count"] += 1

            impr2 = "-"
            if hexagonlns and hexagondfs:
                lnsnum = d[benchmark]["hexagon"]["lns"][metric][agap][branch][relax][field]['num']
                dfsnum = d[benchmark]["hexagon"]["dfs"][metric][agap][branch][None][field]['num']
                impr2 = "%.2f" %improvement(lnsnum, dfsnum)


            print >> f, "%s&%s&%s&%s&%s&%s&%s\\\\"%(benchmark.replace("_","\\_"), arg1, arg2, impr1, arg3, arg4, impr2)


        arg1 = 0.
        arg2 = 0.
        arg3 = 0.
        arg4 = 0.
        if c["mips"]["dfs"]["count"] != 0:
            arg1 = round(c["mips"]["dfs"]["sum"]/c["mips"]["dfs"]["count"],2)
        if c["mips"]["lns"]["count"] != 0:
            arg2 = round(c["mips"]["lns"]["sum"]/c["mips"]["lns"]["count"],2)
        if c["hexagon"]["dfs"]["count"] != 0:
            arg3 = round(c["hexagon"]["dfs"]["sum"]/c["hexagon"]["dfs"]["count"],2)
        if c["hexagon"]["lns"]["count"] != 0:
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

 

def plot_all(d, metric, field, relax, agap, branch):
    '''
	d: the dictionary with the measurements
		e.g. d = pickle.load(open("divs.pickle"))
	metric: the metric of the measurement (from unison)
	field: 'avg', 'bravg', 'brdiff' output metric
	relax: 0.4, 0.45, ..., 0.95 the relax rate
	agap: 10, 20 allowed gap from the optimal solution
	branch: original, random, cloriginal, clrandom
    '''
    agap = str(agap)
    relax = str(relax)
    yvalue = get_ind(field)

    title = "%s for measurements of (%s, %s, %s%%, %s)" %(yvalue.capitalize(), str(relax), metric, str(agap), branch)

    def constr(b, arch, method):
	rel = None if method == "dfs" else relax
        return d[b].has_key(arch) and d[b][arch].has_key(method) and d[b][arch][method].has_key(metric) and d[b][arch][method][metric].has_key(agap) and d[b][arch][method][metric][agap].has_key(branch) and d[b][arch][method][metric][agap][branch].has_key(rel) and d[b][arch][method][metric][agap][branch][rel].has_key(field)


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
        dfs_means = [d[b][arch]["dfs"][metric][agap][branch][None][field]['num'] if constr(b, arch, "dfs") else 0 for b in d]
        # confidence interval
        dfs_error = [2*d[b][arch]["dfs"][metric][agap][branch][None][field]['stdev']/math.sqrt(d[b][arch]["dfs"][metric][agap][branch][None]['num']) if constr(b, arch, "dfs") else 0 for b in d]
        lns_means = [d[b][arch]["lns"][metric][agap][branch][relax][field]['num'] if constr(b, arch, "lns") else 0 for b in d]
        lns_error = [2*d[b][arch]["lns"][metric][agap][branch][relax][field]['stdev']/math.sqrt(d[b][arch]["lns"][metric][agap][branch][relax]['num']) if constr(b, arch, "lns") else 0 for b in d]

        # Coefficient of variation
        #lns_coef_of_var = [d[b][arch]["lns"][metric][agap][branch][relax][field]['stdev']/d[b][arch]["lns"][metric][agap][branch][relax][field]['num'] if constr(b, arch, "lns") else 0 for b in d]
        #dfs_coef_of_var = [d[b][arch]["dfs"][metric][agap][branch][None][field]['stdev']/d[b][arch]["dfs"][metric][agap][branch][None][field]['num'] if constr(b, arch, "dfs") else 0 for b in d]
        #print lns_coef_of_var
        #print dfs_coef_of_var

        x = np.arange(len(labels))  # the label locations
        width = 0.35  # the width of the bars

        #fig, ax = plt.subplots()
        rects1 = ax.bar(x - width/2, dfs_means, width, yerr=dfs_error, ecolor= 'black', color = 'blue', label='DFS')
        rects2 = ax.bar(x + width/2, lns_means, width, yerr=lns_error, ecolor= 'black', color = 'green', label='LNS')

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

    plt.subplots_adjust(hspace=0.5)

    plt.show()


def plot_hist(d, metric, field, relax, agap, branch):
    '''
	d: the dictionary with the measurements
		e.g. d = pickle.load(open("divs.pickle"))
	metric: the metric of the measurement (from unison)
	field: 'avg', 'bravg', 'brdiff' output metric
	relax: 0.4, 0.45, ..., 0.95 the relax rate
	agap: 10, 20 allowed gap from the optimal solution
	branch: original, random, cloriginal, clrandom
    '''
    agap = str(agap)
    relax = str(relax)
    yvalue = get_ind(field)

    title = "%s for measurements of (%s, %s, %s%%, %s)" %(yvalue.capitalize(), str(relax), metric, str(agap), branch)


    def constr(b, arch,  method):
	rel = None if method == "dfs" else relax
        return d[b].has_key(arch) and d[b][arch].has_key(method) and d[b][arch][method].has_key(metric) and d[b][arch][method][metric].has_key(agap) and d[b][arch][method][metric][agap].has_key(branch) and d[b][arch][method][metric][agap][branch].has_key(rel) and d[b][arch][method][metric][agap][branch][rel].has_key(field)


    def plot_arch(d, arch, ax):

        labels = d.keys()

        dfs = [d[b][arch]["dfs"][metric][agap][branch][None][field]['data'] if constr(b, arch, "dfs") else [0] for b in d]
        lns = [d[b][arch]["lns"][metric][agap][branch][relax][field]['data'] if constr(b, arch, "lns") else [0] for b in d]

        x = 2*np.arange(len(labels)) + 0.5 # the label locations
        width = 0.35  # the width of the bars

        lines = []

        offset = 0
        for b in labels:
            datalns = [0]
            datadfs = [0]
            if constr(b, arch, "dfs"):
                datadfs = d[b][arch]["dfs"][metric][agap][branch][None][field]['data']

            if constr(b, arch, "lns"):
                datalns = d[b][arch]["lns"][metric][agap][branch][relax][field]['data']

            # innerwidth = 0.035
            maxdata = max([max(datadfs), max(datalns)])
            if maxdata == 0:
                offset += 2
                continue

	    #print datalns
	    #print datadfs
	    

            xxlns = [offset + i/maxdata for i in datalns]
            xxdfs = [offset + i/maxdata for i in datadfs]

            num_bins_lns = int(max(datalns) - min(datalns))
            num_bins_dfs = int(max(datadfs) - min(datadfs))

            if (num_bins_dfs > 0):
                n, bins, patches = ax.hist(xxdfs, num_bins_dfs, normed=True, alpha=0.5, facecolor = 'blue',  label='DFS')

            if (num_bins_lns > 0):
                n, bins, patches = ax.hist(xxlns, num_bins_lns, normed=True, alpha=0.5, facecolor = 'green', label='LNS')

            offset += 2


        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel(yvalue)
        ax.set_title(title + " (%s)"%arch)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=6)
        # ax.legend()
        handles = [Rectangle((0,0),1,1,color=c,ec="k") for c in ['blue', 'green']]
        labels= ["DFS","LNS"]
        ax.legend(handles, labels)


        # autolabel(rects1)       #
        # autolabel(rects2)

        #fig.tight_layout()

        #plt.show()

    ax = plt.subplot(2, 1, 1)
    plot_arch(d, "mips", ax)
    ax = plt.subplot(2, 1, 2)
    plot_arch(d, "hexagon", ax)
    plt.subplots_adjust(hspace=0.3) #bottom=0.1, right=0.8, top=0.9)
    plt.show()





def plot_relax(d, metric, field, agap, branch):
    '''
	d: the dictionary with the measurements
		e.g. d = pickle.load(open("divs.pickle"))
	metric: the metric of the measurement (from unison)
	field: 'avg', 'bravg', 'brdiff' output metric
	agap: 10, 20 allowed gap from the optimal solution
	branch: original, random, cloriginal, clrandom
    '''
    agap = str(agap)
    yvalue = get_ind(field)

    title = "%s for measurements of (%s, %s%%, %s)" %(yvalue.capitalize(), metric, str(agap), branch)

    def constr(b, arch, method):
	if method == "dfs":
        	return d[b].has_key(arch) and d[b][arch].has_key(method) and d[b][arch][method].has_key(metric) and d[b][arch][method][metric].has_key(agap) and d[b][arch][method][metric][agap].has_key(branch) and d[b][arch][method][metric][agap][branch].has_key(None) and d[b][arch][method][metric][agap][branch][None].has_key(field)
	else:
        	return d[b].has_key(arch) and d[b][arch].has_key(method) and d[b][arch][method].has_key(metric) and d[b][arch][method][metric].has_key(agap) and d[b][arch][method][metric][agap].has_key(branch) and len(d[b][arch][method][metric][agap][branch]) > 0 and d[b][arch][method][metric][agap][branch][ d[b][arch][method][metric][agap][branch].keys()[0]   ].has_key(field)



    def plot_arch(d, b, arch, ax):

        labels = d.keys()
        if constr(b, arch, "lns"):
            lns = [(r, d[b][arch]["lns"][metric][agap][branch][str(r)][field]['num'], 2*d[b][arch]["lns"][metric][agap][branch][str(r)][field]['stdev']/math.sqrt(d[b][arch]["lns"][metric][agap][branch][str(r)]['num']))  for r in sorted(map(float,d[b][arch]["lns"][metric][agap][branch].keys())) ]

            x,y,err = zip(*lns)

            # print b, x, y
            ax.errorbar(x,y, yerr=err, linewidth=1.5, label="LNS")
            #ax.plot(x,y, linewidth=1.5, label="LNS")

            if constr(b, arch, "dfs"):
                v = d[b][arch]["dfs"][metric][agap][branch][None][field]['num']
                ax.plot(x, [v for _ in x], linewidth=1.5, label="DFS");

            ymax = max(list(y)+[v])
            ax.set_ylim(ymax=1.1*ymax)
        ax.set_ylim(ymin=0)

        # Fontsize and labels
        ax.set_ylabel(yvalue, fontsize = 8)
        ax.set_xlabel("relax rate", fontsize = 8)

        ax.set_title(b + " (%s)"%arch, fontsize = 8)
        ax.legend(loc='lower right', fontsize = 8)

    def plot_subplots(arch, dk, st, nl, pos):
        # dk = d.keys()
        for i,b in enumerate(dk[st+pos*nl:st+(pos+1)*nl]):
            ax = plt.subplot(4, nl, i + 1 + pos*nl)
            plot_arch(d, b, arch, ax)

    n = 20
    lims = [(i,i+n) for i in range(0,len(d), n)]
    dk = d.keys()
    for arch in ["mips", "hexagon"]:
        for (st,nsp) in lims:
            nl = (nsp-st)/4
            print st, nsp, nl
            plot_subplots(arch, dk, st, nl, 0)
            plot_subplots(arch, dk, st, nl, 1)
            plot_subplots(arch, dk, st, nl, 2)
            plot_subplots(arch, dk, st, nl, 3)

            plt.subplots_adjust(hspace=0.3) #bottom=0.1, right=0.8, top=0.9)
            plt.suptitle(title, fontsize=20)
            plt.show()




def plot_relax_all(d, metric, field, agap, branch):
    '''
	d: the dictionary with the measurements
		e.g. d = pickle.load(open("divs.pickle"))
	metric: the metric of the measurement (from unison)
	field: 'avg', 'bravg', 'brdiff' output metric
	agap: 10, 20 allowed gap from the optimal solution
	branch: original, random, cloriginal, clrandom
    '''
    agap = str(agap)
    yvalue = get_ind(field)

    title = "%s for measurements of (%s, %s%%, %s)" %(yvalue.capitalize(), metric, str(agap), branch)

    def constr(b, arch, method):
	if method == "dfs":
        	return d[b].has_key(arch) and d[b][arch].has_key(method) and d[b][arch][method].has_key(metric) and d[b][arch][method][metric].has_key(agap) and d[b][arch][method][metric][agap].has_key(branch) and d[b][arch][method][metric][agap][branch].has_key(None) and d[b][arch][method][metric][agap][branch][None].has_key(field)
	else:
        	return d[b].has_key(arch) and d[b][arch].has_key(method) and d[b][arch][method].has_key(metric) and d[b][arch][method][metric].has_key(agap) and d[b][arch][method][metric][agap].has_key(branch) and len(d[b][arch][method][metric][agap][branch]) > 0 and d[b][arch][method][metric][agap][branch][ d[b][arch][method][metric][agap][branch].keys()[0]   ].has_key(field)

    def plot_arch(d, arch, ax):

        labels = d.keys()
	rs = []
        for r in np.arange(0.4,1.0, 0.1):
		nums = [d[b][arch]["lns"][metric][agap][branch][str(r)][field]['num'] for b in d if constr(b, arch, "lns")]	

                error = [2*d[b][arch]["lns"][metric][agap][branch][str(r)][field]['stdev']/math.sqrt(d[b][arch]["lns"][metric][agap][branch][str(r)]['num']) for b in d if constr(b, arch, "dfs")]
		if len(nums)> 0 and len(error)>0:
			rs.append((r, sum(nums)/len(nums), sum(error)/len(error)))

        x,y,err = zip(*rs)
        print x, y

            # print b, x, y
        ax.errorbar(x, y, yerr=err, linewidth=1.5, label="LNS")
        #ax.plot(x, y, yerr=err, linewidth=1.5, label="LNS")


        v = 0
        df = []
        for b in d:
            if constr(b, arch, "dfs"):
                df.append(d[b][arch]["dfs"][metric][agap][branch][None][field]['num'])
        if (len(df) > 0):
            v = sum(df)/len(df)
        ax.plot(x, [v for _ in x], linewidth=1.5, label="DFS");

        ymax = max(list(y)+[v])
        print ymax
        ax.set_ylim(ymax=1.1*ymax)
        ax.set_ylim(ymin=0)

        # Fontsize and labels
        ax.set_ylabel(yvalue, fontsize = 8)
        ax.set_xlabel("relax rate", fontsize = 8)

        ax.set_title(title + " (%s)"%arch, fontsize = 8)
        ax.legend(loc='lower right', fontsize = 8)


    ax = plt.subplot(2, 1, 1)
    plot_arch(d, "mips", ax)
    ax = plt.subplot(2, 1, 2)
    plot_arch(d, "hexagon", ax)

    plt.subplots_adjust(hspace=0.5)

    plt.show()


def plot_all_branching(d, metric, field, relax, agap):
    '''
	d: the dictionary with the measurements
		e.g. d = pickle.load(open("divs.pickle"))
	metric: the metric of the measurement (from unison)
	field: 'avg', 'bravg', 'brdiff' output metric
	relax: 0.4, 0.45, ..., 0.95 the relax rate
	agap: 10, 20 allowed gap from the optimal solution
	branch: original, random, cloriginal, clrandom
    '''
    agap = str(agap)
    relax = str(relax)
    yvalue = get_ind(field)

    title = "%s for measurements of (%s, %s, %s%%)" %(yvalue.capitalize(), str(relax), metric, str(agap))

    def constr(b, arch, branch, method):
	rel = None if method == "dfs" else relax
        return d[b].has_key(arch) and d[b][arch].has_key(method) and d[b][arch][method].has_key(metric) and d[b][arch][method][metric].has_key(agap) and d[b][arch][method][metric][agap].has_key(branch) and d[b][arch][method][metric][agap][branch].has_key(rel) and d[b][arch][method][metric][agap][branch][rel].has_key(field)


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
                        ha='center', va='bottom', fontsize=6)


        labels = d.keys()
        dfs_means = dict()
        lns_means = dict()
        dfs_error = dict()
        lns_error = dict()
        for branch in ["original", "random", "cloriginal", "clrandom"]:
            dfs_means[branch] = [d[b][arch]["dfs"][metric][agap][branch][None][field]['num'] if constr(b, arch, branch, "dfs") else 0 for b in d]
            lns_means[branch] = [d[b][arch]["lns"][metric][agap][branch][relax][field]['num'] if constr(b, arch, branch, "lns") else 0 for b in d]
            dfs_error[branch] = [2*d[b][arch]["dfs"][metric][agap][branch][None][field]['stdev']/math.sqrt(d[b][arch]["dfs"][metric][agap][branch][None]['num']) if constr(b, arch, branch, "dfs") else 0 for b in d]
            lns_error[branch] = [2*d[b][arch]["lns"][metric][agap][branch][relax][field]['stdev']/math.sqrt(d[b][arch]["lns"][metric][agap][branch][relax]['num']) if constr(b, arch, branch, "lns") else 0 for b in d]

            #lns_coef_of_var = [d[b][arch]["lns"][metric][agap][branch][relax][field]['stdev']/d[b][arch]["lns"][metric][agap][branch][relax][field]['num'] if constr(b, arch,branch, "lns") else 0 for b in d]
            #dfs_coef_of_var = [d[b][arch]["dfs"][metric][agap][branch][None][field]['stdev']/d[b][arch]["dfs"][metric][agap][branch][None][field]['num'] if constr(b, arch, branch,"dfs") else 0 for b in d]
            #print lns_coef_of_var
            #print dfs_coef_of_var




        x = 2*np.arange(len(labels))  # the label locations
        width = 2*0.35  # the width of the bars

        #fig, ax = plt.subplots()
        
        rects1 = []
        rects2 = []
        for i,branch in enumerate(["original", "cloriginal", "random", "clrandom"], 1):
            rects1.append(ax.bar(x - 5*width/4+ i*width/4, dfs_means[branch], width/6, yerr=dfs_error[branch], ecolor='black', color = (0.4, 0.4, 0.2 + i*0.2), label='DFS (' + branch + ')'))
        for i,branch in enumerate(["original", "cloriginal", "random", "clrandom"], 1):
            rects2.append(ax.bar(x + i*width/4, lns_means[branch], width/6, yerr=lns_error[branch], ecolor='black', color = (0.1, 0.2 + i*0.2, 0.2), label='LNS ('+branch + ')'))

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel(yvalue)
        ax.set_title(title + " (%s)"%arch)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=6)
        ax.legend()

            
        for rect in rects1:
            autolabel(rect)
        for rect in rects2:
            autolabel(rect)

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

    plt.subplots_adjust(hspace=0.5)

    plt.show()

def plot_maxdiv_time(d, metric, field, agap):
    arch = 'mips'
    algo = 'dfs'
    br   = 'cloriginal'
    l = dict()
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    for b in d:
        if not (d[b].has_key(arch) and d[b][arch].has_key(algo) and d[b][arch][algo].has_key(metric) and d[b][arch][algo][metric].has_key(agap) and d[b][arch][algo][metric][agap].has_key(br) and d[b][arch][algo][metric][agap][br][None].has_key(field)):
                continue
        cdict = dict(**d[b][arch][algo][metric][agap][br][None][field])
        xy = [ (i, cdict[i]['stime']) for i in  cdict.keys()]
        if len(xy) > 0:
            x,y = zip(*xy)
            plt.plot(x, y, label=b)
            

    plt.legend(loc='center right')
    ax.set_yscale('log')
    ax.set_ylim(bottom=1)

    plt.show()

def plot_maxdiv_dist(d, metric, field, agap):
    arch = 'mips'
    algo = 'dfs'
    br   = 'cloriginal'
    l = dict()
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    for b in d:
        if not (d[b].has_key(arch) and d[b][arch].has_key(algo) and d[b][arch][algo].has_key(metric) and d[b][arch][algo][metric].has_key(agap) and d[b][arch][algo][metric][agap].has_key(br) and d[b][arch][algo][metric][agap][br][None].has_key(field)):
                continue
        cdict = dict(**d[b][arch][algo][metric][agap][br][None][field])
        xy = [ (i, cdict[i]['num']) for i in  cdict.keys()]
        if len(xy) > 0:
            x,y = zip(*xy)
            plt.plot(x, y, label=b)
            

    plt.legend(loc='center right')
    ax.set_ylim(bottom=0)

    plt.show()


def plot_maxdiv_lns_dist(d_maxdiv, d_lns, b, metric, field, agap, relax):
    arch = 'mips'
    rel = str(relax)
    agap = str(agap)
    l = dict()
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    # MaxDiversekSet
    algo = 'dfs'
    br   = 'cloriginal'
 
    if (d_maxdiv[b].has_key(arch) and d_maxdiv[b][arch].has_key(algo) and d_maxdiv[b][arch][algo].has_key(metric) and d_maxdiv[b][arch][algo][metric].has_key(agap) and d_maxdiv[b][arch][algo][metric][agap].has_key(br) and d_maxdiv[b][arch][algo][metric][agap][br][None].has_key(field)):
        cdict = dict(**d_maxdiv[b][arch][algo][metric][agap][br][None][field])
        xy = [ (i, cdict[i]['num']) for i in  cdict.keys()]
        if len(xy) > 0:
            x,y = zip(*xy)
            plt.plot(x, y, label='MaxDiversekSet')

    # Random search
    algo = 'dfs'
    br   = 'clrandom'
 
    if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(rel) and d_lns[b][arch][algo][metric][agap][br][rel].has_key(field)):
        cdict = dict(**d_lns[b][arch][algo][metric][agap][br][rel][field])
        xy = [ (i, cdict[i]['num']) for i in  cdict.keys()]
        if len(xy) > 0:
            x,y = zip(*xy)
            plt.plot(x, y, label='Random Search')
 
    # LNS
    algo = 'lns'
    br   = 'clrandom'
 
    if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(rel) and d_lns[b][arch][algo][metric][agap][br][rel].has_key(field)):
        cdict = dict(**d_lns[b][arch][algo][metric][agap][br][rel][field])
        xy = [ (i, cdict[i]['num']) for i in  cdict.keys()]
        if len(xy) > 0:
            x,y = zip(*xy)
            plt.plot(x, y, label='LNS')
                

    ax.set_ylim(bottom=0)
    plt.legend(loc='center right')

    plt.title(b)

    plt.show()



def plot_maxdiv_lns_time(d_maxdiv, d_lns, b, metric, field, agap, relax):
    arch = 'mips'
    rel = str(relax)
    agap = str(agap)
    l = dict()
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    # MaxDiversekSet
    algo = 'dfs'
    br   = 'cloriginal'
    if (d_maxdiv[b].has_key(arch) and d_maxdiv[b][arch].has_key(algo) and d_maxdiv[b][arch][algo].has_key(metric) and d_maxdiv[b][arch][algo][metric].has_key(agap) and d_maxdiv[b][arch][algo][metric][agap].has_key(br) and d_maxdiv[b][arch][algo][metric][agap][br][None].has_key(field)):
        cdict = dict(**d_maxdiv[b][arch][algo][metric][agap][br][None][field])
        xy = [ (i, cdict[i]['stime']) for i in  cdict.keys()]
        if len(xy) > 0:
            x,y = zip(*xy)
            plt.plot(x, y, label='MaxDiversekSet')

    # Random Search
    algo = 'lns'
    br   = 'clrandom'
 
    if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(rel) and d_lns[b][arch][algo][metric][agap][br][rel].has_key(field)):
        cdict = dict(**d_lns[b][arch][algo][metric][agap][br][rel][field])
        xy = [ (i, cdict[i]['stime']) for i in  cdict.keys()]
        if len(xy) > 0:
            x,y = zip(*xy)
            plt.plot(x, y, label='Random Search')
 
    # LNS
    algo = 'lns'
    br   = 'clrandom'
 
    if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(rel) and d_lns[b][arch][algo][metric][agap][br][rel].has_key(field)):
        cdict = dict(**d_lns[b][arch][algo][metric][agap][br][rel][field])
        xy = [ (i, cdict[i]['stime']) for i in  cdict.keys()]
        if len(xy) > 0:
            x,y = zip(*xy)
            plt.plot(x, y, label='LNS')
                

    ax.set_yscale('log')
    ax.set_ylim(bottom=1)
    plt.legend(loc='center right')
    
    plt.title(b)

    plt.show()



