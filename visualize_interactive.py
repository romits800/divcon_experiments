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

def get_name(field):
    if field == 'avg':
        return 'Hamming'
    elif field == 'bravg':
        return 'Branch Hamming'
    elif field == 'brdiff':
        return 'Relative Branch Hamming'
    elif field == 'levenshtein':
        return 'Levenshtein'
    elif field == 'cost':
        return ''
    elif field == 'stime':
        return 'ms'



def get_ind(field):
    if field == 'avg':
        return 'hamm'
    elif field == 'bravg':
        return 'brhamm'
    elif field == 'brdiff':
        return 'brdiffhamm'
    elif field == 'levenshtein':
        return 'levenshtein'
    elif field == 'cost':
        return 'cycles'
    elif field == 'stime':
        return 'ms'


def geometric_standard_deviation(data, mean):
    '''
    https://en.wikipedia.org/wiki/Geometric_standard_deviation
    '''
    n = len(data)
    if (n <1):
        return -1
    data = np.array(data)
    logdata = np.log(data/mean)**2
    return np.exp(np.sqrt(sum(logdata)/n))

def geometric_conf_interval(data):
    n = len(data)
    if (n<1):
        return (None, None)
    data = np.array(data)
    logdata = np.log(data)
    mean = 1./n*sum(logdata)
    if (n<2):
        inf = 10
        return (np.exp(mean-inf), np.exp(mean+inf))
    sigma = np.sqrt(sum((logdata-mean)**2)/(n-1))
    err = 2.*sigma/np.sqrt(n)
    return (np.exp(mean-err), np.exp(mean+err))



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
        dfs_error = [2*d[b][arch]["dfs"][metric][agap][branch][None][field]['stdev']/math.sqrt(d[b][arch]["dfs"][metric][agap][branch][None][field]['n']) if constr(b, arch, "dfs") else 0 for b in d]
        lns_means = [d[b][arch]["lns"][metric][agap][branch][relax][field]['num'] if constr(b, arch, "lns") else 0 for b in d]
        lns_error = [2*d[b][arch]["lns"][metric][agap][branch][relax][field]['stdev']/math.sqrt(d[b][arch]["lns"][metric][agap][branch][relax][field]['n']) if constr(b, arch, "lns") else 0 for b in d]

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
            lns = [(r, d[b][arch]["lns"][metric][agap][branch][str(r)][field]['num'], 2*d[b][arch]["lns"][metric][agap][branch][str(r)][field]['stdev']/math.sqrt(d[b][arch]["lns"][metric][agap][branch][str(r)][field]['n']))  for r in sorted(map(float,d[b][arch]["lns"][metric][agap][branch].keys())) ]

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

                error = [2*d[b][arch]["lns"][metric][agap][branch][str(r)][field]['stdev']/math.sqrt(d[b][arch]["lns"][metric][agap][branch][str(r)][field]['n']) for b in d if constr(b, arch, "dfs")]
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
            dfs_error[branch] = [2*d[b][arch]["dfs"][metric][agap][branch][None][field]['stdev']/math.sqrt(d[b][arch]["dfs"][metric][agap][branch][None][field]['n']) if constr(b, arch, branch, "dfs") else 0 for b in d]
            lns_error[branch] = [2*d[b][arch]["lns"][metric][agap][branch][relax][field]['stdev']/math.sqrt(d[b][arch]["lns"][metric][agap][branch][relax][field]['n']) if constr(b, arch, branch, "lns") else 0 for b in d]

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
        k = sorted(cdict.keys())
        xy = [ (i, cdict[i]['num'], 2*cdict[i]['stdev']/math.sqrt(cdict[i]['n'])) for i in  k]
        if len(xy) > 0:
            x,y,err = map(np.array,zip(*xy))
            plt.plot(x, y, linestyle='--', color='r', label='MaxDiversekSet')
            plt.fill_between(x, y-err, y+err, linestyle='-.', color='r', alpha = 0.2)
            #plt.errorbar(x, y, yerr=err, linestyle=':', color='k', label='MaxDiversekSet')

    # Random search
    algo = 'dfs'
    br   = 'clrandom'
 
    if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(None) and d_lns[b][arch][algo][metric][agap][br][None].has_key(field)):
        cdict = dict(**d_lns[b][arch][algo][metric][agap][br][None][field])
        k = sorted(cdict.keys())
        xy = [ (i, cdict[i]['num'], 2*cdict[i]['stdev']/math.sqrt(cdict[i]['n'])) for i in  k]
        if len(xy) > 0:
            x,y,err = map(np.array, zip(*xy))
            plt.plot(x, y, linestyle='--', color='g', label='Random Search')
            plt.fill_between(x, y-err, y+err, linestyle='-.', color='g', alpha = 0.2)
            #plt.errorbar(x, y, yerr=err, linestyle='-.', color='k', label='Random Search')
 
    # LNS
    algo = 'lns'
    br   = 'clrandom'
 
    if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(rel) and d_lns[b][arch][algo][metric][agap][br][rel].has_key(field)):
        cdict = dict(**d_lns[b][arch][algo][metric][agap][br][rel][field])
        k = sorted(cdict.keys())
        xy = [ (i, cdict[i]['num'], 2*cdict[i]['stdev']/math.sqrt(cdict[i]['n'])) for i in k ]
        if len(xy) > 0:
            x,y,err = map(np.array, zip(*xy))
            plt.plot(x, y, linestyle='--', color='b', label='LNS')
            plt.fill_between(x, y-err, y+err, linestyle='-.', color='b', alpha = 0.2)
                

    ax.set_ylim(bottom=0)
    ax.set_ylabel(get_ind(field))
    ax.set_xlabel("Number of Variants (k)")
    ax.legend(loc='lower right')
    plt.title(b)
    fig.set_size_inches(18.5/3, 12.5/3)
    plt.savefig("dist_" + b + "_" + metric + ".pdf", dpi=400, format='pdf')
    #plt.legend(loc='center right')


    plt.show()



