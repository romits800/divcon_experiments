#!/usr/bin/python

from os import listdir

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from mpl_toolkits.mplot3d import Axes3D
from uncertainties import ufloat

import json

import sys

import pickle
import re

import subprocess

import getopt

import math

benchmarks = sorted([   "h264ref.sei.UpdateRandomAccess",
                        "hmmer.tophits.AllocFancyAli",
                        "gobmk.board.get_last_player",
                        "gcc.expmed.ceil_log2",
                        "h264ref.vlc.symbol2uvlc",
                        "gobmk.patterns.autohelperpat1088",
                        "gobmk.owl_attackpat.autohelperowl_attackpat68",
                        "gobmk.owl_defendpat.autohelperowl_defendpat421",
                        "gcc.xexit.xexit",
                        "gcc.rtlanal.parms_set",
                        "gcc.alias.get_frame_alias_set",
                        "mesa.api.glVertex2i",
                        "gcc.jump.unsigned_condition",
                        "sphinx3.glist.glist_tail",
                        "sphinx3.profile.ptmr_init",
                        "mesa.api.glIndexd",
                        "gobmk.owl_vital_apat.autohelperowl_vital_apat34"])

dbench = dict()
for bi,b in enumerate(benchmarks,1):
    dbench[b] = "b%d"%bi

