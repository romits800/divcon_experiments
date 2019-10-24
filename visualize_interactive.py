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


def improvement(lns, dfs):
    if (lns >= dfs):
	if dfs == 0:
		return -1
        return round((float) ((lns-dfs)/dfs)*100,2)
    else:
        if lns == 0:
		return -1
	return -round((float) ((dfs-lns)/lns)*100,2)

def create_tex(texname, ind, field, relax, title, d, metric, agap):
    '''
	texname: name of the output file
	ind: name of the metric show in the table
	field: 'avg', 'bravg', 'brdiff' output metric
	relax: 0.4, 0.45, ..., 0.95 the relax rate
	title: Title of the table
	d: the dictionary with the measurements
		e.g. d = pickle.load(open("divs.pickle"))
	metric: the metric of the measurement (from unison)
	agap: 10, 20 allowed gap from the optimal solution
    ''' 
    agap = str(agap)
    relax = str(relax)

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
            mipsdfs = d[benchmark].has_key("mips") and d[benchmark]["mips"].has_key("dfs") and d[benchmark]["mips"]["dfs"].has_key(metric) and d[benchmark]["mips"]["dfs"][metric].has_key(agap) and d[benchmark]["mips"]["dfs"][metric][agap][None].has_key(field)
	    mipslns = d[benchmark].has_key("mips") and d[benchmark]["mips"].has_key("lns") and d[benchmark]["mips"]["lns"].has_key(metric) and d[benchmark]["mips"]["lns"][metric].has_key(agap) and d[benchmark]["mips"]["lns"][metric][agap].has_key(relax) and d[benchmark]["mips"]["lns"][metric][agap][relax].has_key(field)
            hexagondfs = d[benchmark].has_key("hexagon") and d[benchmark]["hexagon"].has_key("dfs") and d[benchmark]["hexagon"]["dfs"].has_key(metric) and d[benchmark]["hexagon"]["dfs"][metric].has_key(agap) and d[benchmark]["hexagon"]["dfs"][metric].has_key(agap)
            hexagonlns = d[benchmark].has_key("hexagon") and d[benchmark]["hexagon"].has_key("lns") and d[benchmark]["hexagon"]["lns"].has_key(metric) and d[benchmark]["hexagon"]["lns"][metric].has_key(agap) and d[benchmark]["hexagon"]["lns"][metric][agap].has_key(relax) and d[benchmark]["hexagon"]["lns"][metric][agap][relax].has_key(field)

            arg1 = "-"
            arg2 = "-"
            if mipsdfs:
                nrelax = None
                dfsnum = d[benchmark]["mips"]["dfs"][metric][agap][nrelax][field]['num']
                dfsmaxnum = d[benchmark]["mips"]["dfs"][metric][agap][nrelax][field]['maxnum']
                dfsdivs = d[benchmark]["mips"]["dfs"][metric][agap][nrelax]["divs"]
                arg1 = "%.2f\\textbackslash %d (%d)" %(dfsnum, dfsmaxnum, dfsdivs)

                c["mips"]["dfs"]["sum"] += d[benchmark]["mips"]["dfs"][metric][agap][nrelax][field]['num']
                c["mips"]["dfs"]["count"] += 1

            if mipslns:
                lnsnum = d[benchmark]["mips"]["lns"][metric][agap][relax][field]['num']
                lnsmaxnum = d[benchmark]["mips"]["lns"][metric][agap][relax][field]['maxnum']
                lnsdivs = d[benchmark]["mips"]["lns"][metric][agap][relax]["divs"]
                arg2 = "%.2f\\textbackslash %d (%d)" %(lnsnum, lnsmaxnum, lnsdivs)
                c["mips"]["lns"]["sum"]+= d[benchmark]["mips"]["lns"][metric][agap][relax][field]['num']
                c["mips"]["lns"]["count"] += 1

            impr1 = "-"
            if mipslns and mipsdfs:
                nrelax = None
                lnsnum = d[benchmark]["mips"]["lns"][metric][agap][relax][field]['num']
                dfsnum = d[benchmark]["mips"]["dfs"][metric][agap][nrelax][field]['num']
                impr1 = "%.2f" %improvement(lnsnum, dfsnum)

            #arg2 = str(d[benchmark]["mips"]["lns"][relax][field]['num']) + "\\textbackslash " + str(d[benchmark]["mips"]["lns"][relax][field]['maxnum']) + " (" + str(d[benchmark]["mips"]["lns"]["divs"]) + ")" if mipslns and mipsdfs else "-"

            arg3 = "-"
            arg4 = "-"
            if hexagondfs:
                nrelax = None
                dfsnum = d[benchmark]["hexagon"]["dfs"][metric][agap][nrelax][field]['num']
                dfsmaxnum = d[benchmark]["hexagon"]["dfs"][metric][agap][nrelax][field]['maxnum']
                dfsdivs = d[benchmark]["hexagon"]["dfs"][metric][agap][nrelax]["divs"]
                arg3 = "%.2f\\textbackslash %d (%d)" %(dfsnum, dfsmaxnum, dfsdivs)

                c["hexagon"]["dfs"]["sum"] += d[benchmark]["hexagon"]["dfs"][metric][agap][nrelax][field]['num']
                c["hexagon"]["dfs"]["count"] += 1
                
            if hexagonlns: 
                lnsnum = d[benchmark]["hexagon"]["lns"][metric][agap][relax][field]['num']
                lnsmaxnum = d[benchmark]["hexagon"]["lns"][metric][agap][relax][field]['maxnum']
                lnsdivs = d[benchmark]["hexagon"]["lns"][metric][agap][relax]["divs"]
                arg4 = "%.2f\\textbackslash %d (%d)" %(lnsnum, lnsmaxnum, lnsdivs)
                c["hexagon"]["lns"]["sum"]+= d[benchmark]["hexagon"]["lns"][metric][agap][relax][field]['num']
                c["hexagon"]["lns"]["count"] += 1

            impr2 = "-"
            if hexagonlns and hexagondfs:
                lnsnum = d[benchmark]["hexagon"]["lns"][metric][agap][relax][field]['num']
                dfsnum = d[benchmark]["hexagon"]["dfs"][metric][agap][None][field]['num']
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

 