def plot_maxdiv_lns_time(d_maxdiv, d_lns, b, metric, field, agap, relax):
    arch = 'mips'
    rel = str(relax)
    agap = str(agap)
    l = dict()
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    active = False
    # MaxDiversekSet
    algo = 'dfs'
    br   = 'cloriginal'
    if (d_maxdiv[b].has_key(arch) and d_maxdiv[b][arch].has_key(algo) and d_maxdiv[b][arch][algo].has_key(metric) and d_maxdiv[b][arch][algo][metric].has_key(agap) and d_maxdiv[b][arch][algo][metric][agap].has_key(br) and d_maxdiv[b][arch][algo][metric][agap][br][None].has_key(field)):
        cdict = dict(**d_maxdiv[b][arch][algo][metric][agap][br][None][field])

        # confidence interval
        k = sorted(cdict.keys())
        xy = [ (i, cdict[i]['stime'], 2*cdict[i]['stime_stdev']/math.sqrt(cdict[i]['n'])) for i in  k]
        if len(xy) > 0:
            x,y,err = map(np.array, zip(*xy))
            plt.plot(x, y, linestyle='--', color='r', label='MaxDiversekSet')
            ymerr = y-err
            np.clip(ymerr, 0, max(ymerr), out=ymerr)
            plt.fill_between(x, ymerr, y+err, linestyle='-.', color='r', alpha = 0.2)
            active = True
    # Random Search
    algo = 'dfs'
    br   = 'clrandom'
 
    if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(None) and d_lns[b][arch][algo][metric][agap][br][None].has_key(field)):
        cdict = dict(**d_lns[b][arch][algo][metric][agap][br][None][field])
        k = sorted(cdict.keys())
        xy = [ (i, cdict[i]['stime'], 2*cdict[i]['stime_stdev']/math.sqrt(cdict[i]['n'])) for i in  k]
        if len(xy) > 0:
            x,y,err = map(np.array, zip(*xy))
            plt.plot(x, y, linestyle='--', color='g', label='Random Search')
            ymerr = y-err
            np.clip(ymerr, 0, max(ymerr), out=ymerr)
            plt.fill_between(x, ymerr, y+err, linestyle='-.', color='g', alpha = 0.2)
            active = True
 
    # LNS
    algo = 'lns'
    br   = 'clrandom'
 
    if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(rel) and d_lns[b][arch][algo][metric][agap][br][rel].has_key(field)):
        cdict = dict(**d_lns[b][arch][algo][metric][agap][br][rel][field])
        k = sorted(cdict.keys())
        xy = [ (i, cdict[i]['stime'], 2*cdict[i]['stime_stdev']/math.sqrt(cdict[i]['n'])) for i in k]
        if len(xy) > 0:
            x,y,err = map(np.array, zip(*xy))
            plt.plot(x, y, linestyle='--', color='b', label='LNS')
            ymerr = y-err
            np.clip(ymerr, 0, max(ymerr), out=ymerr)
            plt.fill_between(x, ymerr, y+err, linestyle='-.', color='b', alpha = 0.2)
            active = True
                

    if active:
        ax.set_yscale('log')
        ax.set_ylim(bottom=1)
        plt.legend(loc='lower right')
        ax.set_ylabel(get_ind('stime'))
        ax.set_xlabel("Number of Variants (k)")
    
        plt.title(b)

        fig.set_size_inches(18.5/3, 12.5/3)
        plt.savefig("time_" + b + "_" + metric + ".pdf", dpi=400, format='pdf')
        plt.show()