rrates = [ "-",  "0.05", "0.1", "0.15", "0.2", "0.25", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9"]
#rrates = [ "-", "0.1", "0.2", "0.4", "0.6", "0.8", "0.9"]

def dist_to_delta(dist):
	if dist == "reg_hamming":
		return r'$\delta_r$'
	elif dist == "hamming":
		return r'$\delta_c$'
	elif dist == "br_hamming":
		return r'$\delta_{bh}$'
	elif dist == "levenshtein":
		return r'$\delta_{lev}$'
	else:
		return r'$\delta$'



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

def tex_max_lns_rs(d, metric, field, agap, num, mindist, relax, texname='outfile', debug=False, show=True):
    '''
	d: the dictionary with the measurements
		e.g. d = pickle.load(open("divs.pickle"))
	metric: the metric of the measurement (from divcon - unison)
	field: 'avg', 'bravg', 'brdiff' output metric
	agap: 10, 20 allowed gap from the optimal solution
	branch: original, random, cloriginal, clrandom
        texname: name of the output .tex file - default = 'outfile'
    ''' 
    agap = str(agap)

    ind = get_ind(field)

    title = "%s for measurements of (%s, %s%%)" %(ind.capitalize(), metric, str(agap))


    def get_fields(benchmark, arch, heuristic, metric, agap, branch, relax, mindist, field, num, avg, stdev):
	mnum = d[benchmark][arch][heuristic][metric][agap][branch][relax][mindist][field][num][avg]
	#mnum = mnum if dist else maxnum/1000.
	mstd = d[benchmark][arch][heuristic][metric][agap][branch][relax][mindist][field][num][stdev]
	#maxstd = maxstd if dist else maxstd/1000.
	mseeds = d[benchmark][arch][heuristic][metric][agap][branch][relax][mindist][field][num]["n"]
	return (mnum, mstd, mseeds)

    names = sorted(d.keys())
    with open(texname + '.tex', 'w') as f:
	if show:
		print >> f, "\\documentclass{standalone}"
		print >> f, "\\usepackage{multirow}"
		print >> f, "\\usepackage{longtable}"
		print >> f, "\\begin{document}"
        print >> f, "\\begin{longtable}{|l|%s}"%("c|"*2*(len(relax)+2)) 
	print >> f, '''\\caption{\label{tab:dist_max_rs_lns} Evaluation of \\ac{LNS} with \\ac{RS} and \\textsc{MaxDiverse$k$Set}
		for 200 variants. \\textbf{Bold} text indicates the highest value of pairwise distance $d$
		and lowest diversification time. \\textit{Italic} text indicates that the algorithm was not able to generate
		200 variants, with the number in parenthesis indicating how many variants the algorithm generates in average.}\\\\'''
        print >> f, "\\hline" 
        print >> f, "&\\multicolumn{2}{c|}{\\textsc{MaxDiverse$k$Set}}&\\multicolumn{2}{c|}{{RS}}&\\multicolumn{%d}{c|}{LNS (0.7)}\\\\" %(2*len(relax)) 
        #print >> f, "\\cline{6-%d}"%(5+len(relax)*2)
        #print >> f, "&%s&%s\\\\" %( "&".join(["\\multicolumn{2}{c|}{}", "\\multicolumn{2}{c|}{}"]), "&".join(map(lambda x: "\\multicolumn{2}{c|}{%s}"%x, relax)))
        print >> f, "\\cline{2-%d}"%(5+len(relax)*2)
        print >> f, "&%s\\\\" %( "&".join([r"$d$", "time (s)"]*(len(relax)+2)))
    # MaxDiversekSet
       # print >> f, "&\\footnotesize dfs (%s\\textbackslash maxd (N))&\\footnotesize  lns (%s\\textbackslash maxd (N))&\\footnotesize  improv. \\%%  \\\\" %( ind, ind) 
        print >> f, "\\hline" 

        for bi,benchmark in enumerate(benchmarks,1):
	    branch = "cloriginal"
	    mipsm = d[benchmark].has_key("mips") and d[benchmark]["mips"].has_key("dfs") and d[benchmark]["mips"]["dfs"].has_key(metric) and d[benchmark]["mips"]["dfs"][metric].has_key(agap) and d[benchmark]["mips"]["dfs"][metric][agap].has_key(branch) and d[benchmark]["mips"]["dfs"][metric][agap][branch][None].has_key(mindist) and d[benchmark]["mips"]["dfs"][metric][agap][branch][None][mindist].has_key(field)
	    def mipsmax(num):
		branch = "cloriginal"
		return  mipsm and d[benchmark]["mips"]["dfs"][metric][agap][branch][None][mindist][field].has_key(num)
	    branch = "clrandom"
            mipsrs = d[benchmark].has_key("mips") and d[benchmark]["mips"].has_key("dfs") and d[benchmark]["mips"]["dfs"].has_key(metric) and d[benchmark]["mips"]["dfs"][metric].has_key(agap) and d[benchmark]["mips"]["dfs"][metric][agap].has_key(branch) and d[benchmark]["mips"]["dfs"][metric][agap][branch][None].has_key(mindist) and d[benchmark]["mips"]["dfs"][metric][agap][branch][None][mindist].has_key(field) 
	    def mipsrsnum(num):
		return mipsrs and d[benchmark]["mips"]["dfs"][metric][agap][branch][None][mindist][field].has_key(num)

            def mipslns(relax):
                #print relax
		branch = "clrandom"
                return d[benchmark].has_key("mips") and d[benchmark]["mips"].has_key("lns") and d[benchmark]["mips"]["lns"].has_key(metric) and d[benchmark]["mips"]["lns"][metric].has_key(agap) and d[benchmark]["mips"]["lns"][metric][agap].has_key(branch) and d[benchmark]["mips"]["lns"][metric][agap][branch].has_key(relax) and d[benchmark]["mips"]["lns"][metric][agap][branch][relax].has_key(mindist) and d[benchmark]["mips"]["lns"][metric][agap][branch][relax][mindist].has_key(field) 
	    def mipslnsnum(relax, num):
		return mipslns(relax) and d[benchmark]["mips"]["lns"][metric][agap][branch][relax][mindist][field].has_key(num) 


            arg = {r: "-" for r in relax + ["-", "max"]}
            argtime = {r: "-" for r in relax + ["-", "max"]}
            val = {r: 0 for r in relax + ["-", "max"] }
            valtime = {r: 0 for r in relax + ["-", "max"] }
	    branch = "cloriginal"
            if mipsmax(num):
		r = 'max'
                (maxnum,maxstd,maxnseeds) =  get_fields(benchmark, "mips", "dfs", metric, agap, "cloriginal", None, mindist, field, num, "num", "stdev") 
                (tmaxnum,tmaxstd,tmaxnseeds) =  get_fields(benchmark, "mips", "dfs", metric, agap, "cloriginal", None, mindist, field, num, "stime", "stime_stdev") 
		if debug:
			arg[r] = "%.2f$\\pm$%.2f (%d,%d)" %(maxnum, maxstd, num, maxnseeds)
			argtime[r] = "%.2f$\\pm$%.2f (%d,%d)" %(tmaxnum/1000., tmaxstd/1000., num, tmaxnseeds)
		else:
			arg[r] = "%.2f$\\pm$%.2f" %(maxnum, maxstd)
			argtime[r] = "%.2f$\\pm$%.2f" %(tmaxnum/1000., tmaxstd/1000.)
		val[r] = maxnum
		valtime[r] = tmaxnum
	    elif mipsm:
                keys = d[benchmark]["mips"]["dfs"][metric][agap][branch][None][mindist][field].keys()
                if len(keys) != 0: 
			maxn = max(keys)
			r = 'max'
			(maxnum,maxstd,maxnseeds) =  get_fields(benchmark, "mips", "dfs", metric, agap, "cloriginal", None, mindist, field, maxn, "num", "stdev") 
			(tmaxnum,tmaxstd,tmaxnseeds) =  get_fields(benchmark, "mips", "dfs", metric, agap, "cloriginal", None, mindist, field, maxn, "stime", "stime_stdev") 
			if debug:
				arg[r] = "\\textit{%.2f$\\pm$%.2f (%d,%d)}" %(maxnum, maxstd, maxn, maxnseeds)
				argtime[r] = "%.2f$\\pm$%.2f (%d,%d)" %(tmaxnum/1000., tmaxstd/1000., num, tmaxnseeds)
			else:
				arg[r] = "\\textit{%.2f$\\pm$%.2f}" %(maxnum, maxstd)
				argtime[r] = "\\textit{%.2f$\\pm$%.2f (%d)}" %(tmaxnum/1000., tmaxstd/1000., maxn)
			val[r] = maxnum
			valtime[r] = tmaxnum


	    branch = "clrandom"
            if mipsrsnum(num):
		r = '-'
		nrelax = None
                (rsnum,rsstd,rsnseeds) =  get_fields(benchmark, "mips", "dfs", metric, agap, branch, None, mindist, field, num, "num", "stdev") 
                (trsnum,trsstd,trsnseeds) =  get_fields(benchmark, "mips", "dfs", metric, agap, branch, None, mindist, field, num, "stime", "stime_stdev") 
	
		if debug:
			arg[r] = "%.2f$\\pm$%.2f (%d)" %(rsnum, rsstd, rsnseeds)
			argtime[r] = "%.2f$\\pm$%.2f (%d)" %(trsnum/1000., trsstd/1000., trsnseeds)
		else:
			arg[r] = "%.2f$\\pm$%.2f" %(rsnum, rsstd)
			argtime[r] = "%.2f$\\pm$%.2f" %(trsnum/1000., trsstd/1000.)

		val[r] = rsnum
		valtime[r] = trsnum
	    elif mipsrs:
                keys = d[benchmark]["mips"]["dfs"][metric][agap][branch][None][mindist][field].keys()
                if len(keys) != 0: 
			maxn = max(keys)
			r = '-'
			nrelax = None
			(rsnum,rsstd,rsnseeds) =  get_fields(benchmark, "mips", "dfs", metric, agap, branch, None, mindist, field, maxn, "num", "stdev") 
			(trsnum,trsstd,trsnseeds) =  get_fields(benchmark, "mips", "dfs", metric, agap, branch, None, mindist, field, maxn, "stime", "stime_stdev") 
		
			if debug:
				arg[r] = "\\textit{%.2f$\\pm$%.2f (%d)}" %(rsnum, rsstd, rsnseeds)
				argtime[r] = "\\textit{%.2f$\\pm$%.2f (%d)}" %(trsnum/1000., trsstd/1000., trsnseeds)
			else:
				arg[r] = "\\textit{%.2f$\\pm$%.2f}" %(rsnum, rsstd)
				argtime[r] = "\\textit{%.2f$\\pm$%.2f (%d)}" %(trsnum/1000., trsstd/1000., maxn)

			val[r] = rsnum
			valtime[r] = trsnum



            for r in relax:
                    if mipslnsnum(r, num):
			(lnsnum,lnsstd,lnsnseeds) =  get_fields(benchmark, "mips", "lns", metric, agap, branch, r, mindist, field, num, "num", "stdev") 
			(tlnsnum,tlnsstd,tlnsnseeds) =  get_fields(benchmark, "mips", "lns", metric, agap, branch, r, mindist, field, num, "stime", "stime_stdev") 
	
			if debug:
				arg[r] = "%.2f$\\pm$%.2f (%d)" %(lnsnum, lnsstd, lnsnseeds)
				argtime[r] = "%.2f$\\pm$%.2f (%d)" %(tlnsnum/1000., tlnsstd/1000., tlnsnseeds)
			else:
				arg[r] = "%.2f$\\pm$%.2f" %(lnsnum, lnsstd)
				argtime[r] = "%.2f$\\pm$%.2f" %(tlnsnum/1000., tlnsstd/1000.)
                        val[r] = lnsnum
                        valtime[r] = tlnsnum
                    elif mipslns(r):
                        keys = d[benchmark]["mips"]["lns"][metric][agap][branch][r][mindist][field].keys()
                        if len(keys) != 0:
				maxn = max(keys)
				(lnsnum,lnsstd,lnsnseeds) =  get_fields(benchmark, "mips", "lns", metric, agap, branch, r, mindist, field, maxn, "num", "stdev") 
				(tlnsnum,tlnsstd,tlnsnseeds) =  get_fields(benchmark, "mips", "lns", metric, agap, branch, r, mindist, field, maxn, "stime", "stime_stdev") 
		
				if debug:
					arg[r] = "\\textit{%.2f$\\pm$%.2f (%d)}" %(lnsnum, lnsstd, lnsnseeds)
					argtime[r] = "\\textit{%.2f$\\pm$%.2f (%d)}" %(tlnsnum/1000., tlnsstd/1000., tlnsnseeds)
				else:
					arg[r] = "\\textit{%.2f$\\pm$%.2f}" %(lnsnum, lnsstd)
					argtime[r] = "\\textit{%.2f$\\pm$%.2f (%d)}" %(tlnsnum/1000., tlnsstd/1000., maxn)
				val[r] = lnsnum
				valtime[r] = tlnsnum


            #vitems = filter(lambda (m,y): "textit" not in arg[m] and arg[m] == '-', val.items())
            vitems = filter(lambda (m,y): "textit" not in arg[m] and arg[m] != '-', val.items())
            
            if (len(vitems)>0) and (sum(zip(*vitems)[1]) > 0):
                mr, m = max(vitems, key=lambda (x,y): y)
                mrs,_ = zip(*filter(lambda (x,y): abs(y - m) < 1, vitems))
                for r in mrs:
                    arg[r] = "\\textbf{%s}" %arg[r]

            vitems = filter(lambda (m,y): "textit" not in argtime[m] and argtime[m] != '-', valtime.items())
            
            if (len(vitems)>0) and (sum(zip(*vitems)[1]) > 0):
                mr, m = min(vitems, key=lambda (x,y): y)
                mrs,_ = zip(*filter(lambda (x,y): abs(y - m) < 1, vitems))
                for r in mrs:
                    argtime[r] = "\\textbf{%s}" %argtime[r]


            print >> f, "&".join(["b" + str(bi)] + [ "%s & %s" %(arg[r],argtime[r])  for r in ["max", "-"] + relax ]) #"%s&%s&%s&%s\\\\"%("b" + str(bi), arg1, arg2, impr1)
            print >> f, "\\\\"


        #impr1 = improvement(arg2, arg1)
        print >> f, "\\hline" 
        print >> f, "\\end{longtable}" 
	if show:
		print >> f, "\\end{document}" 

    if show:
	    p = subprocess.Popen(["pdflatex", texname + ".tex"], stdout=subprocess.PIPE)
	    p.communicate()
	    p = subprocess.Popen(["evince", texname + ".pdf"], stdout=subprocess.PIPE)
	    p.communicate()


def tex_distances(d, field, agap, num, mindist, relax, metrics, texname='outfile', debug=False, show=True):
    '''
	d: the dictionary with the measurements
		e.g. d = pickle.load(open("divs.pickle"))
	field: 'avg', 'bravg', 'brdiff' output metric
	agap: 5, 10, 20 allowed gap from the optimal solution
	metric: the metrics of the measurement (from divcon - unison)
        texname: name of the output .tex file - default = 'outfile'
    ''' 
    agap = str(agap)

    ind = get_ind(field)

    title = "%s for measurements of (%s, %s%%)" %(ind.capitalize(), relax, str(agap))


    def get_fields(benchmark, arch, heuristic, metric, agap, branch, relax, mindist, field, num, avg, stdev):
	mnum = d[benchmark][arch][heuristic][metric][agap][branch][relax][mindist][field][num][avg]
	#mnum = mnum if dist else maxnum/1000.
	mstd = d[benchmark][arch][heuristic][metric][agap][branch][relax][mindist][field][num][stdev]
	#maxstd = maxstd if dist else maxstd/1000.
	mseeds = d[benchmark][arch][heuristic][metric][agap][branch][relax][mindist][field][num]["n"]
	return (mnum, mstd, mseeds)

    names = sorted(d.keys())
    with open(texname + '.tex', 'w') as f:
	if show:
		print >> f, "\\documentclass{standalone}"
		print >> f, "\\usepackage{multirow}"
		print >> f, "\\usepackage{longtable}"
		print >> f, "\\begin{document}"
        print >> f, "\\begin{longtable}{|l|%s}"%("c|"*2*(len(metrics))) 
	print >> f, '''\\caption{\\label{tab:distances}{The table shows 
		      the diversification time, $t$, and the number of generated
		      variants, $num$, within the given time limit (10 min), gap=10\%,
		      and \\ac{LNS} relax rate=70\%
		      for the three distances $\delta_c$, $\delta_{bh}$,
		      and $\delta_{lev}$.
		      The values in  \\textbf{bold} represent the minimum 
		      diversification time for each benchmark and the values in \\emph{italic} 
		      correspond to incomplete experiments.}}\\\\'''
        print >> f, "\\hline" 
        #print >> f, "&\\multicolumn{2}{c|}{\\multirow{2}{*}{\\textsc{MaxDiverse$k$Set}}}&\\multicolumn{2}{c|}{\\multirow{2}{*}{RS}}&\\multicolumn{%d}{c|}{LNS}\\\\" %2*len(relax) 
        #print >> f, "\\cline{6-%d}"%(5+len(relax)*2)
        print >> f, "&%s\\\\" %( "&".join(map(lambda x: "\\multicolumn{2}{c|}{%s}"%(dist_to_delta(x)), metrics)))
        print >> f, "\\cline{2-%d}"%(1 + len(metrics)*2)
        print >> f, "&%s\\\\" %( "&".join([r"$t$", "num"]*(len(metrics))))
    # MaxDiversekSet
       # print >> f, "&\\footnotesize dfs (%s\\textbackslash maxd (N))&\\footnotesize  lns (%s\\textbackslash maxd (N))&\\footnotesize  improv. \\%%  \\\\" %( ind, ind) 
        print >> f, "\\hline" 

        for bi,benchmark in enumerate(benchmarks, 1):
            def mipslns_0(metric):
		branch = "clrandom"
                return d[benchmark].has_key("mips") and d[benchmark]["mips"].has_key("lns") and d[benchmark]["mips"]["lns"].has_key(metric) and d[benchmark]["mips"]["lns"][metric].has_key(agap) and d[benchmark]["mips"]["lns"][metric][agap].has_key(branch) and d[benchmark]["mips"]["lns"][metric][agap][branch].has_key(relax) and d[benchmark]["mips"]["lns"][metric][agap][branch][relax].has_key(mindist) and d[benchmark]["mips"]["lns"][metric][agap][branch][relax][mindist].has_key(field)
            def mipslns(metric, num):
		branch = "clrandom"
                return mipslns_0(metric) and d[benchmark]["mips"]["lns"][metric][agap][branch][relax][mindist][field].has_key(num)

            arg = {m: "-" for m in metrics}
            argtime = {m: "-" for m in metrics}
            val = {m: 0 for m in metrics}
            valtime = {m: 0 for m in metrics} 

	    branch = "clrandom"
            for metric in metrics:
              if mipslns(metric, num):
                (lnsnum,lnsstd,lnsnseeds) = get_fields(benchmark, "mips", "lns", metric, agap, branch, relax, mindist, field, num, "num", "stdev") 
                (tlnsnum,tlnsstd,tlnsnseeds) = get_fields(benchmark, "mips", "lns", metric, agap, branch, relax, mindist, field, num, "stime", "stime_stdev") 
                if debug:
                        arg[metric] = "%.2f$\\pm$%.2f (%d)" %(lnsnum, lnsstd, lnsnseeds)
                        argtime[metric] = "%.2f$\\pm$%.2f (%d)" %(tlnsnum/1000., tlnsstd/1000., tlnsnseeds)
                else:
                        arg[metric] = "%d " %(num)
                        argtime[metric] = "%.2f$\\pm$%.2f" %(tlnsnum/1000., tlnsstd/1000.)

                val[metric] = lnsnum
                valtime[metric] = tlnsnum/1000.

              else:
                if mipslns_0(metric):
		    keys = d[benchmark]["mips"]["lns"][metric][agap][branch][relax][mindist][field].keys()
		    remlown = filter(lambda x: d[benchmark]["mips"]["lns"][metric][agap][branch][relax][mindist][field][x]['n'] >= 5, keys)
                    n = max(remlown)

                    (lnsnum,lnsstd,lnsnseeds) = get_fields(benchmark, "mips", "lns", metric, agap, branch, relax, mindist, field, n, "num", "stdev") 
                    (tlnsnum,tlnsstd,tlnsnseeds) = get_fields(benchmark, "mips", "lns", metric, agap, branch, relax, mindist, field, n, "stime", "stime_stdev") 
                    if debug:
                        arg[metric] = "\\textit{%.2f$\\pm$%.2f (%d)}" %(lnsnum, lnsstd, lnsnseeds)
                        argtime[metric] = "\\textit{%.2f$\\pm$%.2f (%d)}" %(tlnsnum/1000., tlnsstd/1000., tlnsnseeds)
                    else:
                        arg[metric] = "\\textit{%d }" %(n)
                        argtime[metric] = "\\textit{%.2f$\\pm$%.2f}" %(tlnsnum/1000., tlnsstd/1000.)
 
                    val[metric] = lnsnum
                    valtime[metric] = tlnsnum/1000.


            vitems = filter(lambda (m,y): "textit" not in argtime[m] and argtime[m] != '-', valtime.items())
            if len(vitems)>0 and sum(zip(*vitems)[1]) > 0:
                mr, m = min(vitems, key=lambda (x,y): y)
                mrs,_ = zip(*filter(lambda (x,y): abs(y - m) < 0.5, vitems))
                for m in mrs:
                    argtime[m] = "\\textbf{%s}" %argtime[m]


            print >> f, "&".join(["b" + str(bi)] + [ "%s & %s" %(argtime[m], arg[m])  for m in metrics ]) #"%s&%s&%s&%s\\\\"%("b" + str(bi), arg1, arg2, impr1)
            print >> f, "\\\\"


        #impr1 = improvement(arg2, arg1)
        print >> f, "\\hline" 
        print >> f, "\\end{longtable}" 
	if show:
		print >> f, "\\end{document}" 

    if show:
	    p = subprocess.Popen(["pdflatex", texname + ".tex"], stdout=subprocess.PIPE)
	    p.communicate()
	    p = subprocess.Popen(["evince", texname + ".pdf"], stdout=subprocess.PIPE)
	    p.communicate()



def plot_maxdiv_lns_new(d, b, metric, field, agap, relax, mindist, dist=True, path=".", legend_loc='lower right'):
    arch = 'mips'
    rel = str(relax)
    agap = str(agap)
    l = dict()
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    avg = 'num' if dist else 'stime'
    stdev = 'stdev' if dist else 'stime_stdev'

    # MaxDiversekSet
    algo = 'dfs'
    br   = 'cloriginal'
 
    if (d[b].has_key(arch) and d[b][arch].has_key(algo) and d[b][arch][algo].has_key(metric) and d[b][arch][algo][metric].has_key(agap) and d[b][arch][algo][metric][agap].has_key(br) and d[b][arch][algo][metric][agap][br][None].has_key(mindist) and d[b][arch][algo][metric][agap][br][None][mindist].has_key(field)):
        cdict = dict(**d[b][arch][algo][metric][agap][br][None][mindist][field])
        k = sorted(cdict.keys())
        xy = [ (i, cdict[i][avg], 2*cdict[i][stdev]/math.sqrt(cdict[i]['n'])) for i in  k]
        if len(xy) > 0:
            x,y,err = map(np.array,zip(*xy))
            plt.plot(x, y, linestyle='--', lw=2, color='r', label='MaxDiversekSet')
            plt.fill_between(x, y-err, y+err, linestyle='-.', color='r', alpha = 0.2)
            #plt.errorbar(x, y, yerr=err, linestyle=':', color='k', label='MaxDiversekSet')

    # Random search
    algo = 'dfs'
    br   = 'clrandom'
 
    if (d[b].has_key(arch) and d[b][arch].has_key(algo) and d[b][arch][algo].has_key(metric) and d[b][arch][algo][metric].has_key(agap) and d[b][arch][algo][metric][agap].has_key(br) and d[b][arch][algo][metric][agap][br].has_key(None) and d[b][arch][algo][metric][agap][br][None].has_key(mindist) and d[b][arch][algo][metric][agap][br][None][mindist].has_key(field)):
        cdict = dict(**d[b][arch][algo][metric][agap][br][None][mindist][field])
        k = sorted(cdict.keys())
        xy = [ (i, cdict[i][avg], 2*cdict[i][stdev]/math.sqrt(cdict[i]['n'])) for i in  k]
        if len(xy) > 0:
            x,y,err = map(np.array, zip(*xy))
            plt.plot(x, y, linestyle='--', lw=2, color='g', label='Random Search')
            plt.fill_between(x, y-err, y+err, linestyle='-.', color='g', alpha = 0.2)
            #plt.errorbar(x, y, yerr=err, linestyle='-.', color='k', label='Random Search')
 
    # LNS
    algo = 'lns'
    br   = 'clrandom'
 
    if (d[b].has_key(arch) and d[b][arch].has_key(algo) and d[b][arch][algo].has_key(metric) and d[b][arch][algo][metric].has_key(agap) and d[b][arch][algo][metric][agap].has_key(br) and d[b][arch][algo][metric][agap][br].has_key(rel) and d[b][arch][algo][metric][agap][br][None].has_key(mindist) and d[b][arch][algo][metric][agap][br][rel][mindist].has_key(field)):
        cdict = dict(**d[b][arch][algo][metric][agap][br][rel][mindist][field])
        k = sorted(cdict.keys())
        xy = [ (i, cdict[i][avg], 2*cdict[i][stdev]/math.sqrt(cdict[i]['n'])) for i in k ]
        if len(xy) > 0:
            x,y,err = map(np.array, zip(*xy))
            plt.plot(x, y, linestyle='--', lw=2, color='b', label='LNS')
            plt.fill_between(x, y-err, y+err, linestyle='-.', color='b', alpha = 0.2)

    if dist:
        ax.set_ylim(bottom=0)
        ax.set_ylabel(r'$d(\delta_c)$', fontsize=14)
        #ax.set_ylabel(et_ind(field), fontsize=14)
 
    else:      
        ax.set_yscale('log')
        ax.set_ylim(bottom=1)
        ax.set_ylabel(get_ind('stime'), fontsize=14)
 
    ax.set_xlabel("Number of Variants", fontsize=14)
    ax.legend(loc=legend_loc, fontsize=14)
    plt.title(dbench[b], fontsize=20)
    ax.tick_params(axis = 'both', which = 'major', labelsize = 14)
    ax.tick_params(axis = 'both', which = 'minor', labelsize = 14)
    fig.set_size_inches(18.5/3, 15/3.)
    plt.savefig(path + "/" + "%s_" %("dist" if dist else "time") + b + "_" + metric + ".pdf", dpi=400, format='pdf')
    #plt.legend(loc='center right')


    #plt.show()




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


def plot_rs_vs_lns( d_lns, metric, field, agap, colors, num, mindist, loc='upper right', dist=True, path="."):
    arch = 'mips'
    agap = str(agap)
    l = dict()
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    #lns = dict()

    if dist:
        mean = 'num'
        stdev = 'stdev'
    else:
        mean = 'stime'
        stdev = 'stime_stdev'
    # colors = ['darkorange', 'darkred', 'darkgreen', 'royalblue', 'darkorchid', 'crimson', 'olive', 'yellowgreen']
    c = 0
    for bi,b in enumerate(benchmarks,1):

        lns_random = []

        # Random search
        algo = 'dfs'
        br   = 'clrandom'
     
        if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(None) and d_lns[b][arch][algo][metric][agap][br][None].has_key(mindist) and d_lns[b][arch][algo][metric][agap][br][None][mindist].has_key(field) and d_lns[b][arch][algo][metric][agap][br][None][mindist][field].has_key(num)):
            cdict = dict(**d_lns[b][arch][algo][metric][agap][br][None][mindist][field])
            k = sorted(cdict.keys())
            

            #for i in k:
            if not cdict[num].has_key(mean):
                continue

            val = ufloat(cdict[num][mean],cdict[num][stdev])