def plot_all(field, relax, d, yvalue, title, metric, agap):
    '''
	field: 'avg', 'bravg', 'brdiff' output metric
	relax: 0.4, 0.45, ..., 0.95 the relax rate
	d: the dictionary with the measurements
		e.g. d = pickle.load(open("divs.pickle"))
	yvalue: value on the y axis
	title: Title of the plot
	metric: the metric of the measurement (from unison)
	agap: 10, 20 allowed gap from the optimal solution
    '''
    agap = str(agap)
    relax = str(relax)

    def constr(b, arch, method):
	rel = None if method == "dfs" else relax
        return d[b].has_key(arch) and d[b][arch].has_key(method) and d[b][arch][method].has_key(metric) and d[b][arch][method][metric].has_key(agap) and d[b][arch][method][metric][agap].has_key(rel) and d[b][arch][method][metric][agap][rel].has_key(field)


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
        dfs_means = [d[b][arch]["dfs"][metric][agap][None][field]['num'] if constr(b, arch, "dfs") else 0 for b in d]
        lns_means = [d[b][arch]["lns"][metric][agap][relax][field]['num'] if constr(b, arch, "lns") else 0 for b in d]

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

    plt.subplots_adjust(hspace=0.5)

    plt.show()



def plot_hist(field, relax, d, yvalue, title, metric, agap):
    '''
	field: 'avg', 'bravg', 'brdiff' output metric
	relax: 0.4, 0.45, ..., 0.95 the relax rate
	d: the dictionary with the measurements
		e.g. d = pickle.load(open("divs.pickle"))
	yvalue: value on the y axis
	title: Title of the plot
	metric: the metric of the measurement (from unison)
	agap: 10, 20 allowed gap from the optimal solution
    '''
    agap = str(agap)
    relax = str(relax)


    def constr(b, arch,  method):
	rel = None if method == "dfs" else relax
        return d[b].has_key(arch) and d[b][arch].has_key(method) and d[b][arch][method].has_key(metric) and d[b][arch][method][metric].has_key(agap) and d[b][arch][method][metric][agap].has_key(rel) and d[b][arch][method][metric][agap][rel].has_key(field)


    def plot_arch(d, arch, ax):

        labels = d.keys()

        dfs = [d[b][arch]["dfs"][metric][agap][None][field]['data'] if constr(b, arch, "dfs") else [0] for b in d]
        lns = [d[b][arch]["lns"][metric][agap][relax][field]['data'] if constr(b, arch, "lns") else [0] for b in d]

        x = 2*np.arange(len(labels)) + 0.5 # the label locations
        width = 0.35  # the width of the bars

        lines = []

        offset = 0
        for b in labels:
            datalns = [0]
            datadfs = [0]
            if constr(b, arch, "dfs"):
                datadfs = d[b][arch]["dfs"][metric][agap][None][field]['data']

            if constr(b, arch, "lns"):
                datalns = d[b][arch]["lns"][metric][agap][relax][field]['data']

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

            n, bins, patches = ax.hist(xxdfs, num_bins_dfs, normed=True, alpha=0.5, facecolor = 'blue',  label='DFS')
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