def plot_maxdiv_lns_time_subplots(d_maxdiv, d_lns, bs, metric, field, agap, relax):
    arch = 'mips'
    rel = str(relax)
    agap = str(agap)
    l = dict()
    fig = plt.figure()


    def plot_one(b, ax):
        # MaxDiversekSet
        algo = 'dfs'
        br   = 'cloriginal'
        if (d_maxdiv[b].has_key(arch) and d_maxdiv[b][arch].has_key(algo) and d_maxdiv[b][arch][algo].has_key(metric) and d_maxdiv[b][arch][algo][metric].has_key(agap) and d_maxdiv[b][arch][algo][metric][agap].has_key(br) and d_maxdiv[b][arch][algo][metric][agap][br][None].has_key(field)):
            cdict = dict(**d_maxdiv[b][arch][algo][metric][agap][br][None][field])

            # confidence interval
            k = sorted(cdict.keys())
            xy = [ (i, cdict[i]['stime'], 2*cdict[i]['stime_stdev']/math.sqrt(cdict[i]['n'])) for i in  k]
            if len(xy) > 0:
                x,y,err = zip(*xy)
                ax.errorbar(x, y, yerr=err, linestyle=':', color='k', label='MaxDiversekSet')
        # Random Search
        algo = 'dfs'
        br   = 'clrandom'
     
        if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(None) and d_lns[b][arch][algo][metric][agap][br][None].has_key(field)):
            cdict = dict(**d_lns[b][arch][algo][metric][agap][br][None][field])
            k = sorted(cdict.keys())
            xy = [ (i, cdict[i]['stime'], 2*cdict[i]['stime_stdev']/math.sqrt(cdict[i]['n'])) for i in  k]
            if len(xy) > 0:
                x,y,err = zip(*xy)
                ax.errorbar(x, y, yerr=err, linestyle='-.', color='k', label='Random Search')
     
        # LNS
        algo = 'lns'
        br   = 'clrandom'
     
        if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(rel) and d_lns[b][arch][algo][metric][agap][br][rel].has_key(field)):
            cdict = dict(**d_lns[b][arch][algo][metric][agap][br][rel][field])
            k = sorted(cdict.keys())
            xy = [ (i, cdict[i]['stime'], 2*cdict[i]['stime_stdev']/math.sqrt(cdict[i]['n'])) for i in k]
            if len(xy) > 0:
                x,y,err = zip(*xy)
                ax.errorbar(x, y, yerr=err, linestyle='--', color='k', label='LNS')
                
    for i,b in enumerate(bs,1):
        ax = plt.subplot(math.ceil(len(bs)/2.), 2, i)
        plot_one(b, ax)
        ax.set_yscale('log')
        ax.legend(loc='lower right')
        ax.set_ylim(bottom=1)
        ax.set_xlabel("Number of variants (k)")
        ax.set_ylabel(get_ind('stime'))
        plt.title(b)

    #ax.set_yscale('log')
    #plt.legend(loc='center right')

    #plt.title(bs)

    plt.suptitle("Measurement for solving time with optimality gap %s%%, LNS with relax rate %f" %(agap,relax), fontsize='large')
    plt.subplots_adjust(hspace=0.5)
    plt.show()