# 
                 # LNS
            algo = 'lns'
            br   = 'clrandom'
         
            for rel in rrates[1:]:

                #if not lns.has_key(rel):
                 #       lns[rel] = dict()

                if (d_lns[b].has_key(arch) and d_lns[b][arch].has_key(algo) and d_lns[b][arch][algo].has_key(metric) and d_lns[b][arch][algo][metric].has_key(agap) and d_lns[b][arch][algo][metric][agap].has_key(br) and d_lns[b][arch][algo][metric][agap][br].has_key(rel) and d_lns[b][arch][algo][metric][agap][br][rel].has_key(mindist) and d_lns[b][arch][algo][metric][agap][br][rel][mindist].has_key(field) and d_lns[b][arch][algo][metric][agap][br][rel][mindist][field].has_key(num)):
                    lnsdict = dict(**d_lns[b][arch][algo][metric][agap][br][rel][mindist][field][num])
                    #k = sorted(cdict.keys())

                    val2 = ufloat(lnsdict[mean], lnsdict[stdev])
                    n = lnsdict['n']

                    if val2>=val:
                        lnsval = (1.0*val2)/val
                    else:
                        lnsval = -(1.0*val)/val2

                    lns_random.append((float(rel),lnsval,n))

            if len(lns_random) > 0:
                x,y,n = zip(*lns_random)
                ci = [ 2.*i.std_dev/math.sqrt(ni) for i,ni in zip(y,n)]
                ermin = [i.nominal_value - j for i,j in zip(y,ci)]
                erplus = [i.nominal_value + j for i,j in zip(y,ci)]
                plt.fill_between(x, ermin, erplus, linestyle='-.', color=colors[c], alpha = 0.1)
                plt.plot(x, map(lambda i: i.nominal_value, y), 'o--', linewidth=1.5,  color=colors[c], label='b' + str(bi))
                c+=1 



    #ax.set_ylim(bottom=0,top=1.1)
    x = [0.1, 0.2, 0.4, 0.6, 0.8]
    
    ax.set_xticks(x)
    if dist:
        ax.set_yticks([-2, -1, 0, 1, 2, 5, 10])
    else:
        ax.set_yticks([-10, -5, -1, 1, 5, 10, 50] )
        ax.set_ylim([-20,100])
        #ax.set_yscale('log')

    ax.set_xlim([0.05,0.9])

    xn = [ float(r) for r in rrates[1:]]
    plt.fill_between(xn, [-1. for _ in xn], [1. for _ in xn], linestyle='-.', color='gray', alpha=0.8, hatch='/')
    if dist:
	label = r'$P_{\delta}(\delta_c, S_{LNS}, S_{RS})$'
        ax.set_ylabel(label, fontsize=14, labelpad=5)
	ax.yaxis.set_label_coords(-0.02,0.95)
    else:
	label = r'$P_{t}(t_{LSN}, t_{RS})$'
        ax.set_ylabel(label, fontsize=14, labelpad=5)
        #ax.set_ylabel(label, rotation=0, fontsize=12, labelpad=5)
	ax.yaxis.set_label_coords(-0.02,0.95)

    ax.set_xlabel("relax rate", fontsize=20)

    #ax.legend(loc=loc, fontsize=12)

    ax.tick_params(axis = 'both', which = 'major', labelsize = 20)
    ax.tick_params(axis = 'both', which = 'minor', labelsize = 14)


    plt.title('LNS over RS', fontsize=24)
    #fig.set_size_inches(18.5/3, 12.5/3)
    fig.set_size_inches(8.5, 6.0)
    plt.savefig( path + "/" + "lns_vs_rs_" + ("dist" if dist else "time") + "_" + metric + ".pdf", dpi=400, format='pdf')
    #plt.legend(loc='center right')
    #plt.show()