def plot_relax(field, d, yvalue, title, metric, agap):
    '''
	field: 'avg', 'bravg', 'brdiff' output metric
	d: the dictionary with the measurements
		e.g. d = pickle.load(open("divs.pickle"))
	yvalue: value on the y axis
	title: Title of the plot
	metric: the metric of the measurement (from unison)
	agap: 10, 20 allowed gap from the optimal solution
    '''
    agap = str(agap)


    def constr(b, arch, method):
	if method == "dfs":
        	return d[b].has_key(arch) and d[b][arch].has_key(method) and d[b][arch][method].has_key(metric) and d[b][arch][method][metric].has_key(agap) and d[b][arch][method][metric][agap].has_key(None) and d[b][arch][method][metric][agap][None].has_key(field)
	else:
        	return d[b].has_key(arch) and d[b][arch].has_key(method) and d[b][arch][method].has_key(metric) and d[b][arch][method][metric].has_key(agap) and len(d[b][arch][method][metric][agap]) > 0 and d[b][arch][method][metric][agap][ d[b][arch][method][metric][agap].keys()[0]   ].has_key(field)



    def plot_arch(d, b, arch, ax):

        labels = d.keys()
        if constr(b, arch, "lns"):
            lns = [(r, d[b][arch]["lns"][metric][agap][str(r)][field]['num'])  for r in sorted(map(float,d[b][arch]["lns"][metric][agap].keys())) ]

            x,y = zip(*lns)

            # print b, x, y
            ax.plot(x,y, linewidth=1.5, label="LNS")

            if constr(b, arch, "dfs"):
                v = d[b][arch]["dfs"][metric][agap][None][field]['num']
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

def plot_relax_all(field, d, yvalue, title, metric, agap):
    '''
	field: 'avg', 'bravg', 'brdiff' output metric
	d: the dictionary with the measurements
		e.g. d = pickle.load(open("divs.pickle"))
	yvalue: value on the y axis
	title: Title of the plot
	metric: the metric of the measurement (from unison)
	agap: 10, 20 allowed gap from the optimal solution
    '''
    agap = str(agap)


    def constr(b, arch, method):
	if method == "dfs":
        	return d[b].has_key(arch) and d[b][arch].has_key(method) and d[b][arch][method].has_key(metric) and d[b][arch][method][metric].has_key(agap) and d[b][arch][method][metric][agap].has_key(None) and d[b][arch][method][metric][agap][None].has_key(field)
	else:
        	return d[b].has_key(arch) and d[b][arch].has_key(method) and d[b][arch][method].has_key(metric) and d[b][arch][method][metric].has_key(agap) and len(d[b][arch][method][metric][agap]) > 0 and d[b][arch][method][metric][agap][ d[b][arch][method][metric][agap].keys()[0]   ].has_key(field)

    def plot_arch(d, arch, ax):

        labels = d.keys()
	rs = []
        for r in np.arange(0.4,1.0, 0.05):
		nums = [d[b][arch]["lns"][metric][agap][str(r)][field]['num'] for b in d if constr(b, arch, "lns")]	
		if len(nums)> 0:
			rs.append((r, sum(nums)/len(nums)))

        x,y = zip(*rs)

            # print b, x, y
        ax.plot(x,y, linewidth=1.5, label="LNS")

	v = []
        if constr(b, arch, "dfs"):
                v = d[b][arch]["dfs"][metric][agap][None][field]['num']
                ax.plot(x, [v for _ in x], linewidth=1.5, label="DFS");

        ymax = max(list(y)+[v])
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