def plot_maxdiv_lns_dist_subplots(d_maxdiv, d_lns, bs, metric, field, agap, relax):
    arch = 'mips'
    rel = str(relax)
    agap = str(agap)
    l = dict()
    fig = plt.figure()


    def plot_one(b, ax):
        # MaxDiversekSet
        algo = 'dfs'
        br   = 'cloriginal'
        if (d_maxdiv[b].has_key(arch) and d_maxdiv[b][arch].has_key(algo) and d_maxdiv[b][arch][algo].has_key(metric) and d_maxdiv[b][arch][algo][metric].has_key(agap) and d_maxdiv[b][arch][algo][metric][agap].has_key(br) and d_maxdiv[b][arch][algo][metric][agap][br][None].has_key(field)):
            cdict = dict(**d_maxdiv[b][arch][algo][metric][agap][br][None][field])

            # confidence interval
            k = sorted(cdict.keys())
            xy = [ (i, cdict[i]['num'], 2*cdict[i]['stdev']/math.sqrt(cdict[i]['n'])) for i in  k]
            if len(xy) > 0:
                x,y,err = zip(*xy)
                ax.errorbar(x, y, yerr=err, linestyle=':', color='k', label='MaxDiversekSet')
        # Random Search
        algo = 'dfs'
        br   = 'clrandom'
     
        if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(None) and d_lns[b][arch][algo][metric][agap][br][None].has_key(field)):
            cdict = dict(**d_lns[b][arch][algo][metric][agap][br][None][field])
            k = sorted(cdict.keys())
            xy = [ (i, cdict[i]['num'], 2*cdict[i]['stdev']/math.sqrt(cdict[i]['n'])) for i in  k]
            if len(xy) > 0:
                x,y,err = zip(*xy)
                ax.errorbar(x, y, yerr=err, linestyle='-.', color='k', label='Random Search')
     
        # LNS
        algo = 'lns'
        br   = 'clrandom'
     
        if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(rel) and d_lns[b][arch][algo][metric][agap][br][rel].has_key(field)):
            cdict = dict(**d_lns[b][arch][algo][metric][agap][br][rel][field])
            k = sorted(cdict.keys())
            xy = [ (i, cdict[i]['num'], 2*cdict[i]['stdev']/math.sqrt(cdict[i]['n'])) for i in k]
            if len(xy) > 0:
                x,y,err = zip(*xy)
                ax.errorbar(x, y, yerr=err, linestyle='--', color='k', label='LNS')
                
    for i,b in enumerate(bs,1):
        ax = plt.subplot(math.ceil(len(bs)/2.), 2, i)
        plot_one(b, ax)
        ax.legend(loc='lower right')
        ax.set_ylim(bottom=1)
        ax.set_ylabel(get_ind(field))
        ax.set_xlabel("Number of variants (k)")
        plt.title(b)

    dist = get_name(field)
    plt.suptitle("Measurement for %s distance with optimality gap %s%%, LNS with relax rate %f" %(dist, agap,relax), fontsize='large')
    plt.subplots_adjust(hspace=0.5)
    #ax.set_yscale('log')
    #plt.legend(loc='center right')

    #plt.title(bs)

    plt.show()


def plot_coefficient_of_variation(d_maxdiv, d_lns, b, metric, field, agap, relax, dist=True):
    arch = 'mips'
    rel = str(relax)
    agap = str(agap)
    l = dict()
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    if dist:
        stdev = 'stdev'
        mean = 'num'
    else:
        stdev = 'stime_stdev'
        mean = 'stime'
    # MaxDiversekSet
    algo = 'dfs'
    br   = 'cloriginal'
 
    if (d_maxdiv[b].has_key(arch) and d_maxdiv[b][arch].has_key(algo) and d_maxdiv[b][arch][algo].has_key(metric) and d_maxdiv[b][arch][algo][metric].has_key(agap) and d_maxdiv[b][arch][algo][metric][agap].has_key(br) and d_maxdiv[b][arch][algo][metric][agap][br][None].has_key(field)):
        cdict = dict(**d_maxdiv[b][arch][algo][metric][agap][br][None][field])
        k = sorted(cdict.keys())
        xy = [ (i, cdict[i][stdev]/cdict[i][mean] if cdict[i][mean]>0 else 0) for i in  k]
        if len(xy) > 0:
            x,y = zip(*xy)
            plt.plot(x, y, linestyle=':', color='k', label='MaxDiversekSet')

    # Random search
    algo = 'dfs'
    br   = 'clrandom'
 
    if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(None) and d_lns[b][arch][algo][metric][agap][br][None].has_key(field)):
        cdict = dict(**d_lns[b][arch][algo][metric][agap][br][None][field])
        k = sorted(cdict.keys())
        xy = [ (i, cdict[i][stdev]/cdict[i][mean] if cdict[i][mean]>0 else 0) for i in  k]
        if len(xy) > 0:
            x,y = zip(*xy)
            plt.plot(x, y, linestyle='-.', color='k', label='Random Search')
 
    # LNS
    algo = 'lns'
    br   = 'clrandom'
 
    if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(rel) and d_lns[b][arch][algo][metric][agap][br][rel].has_key(field)):
        cdict = dict(**d_lns[b][arch][algo][metric][agap][br][rel][field])
        k = sorted(cdict.keys())
        xy = [ (i, cdict[i][stdev]/cdict[i][mean] if cdict[i][mean]>0 else 0) for i in  k]
        if len(xy) > 0:
            x,y = zip(*xy)
            plt.plot(x, y, linestyle='--', color='darkorange', label='LNS')
                

    ax.set_ylim(bottom=0)
    ax.set_ylabel(r'$\frac{\sigma}{\mu}$')
    ax.set_xlabel("Number of Variants (k)")
    ax.legend(loc='lower right')
    plt.title(b)
    fig.set_size_inches(18.5/3, 12.5/3)
    plt.savefig("cf_dist_" + b + "_" + metric + ".pdf", dpi=400, format='pdf')
    #plt.legend(loc='center right')


    plt.show()