agaps = ['5', '10', '20']
metrics = ["hamming", "reg_hamming", "levenshtein", "br_hamming", "diff_br_hamming", "hamm_reg_gadget"]

def plot_gadgets_vs_distance(d_gadgets, d_random_lns, num, field):
    res = []
    for bench in benchmarks:
        for r in rrates:
            for ag in agaps:
                for metric in metrics:
                    if not d_gadgets.has_key(ag): continue
                    if not d_gadgets[ag].has_key(bench): continue
                    if not d_gadgets[ag][bench].has_key(r): continue
                    if not d_gadgets[ag][bench][r].has_key(metric): continue

                    if not d_random_lns.has_key(bench): continue
                    if not d_random_lns[bench].has_key('mips'): continue
                    lns = 'lns' if r!='-' else 'dfs'
                    if not d_random_lns[bench]['mips'].has_key(lns): continue
                    if not d_random_lns[bench]['mips'][lns].has_key(metric): continue
                    if not d_random_lns[bench]['mips'][lns][metric].has_key(ag): continue
                    if not d_random_lns[bench]['mips'][lns][metric][ag].has_key('clrandom'): continue
                    if not d_random_lns[bench]['mips'][lns][metric][ag]['clrandom'].has_key(r): continue
                    r = r if r!="-" else None
                    if not d_random_lns[bench]['mips'][lns][metric][ag]['clrandom'][r].has_key(field): continue
                    if not d_random_lns[bench]['mips'][lns][metric][ag]['clrandom'][r][field].has_key(num): continue
                    x = d_gadgets[ag][bench][r][metric]['res'][0]
                    y = d_random_lns[bench]['mips'][lns][metric][ag]['clrandom'][r][field][num]['num']
                    res.append((x,y))

    if len(res)>0:
        x,y = zip(*res)
        plt.plot(x,y,'o')
        plt.show()