# # Table
# 
# if (s_out in ["hamming", "all"] and s_relax != "all"):
#     title = "Hamming distance for %s, %s, %s, %s" %(s_metric, s_agap, s_constant, s_relax)
#     create_tex("out_hamming",       "hamm",    "avg", s_relax, title, d, s_metric, s_agap)
# 
# if (s_out in ["br_hamming", "all"] and s_relax != "all"):
#     title = "Hamming distance of branch instructions for %s, %s, %s, %s" %(s_metric, s_agap, s_constant, s_relax)
#     create_tex("out_brhamming",     "brhamm",    "bravg",  s_relax, title, d, s_metric, s_agap)
# 
# if (s_out in ["diff_br_hamming", "all"] and s_relax != "all"):
#     title = "Hamming distance of difference to branch instructions for %s, %s, %s, %s" %(s_metric, s_agap, s_constant, s_relax)
#     create_tex("out_diffbrhamming", "diffhamm",  "brdiff",  s_relax, title, d, s_metric, s_agap)
# 
# if (s_out in ["cost", "all"] and s_relax != "all"):
#     title = "Cost in cycles for %s, %s, %s, %s" %(s_metric, s_agap, s_constant, s_relax)
#     create_tex("out_cost", "cost",  "cost",  s_relax, title, d, s_metric, s_agap)
# 
# 
# # if (s_out in ["stime", "all"]):
# #     title = "Execution time (s) of the generation of the last variant for %s, %s, %s, %s" %(s_metric, s_agap, s_constant, s_relax)
# #     create_tex("out_stime",        "ms",        "stime",  title, d)
# 
# # Plot
# if (s_out in ["hamming", "all"] and s_relax != "all"):
#     plot_all("avg",    s_relax, d, "Hamming Distance", 'Hamming Distance between DFS LNS', s_metric, s_agap)
# 
# if (s_out in ["br_hamming", "all"] and s_relax != "all"):
#     plot_all("bravg",  s_relax, d,  "Hamming Distance", 'Branch Hamming Distance between DFS LNS', s_metric, s_agap)
# 
# if (s_out in ["diff_br_hamming", "all"] and s_relax != "all"):
#     plot_all("brdiff", s_relax, d,  "Hamming Distance", 'Diff Branch Hamming Distance between DFS LNS', s_metric, s_agap)
# 
# if (s_out in ["stime", "all"] and s_relax != "all"):
#     plot_all("stime", s_relax, d,  "Solver Time", 'Solver time', s_metric, s_agap)
# 
# if (s_out in ["cost", "all"] and s_relax != "all"):
#     plot_all("cost", s_relax, d,  "Cost (cycles)", 'Cost (cycles)', s_metric, s_agap)
# 
# 
# 
# if (s_out in ["hamming", "all"] and s_relax != "all"):
#     plot_hist("avg",    s_relax, d,  "Hamming Distance", 'Hamming Distance between DFS LNS', s_metric, s_agap)
# 
# if (s_out in ["br_hamming", "all"] and s_relax != "all"):
#     plot_hist("bravg",  s_relax, d,  "Hamming Distance", 'Branch Hamming Distance between DFS LNS', s_metric, s_agap)
# 
# if (s_out in ["diff_br_hamming", "all"] and s_relax != "all"):
#     plot_hist("brdiff", s_relax, d,  "Hamming Distance", 'Diff Branch Hamming Distance between DFS LNS', s_metric, s_agap)
# 
# if (s_out in ["stime", "all"] and s_relax != "all"):
#     plot_hist("stime", s_relax, d,  "Solver Time", 'Solver time', s_metric, s_agap)
# 
# if (s_out in ["cost", "all"] and s_relax != "all"):
#     plot_hist("cost", s_relax, d,  "Cost (cycles)", 'Cost (cycles)', s_metric, s_agap)
# 
# 
# 
# if (s_out in ["hamming", "all"] and s_relax == "all"):
#     plot_relax("avg", d, "Hamming Distance", "Hamming distance for different relax rates (0.4, 0.45, ..., 0.95)", s_metric, s_agap)
# 
# if (s_out in ["br_hamming", "all"] and s_relax == "all"):
#     plot_relax("bravg", d,  "Hamming Distance", 'Branch Hamming Distance for different relax rates (0.4, 0.45, ..., 0.95)', s_metric, s_agap)
# 
# if (s_out in ["diff_br_hamming", "all"] and s_relax == "all"):
#     plot_relax("brdiff",  d,  "Hamming Distance", 'Diff Branch Hamming Distance for different relax rates (0.4, 0.45, ..., 0.95)', s_metric, s_agap)
# 
# if (s_out in ["stime", "all"] and s_relax == "all"):
#     plot_relax("stime",  d,  "Diversify Time", 'Diversify time for different relax rates (0.4, 0.45, ..., 0.95)', s_metric, s_agap)
# 
# if (s_out in ["cost", "all"] and s_relax == "all"):
#     plot_relax("cost", d, "Cost (cycles)", "Cost (cycles) for different relax rates (0.4, 0.45, ..., 0.95)", s_metric, s_agap)
# 