def plot_maxdiv_lns_all_dist(d_maxdiv, d_lns, metric, field, agap, relax, benchmarks, colors):
    arch = 'mips'
    rel = str(relax)
    agap = str(agap)
    l = dict()
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    # colors = ['darkorange', 'darkred', 'darkgreen', 'royalblue', 'darkorchid', 'crimson', 'olive', 'yellowgreen']
    for b, color in zip(benchmarks, colors):
        print b, color



        # MaxDiversekSet
        algo = 'dfs'
        br   = 'cloriginal'
     
        if (d_maxdiv[b].has_key(arch) and d_maxdiv[b][arch].has_key(algo) and d_maxdiv[b][arch][algo].has_key(metric) and d_maxdiv[b][arch][algo][metric].has_key(agap) and d_maxdiv[b][arch][algo][metric][agap].has_key(br) and d_maxdiv[b][arch][algo][metric][agap][br][None].has_key(field)):
            cdict = dict(**d_maxdiv[b][arch][algo][metric][agap][br][None][field])
            k = sorted(cdict.keys())
            xy = [ (i, cdict[i]['num']/cdict[i]['maxnum'], 2*cdict[i]['stdev']/cdict[i]['maxnum']/math.sqrt(cdict[i]['n'])) for i in  k]
            if len(xy) > 0:
                x,y,err = map(np.array,zip(*xy))
                plt.plot(x, y, linestyle=':', color='r', label=b + '(MaxDiversekSet)')
                plt.fill_between(x, y-err, y+err, linestyle=':', color='r', alpha = 0.2)
     
                #x,y,err = zip(*xy)
                #plt.errorbar(x, y, alpha=0.9, linestyle=':', color=color, label='MaxDiversekSet')

        # Random search
        algo = 'dfs'
        br   = 'clrandom'
     
        if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(None) and d_lns[b][arch][algo][metric][agap][br][None].has_key(field)):
            cdict = dict(**d_lns[b][arch][algo][metric][agap][br][None][field])
            k = sorted(cdict.keys())
            xy = [ (i, cdict[i]['num']/cdict[i]['maxnum'], 2*cdict[i]['stdev']/cdict[i]['maxnum']/math.sqrt(cdict[i]['n'])) for i in  k]
            if len(xy) > 0:
                x,y,err = map(np.array,zip(*xy))
                plt.plot(x, y, linestyle='-', color='g', label= b + '(random)')
                plt.fill_between(x, y-err, y+err, linestyle=':', color='g', alpha = 0.2)
     
        # LNS
        algo = 'lns'
        br   = 'clrandom'
     
        if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(rel) and d_lns[b][arch][algo][metric][agap][br][rel].has_key(field)):
            cdict = dict(**d_lns[b][arch][algo][metric][agap][br][rel][field])
            k = sorted(cdict.keys())
            xy = [ (i, cdict[i]['num']/cdict[i]['maxnum'], 2*cdict[i]['stdev']/cdict[i]['maxnum']/math.sqrt(cdict[i]['n'])) for i in k ]
            if len(xy) > 0:
                x,y,err = map(np.array,zip(*xy))
                plt.plot(x, y, linestyle='-.', color='b', label=b + '(LNS)')
                plt.fill_between(x, y-err, y+err, linestyle=':', color='b', alpha = 0.2)
                    

    ax.set_ylim(bottom=0)
    ax.set_ylabel(get_ind(field))
    ax.set_xlabel("Number of Variants (k)")
    ax.legend(loc='lower right')
    fig.set_size_inches(18.5/3, 12.5/3)
    plt.savefig("dist_" + b + "_" + metric + ".pdf", dpi=400, format='pdf')
    #plt.legend(loc='center right')

    plt.title(b)

    plt.show()