def plot_one_dvg(dist_vs_gadgets, field, remove_zero=False): 
    '''
    the first is the dict that extract_results.py generates
    the  field is the relevant field
    '''

    res = dist_vs_gadgets[field].items() #[(dg['gadgets'],dg[field]) for dg in dist_vs_gadgets]
    if remove_zero:
        res = filter(lambda ((i,j),f): j>0, res)
    if len(res)==0:
        print "No samples."
        return
    xy,fr = zip(*res)
    x,y = zip(*xy)
    plt.scatter(x, y, s=fr, alpha=0.5)
    #plt.plot(x,y,'o', alpha=0.5, label=field)

def plot_many_dist_vs_gadgets(dist_vs_gadgets, fields, remove_zero=False): 
    '''
    the first is the dict that extract_results.py generates
    the  fields are the relevant field (hamm, reghamm, brhamm, brdiff, lev)
    '''
    for field in fields:
        fig = plt.figure()
        plt.title(field)
        plt.ylim([-5,50])
        plot_one_dvg(dist_vs_gadgets, field, remove_zero)
    plt.legend()
    plt.show()

def fields_to_num(field):
    if field == "hamm":
        return 1
    elif field == "brhamm":
        return 2
    elif field == "brdiff":
        return 3
    elif field == "lev":
        return 4
    elif field == "reghamm":
        return 5

