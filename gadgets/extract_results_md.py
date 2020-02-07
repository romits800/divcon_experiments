#! env python

# grep -E "(python create|^Average|^Number divs)" out2 &> out
import re
import sys
from uncertainties import ufloat
import cPickle as pickle
import os

pat = re.compile("div_monolithic_([^_]*)_([^_]*)_([a-zA-Z_0-9]*\.[a-zA-Z_0-9]*\.[a-zA-Z_0-9]*)_([0-9]+)_([0-9]+)_([^0-9]+)_(random|clrandom|original|cloriginal)_([0-9]+)(_.*|)_result.pickle")
# div_monolithic_lns_mips_gcc.alias.get_frame_alias_set_10_1000_br_hamming_clrandom_105_0.4_10000_constant.pickle
pat2 = re.compile("_([01]\.[0-9]+)_([0-9]+)_([a-z]+)")

def print_metric(metric):
    if metric == "diff_br_hamming": return "diff"
    elif metric == "br_hamming": return "br"
    elif metric == "hamming": return "hamm"
    elif metric == "levenshtein": return "lev"
    else: return "None"
    
 
if (len(sys.argv) < 3):
    print "Give as argument folder to the bench folders and the metric"
    print "python extract_results.py <divs_? folder> <max|both>"
    exit (0)

path = sys.argv[1]
metric = sys.argv[2]

# Open a file
for meas in os.listdir(path):
    if meas.startswith("divs"):
        measfolder = os.path.join(path, meas)
        final_num = meas.split("_")[-1]
        
        finalfolder = os.path.join(measfolder, "divs_" + final_num)
        files = []
        for di in os.listdir(finalfolder):
            benchfolder = os.path.join(finalfolder, di)
            for fil in os.listdir(benchfolder):
                if fil.endswith("_result.pickle"):
                    newfile = os.path.join(benchfolder, fil)
                    files.append(newfile) 

        m = []
        for fil in files:
            inp = pickle.load(open(fil))

            try:
                maxavg = "Average" if inp[metric]['avg'] == "Average" else ufloat(inp[metric]['avg'], inp[metric]['conf'])
            except:
                print "Exception ", fil
                continue
            numdivs = inp['numdivs']
            name = fil.split("/")[-1]
            m.append((name, numdivs, maxavg))

        d = dict()
        for i,j,k in m:
            a = re.match(pat,i)
            islns = True
            try:
                method, arch, bench, gap, nodivs, metric, branching, seed, rest = a.groups()

                if not d.has_key(bench):
                    d[bench] = dict()
                   
                if method == "lns":
                    b = re.match(pat2, rest)
                    try:
                        relax, base, lnsmeth = b.groups()
                    except:
                        print "Exception 1", rest, b
                else:
                    relax = '-'

                if not d[bench].has_key(relax):
                    d[bench][relax] = dict()
                d[bench][relax][metric] = dict()
                d[bench][relax][metric]["divs"] = j
                d[bench][relax][metric]["gadgets"] = k
            except:
                print "Exception 2", i

        metrics = ["br_hamming", "levenshtein", "hamming", "diff_br_hamming"]
        rrates = ["-"]
        print "\t\t".join(["Benchmark", "Relax"] + metrics )
        for bench in d:
            for r in rrates:
                if r not in d[bench]:
                    continue
                print "\t".join([bench, r ,"\t".join([  "-" if m not in d[bench][r] or d[bench][r][m]["gadgets"]== "Average" else (str(d[bench][r][m]["gadgets"]*100) + "%"  + " (" + str(d[bench][r][m]["divs"]) + ")" ) for m in metrics ])])
                
                
        print "###############################################"
        l = dict()
        for r in rrates:
            if not l.has_key(r): l[r] = dict()
            for m in metrics:
                #if not l[r].has_key(m): l[r][m] = dict()
                k = [ d[b][r][m]["gadgets"]  for b in d if d[b].has_key(r) and d[b][r].has_key(m) and d[b][r][m]["gadgets"] != "Average"]
                if (len(k) >0):
                    l[r][m] = sum(k)/len(k)

        print "\t\t".join(["Relax"] + metrics )
        for r in rrates:
            if r not in l:
                 continue
            print "\t".join([r ,"\t".join([ (str(l[r][m]*100) if l[r][m]!= "Average" else "-") + "%"  for m in metrics if m in l[r]])])