def plot_maxdiv_lns_aggregaded( d_lns, metric, field, agap, relax, benchmarks, colors, loc='upper right', dist=True):
    arch = 'mips'
    agap = str(agap)
    l = dict()
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    maxdiv = dict()
    random = dict()
    lns = dict()

    if dist:
        mean = 'num'
    else:
        mean = 'stime'
    # colors = ['darkorange', 'darkred', 'darkgreen', 'royalblue', 'darkorchid', 'crimson', 'olive', 'yellowgreen']
    for b in benchmarks:


        # Random search
        algo = 'dfs'
        br   = 'clrandom'
     
        if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(None) and d_lns[b][arch][algo][metric][agap][br][None].has_key(field)):
            cdict = dict(**d_lns[b][arch][algo][metric][agap][br][None][field])
            k = sorted(cdict.keys())

            for i in k:
                if not cdict[i].has_key(mean):
                    continue

                val = cdict[i][mean]
# 
                if random.has_key(i):
                    random[i].append((1.*val)/val)
                else:
                    random[i] = [(1.*val)/val]

                # LNS
                algo = 'lns'
                br   = 'clrandom'
         
                for rel in relax:

                    rel = str(rel)
                    if not lns.has_key(rel):
                            lns[rel] = dict()

                    if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(rel) and d_lns[b][arch][algo][metric][agap][br][rel].has_key(field)) and d_lns[b][arch][algo][metric][agap][br][rel][field].has_key(i):
                        lnsdict = dict(**d_lns[b][arch][algo][metric][agap][br][rel][field][i])
                        #k = sorted(cdict.keys())


                        lnsval = (1.0*lnsdict[mean])/val

                        if lns[rel].has_key(i):
                            lns[rel][i].append(lnsval)
                        else:
                            lns[rel][i] = [lnsval]

    x = sorted(random)
    mi = [ np.prod(random[i])**(1./len(random[i])) for i in x]
    if len(x) > 0:
        plt.plot(x, mi, linewidth=1.5, linestyle='-', color=colors[0], label='Random search')


    c = 1
    mval = 1
    for rel in sorted(lns):
        x = sorted(lns[rel])
        mi = [ np.prod(lns[rel][i])**(1./len(lns[rel][i]))  for i in x ]
        err = [ geometric_conf_interval(lns[rel][i]) for i in x ]
        #stdev = [ sum([(j-mi[ii])**2 for j in lns[rel][i]])/(len(lns[rel][i])-1) for ii,i in enumerate(x) if i in random]
        #err  = [ 2*stdev[ii]/math.sqrt(len(lns[rel][i])) for ii, i in enumerate(x) if i in random]
        if len(x) > 0:
            ermin, erplus = zip(*err)
            plt.plot(x, mi,  linewidth=1.5, linestyle='-', color=colors[c], label='LNS, relax=' + rel)
            mval = max(mval, max(mi))
            if not None in ermin:
                plt.fill_between(x, ermin, erplus, linestyle='-.', color=colors[c], alpha = 0.1)
            c += 1


    ax.set_ylim(bottom=0,top=1.1*mval)
    ax.set_ylabel('LNS/RA')
    ax.set_xlabel("Number of Variants (k)")
    ax.legend(loc=loc)
    plt.title('Geometric Mean for all benchmarks (%s).' %get_name(field), fontsize=12)
    fig.set_size_inches(18.5/3, 12.5/3)
    # fig.set_size_inches(18.5/1.5, 9.5/1.5)
    plt.savefig("geometric_mean_" + ("dist" if dist else "time") + "_" + metric + ".pdf", dpi=400, format='pdf')
    #plt.legend(loc='center right')


    plt.show()