def num_to_field(num):
    if num == 1:
        return "hamm"
    elif num == 2:
        return  "brhamm"
    elif num == 3:
        return "brdiff"
    elif num == 4:
        return "lev"
    elif num == 5:
        return "reghamm"



def plot_3d_dvg(dist_vs_gadgets_points, fields, remove_zero=False):
    ''' 3D plot
    '''
    fig = plt.figure() 
    ax = fig.add_subplot(111, projection='3d')
    nums = map(fields_to_num, fields)
    
    keys, freq = zip(*dist_vs_gadgets_points.items())
    unzkeys = zip(*keys)
    x = unzkeys[0]
    y = unzkeys[nums[0]]
    z = unzkeys[nums[1]]
    ax.scatter(x,y,z,s=freq, marker='o')
    ax.set_xlabel("gadget survival")
    ax.set_ylabel(fields[0])
    ax.set_zlabel(fields[1])
    plt.show()
    
def plot_surv_dvg(dist_vs_gadgets_points, fields, surv, remove_zero=False):
    ''' 3D plot
    '''
    fig = plt.figure() 
    ax = plt.subplot(1, 1, 1)
    nums = map(fields_to_num, fields)
    vals = filter(lambda (v,f): v[0] == surv, dist_vs_gadgets_points.items())
    if remove_zero:
        vals = filter(lambda (v,f): v[nums[0]]!=0 or v[nums[1]]!=0, vals)
    print max(vals, key = lambda (v,f): f)
    keys, freq = zip(*vals)

    unzkeys = zip(*keys)
    x = unzkeys[nums[0]]
    y = unzkeys[nums[1]]

    ax.scatter(x,y,s=freq, marker='o', alpha=0.5)
    ax.set_xlabel(fields[0])
    ax.set_ylabel(fields[1])
    plt.show()
 

def plot_distance_histograms(dist_vs_gadgets_points, dists):
    def split_dict(d, n):
            for m,f in dist_vs_gadgets_points.items():
              if m[0] == 0:
                  d[0].append((m[n],f))
              elif m[0] <= 0.1:
                  d[1].append((m[n],f))
              elif m[0] <= 0.4:
                 d[4].append((m[n],f))
              else:
                 d[10].append((m[n],f))

    def plot_all(d):                   
      plt.hist(zip(*d[0])[0], 40, weights=zip(*d[0])[1], label='0', alpha=0.5)
      plt.hist(zip(*d[1])[0], 40, weights=zip(*d[1])[1], label='1', alpha=0.5)
      plt.hist(zip(*d[4])[0], 40, weights=zip(*d[4])[1], label='4', alpha=0.5)
      plt.hist(zip(*d[10])[0], 40, weights=zip(*d[10])[1], label='10', alpha=0.5)

    nums = map(fields_to_num, dists)
    ds = { n:{0:[], 1:[], 4:[], 10:[]} for n in nums }
    for n in ds:
        split_dict(ds[n], n)
        fig = plt.figure()
        plot_all(ds[n])
        plt.legend()
        plt.title(num_to_field(n))
    plt.show()


def plot_3d_histogram(dist_vs_gadgets_points, dists):
    def split_dict(d, n1, n2):
            for m,f in dist_vs_gadgets_points.items():
              if m[0] == 0:
                  d[0].append(((m[n1],m[n2]), f))
              elif m[0] <= 0.1:
                  d[1].append(((m[n1],m[n2]), f))
              elif m[0] <= 0.4:
                 d[4].append(((m[n1],m[n2]),f))
              else:
                 d[10].append(((m[n1],m[n2]),f))

    num1, num2 = fields_to_num(dists[0]), fields_to_num(dists[1])

    d = {0:[], 1:[], 4:[], 10:[]}

    split_dict(d, num1, num2)

    colors = ['r', 'g', 'b', 'orange']
    for i,di in enumerate(sorted(d)):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')


        xy, f = zip(*d[di])
        x,y = zip(*xy)
        hist, xedges, yedges = np.histogram2d(x, y, weights=f, bins=40)

        # Construct arrays for the anchor positions of the 16 bars.
        xpos, ypos = np.meshgrid(yedges[:-1], xedges[:-1]) #xedges[:-1] + 0.25, yedges[:-1] + 0.25, indexing="ij")
        xpos = xpos.ravel()
        ypos = ypos.ravel()
        zpos = hist.flatten()

        # Construct arrays with the dimensions for the 16 bars.
        #dx = dy = 0.5 * np.ones_like(zpos)
        #dz = hist.ravel()
        #print xpos.shape()
        #print ypos.shape()
        #print zpos.shape()
        #print dx.shape()
        #print dy.shape()
        #print dz.shape()

        #ax.bar3d(xpos, ypos, zpos, dx, dy, dz, zsort='average')
        print len(xpos), len(ypos), len(zpos)
        ax.bar3d(xpos, ypos, np.zeros(len(zpos)), 1, 1, zpos, zsort='average', color=colors[i], label=di)
        ax.set_xlabel(num_to_field(num2))
        ax.set_ylabel(num_to_field(num1))
        plt.title(di)
    plt.show()

