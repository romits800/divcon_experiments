#! env python

# grep -E "(python create|^Average|^Number divs)" out2 &> out
import re
import sys
from uncertainties import ufloat
from uncertainties import unumpy  # Array manipulation
import uncertainties
import math
import cPickle as pickle
import os

pat = re.compile("div_monolithic_([^_]*)_([^_]*)_([a-zA-Z_0-9]*\.[a-zA-Z_0-9]*\.[a-zA-Z_0-9]*)_([0-9]+)_([0-9]+)_([^0-9]+)_(random|clrandom|original|cloriginal)_([0-9]+)(_.*|)_result.pickle")
# div_monolithic_lns_mips_gcc.alias.get_frame_alias_set_10_1000_br_hamming_clrandom_105_0.4_10000_constant.pickle
pat2 = re.compile("_([01]\.[0-9]+)_([0-9]+)_([a-z]+)")


metrics = ["br_hamming", "levenshtein", "hamming", "diff_br_hamming", "reg_hamming", "hamm_reg_gadget"]
rrates = rrates =  ["-"]

def print_metric(metric):
    if metric == "diff_br_hamming": return "diff"
    elif metric == "br_hamming": return "br"
    elif metric == "hamming": return "hamm"
    elif metric == "levenshtein": return "lev"
    elif metric == "reg_hamming": return "reg"
    elif metric == "hamm_reg_gadget": return "hrg"
    else: return "None"
    
 
if (len(sys.argv) < 4):
    print "Give as argument folder to the bench folders and the metric"
    print "python extract_results.py <divs_? folder> <max|both> <agap=10|20>"
    exit (0)

path = sys.argv[1]
gmetric = sys.argv[2]
agap = sys.argv[3]

# Open a file
l = dict()
d = dict()
for meas in os.listdir(path):
   if meas.startswith("divs"):
        print "###############################################"
        print "###########      %s      ###########"%meas
        print "###############################################"
 
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

            if inp[gmetric].has_key('conf'):
                maxavg = "Average" if inp[gmetric]['avg'] == "Average" else ufloat(inp[gmetric]['avg'], inp[gmetric]['conf'])
                avg =  "Average" if inp[gmetric]['avg'] == "Average" else inp[gmetric]['avg']
                std = inp[gmetric]['std']
                numdivs = inp['numdivs']
                name = fil.split("/")[-1]
                m.append((name, numdivs, avg, std))
            else:
                print "Error", inp[gmetric]

        for i,j,k1,k2 in m:
            a = re.match(pat,i)
            islns = True
            try:
                method, arch, bench, gap, nodivs, metric, branching, seed, rest = a.groups()
                if gap!=agap: continue

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
                if not d[bench][relax].has_key(metric):
                    d[bench][relax][metric] = dict()
                d[bench][relax][metric][meas] = {'num': j, 'mean': k1, 'std': k2 }
            except:
                print "Exception 2", i

        print "".join(map(lambda x: x.ljust(17), ["Benchmark".ljust(50), "Relax"] + metrics) )
        for bench in d:
            for r in rrates:
                if r not in d[bench]:
                    continue
                print "".join([bench.ljust(50)] + map(lambda x: x.ljust(17), [r ] +[  "-" if m not in d[bench][r] or not d[bench][r][m].has_key(meas) or d[bench][r][m][meas]["mean"]== "Average" else (str(ufloat(d[bench][r][m][meas]["mean"], d[bench][r][m][meas]['std'])*100) + "%"  + " (" + str(d[bench][r][m][meas]["num"]) + ")" ) for m in metrics ]))
                
                
        print "-----------------------------------------------"
        for r in rrates:
            if not l.has_key(r): l[r] = dict()
            for metric in metrics:
                k = [ (d[b][r][metric][meas]["mean"],d[b][r][metric][meas]["std"],d[b][r][metric][meas]['num'])  for b in d if d[b].has_key(r) and d[b][r].has_key(metric) and d[b][r][metric].has_key(meas) and d[b][r][metric][meas]["mean"] != "Average"]
                if (len(k) >0):
                    # For each replicate j you must have number of samples Nj, mean Mj, and variance Vj=SDj^2. 
                    # The mean across the three replicates is M=(N1*M1+N2*M2*N3*M3)/(N1+N2+N3).
                    # For each replicate, calculate the mean square Qj=Mj^2+Vj*(Nj-1)/Nj. 
                    # Note that the adjustment coefficient (Nj-1)/Nj is needed only if you computed Vj using (Nj-1) as the number of statistical freedom degrees (to obtain unbiased estimate). 
                    # The mean square across the three replicates is Q=(N1*Q1+N2*Q2*N3*Q3)/(N1+N2+N3). 
                    # Finally, the variance across those replicates is V=Q-M^2, and SD=sqrt(V). If the numbers of samples is small, you may want to adjust the above formula for V to one less statistical freedom degree by multiplying it by (N1+N2+N3)/(N1+N2+N3-1).
                    if not l[r].has_key(metric): l[r][metric] = dict()
                    num = sum([n for m,s,n in k])
                    mean = sum([m*n for m,s,n in k])/num #sum([n for m,s,n in k])
                    qs = [ m**2+s**2*(n-1)/n for m,s,n in k]
                    q = sum([ q*n for (m,s,n), q in zip(k,qs)])/num # sum([n for m,s,n in k])
                    std = math.sqrt(q-mean**2)

                    # avg = sum([m for m,s,n in k])/len(k)
                    # avg = sum(k)/len(k)
                    # std2 = math.sqrt(sum([ (avg-m)**2 for m,s,n in k])/(len(k) -1 ))
                    # std = unumpy.sqrt(std)
                    l[r][metric][meas] = {'res': ufloat(mean,std), 'mean': mean, 'std': std, 'num': num }
                    # print metric, r, mean, l[r][metric], ufloat(avg, std2)

        print "".join(map(lambda x: x.ljust(20), ["Relax"] + metrics) )
        for r in rrates:
            if r not in l:
                 continue
            results = [ ('-' if m not in l[r]  or meas not in l[r][m] or l[r][m]== "Average" else (l[r][m][meas]['res']*100).format("3.5")) + "%"  for m in metrics ]
            print "".join( map(lambda x: x.ljust(20), [r ] + results))

print
print "###############################################"
print "#########      TOTAL (all seeds)      #########"
print "###############################################"

# For all seeds
for r in l:
    for metric in l[r]:
        k = [(l[r][metric][meas]['mean'],l[r][metric][meas]['std'],l[r][metric][meas]['num']) for meas in l[r][metric] if l.has_key(r) and l[r].has_key(metric)]
        num = sum([n for m,s,n in k])
        mean = sum([m*n for m,s,n in k])/num #sum([n for m,s,n in k])
        qs = [ m**2+s**2*(n-1)/n for m,s,n in k]
        q = sum([ q*n for (m,s,n), q in zip(k,qs)])/num # sum([n for m,s,n in k])
        std = math.sqrt(q-mean**2)
        l[r][metric]['res'] = ufloat(mean,std)

print "".join(map(lambda x: x.ljust(20), ["Relax"] + metrics) )
for r in rrates:
    if r not in l:
         continue
    results = [ ('-' if m not in l[r]  or 'res' not in l[r][m] or l[r][m]== "Average" else (l[r][m]['res']*100).format("3.5")) + "%"  for m in metrics ]
    print "".join( map(lambda x: x.ljust(20), [r ] + results))


print
print "###############################################"
print "#########      TOTAL (benchmarks)     #########"
print "###############################################"

for r in rrates:
    print "-------------------------------------------------------------------------------"
    print "-------------------------------------------------------------------------------"
    print "".join(map(lambda x: x.ljust(17), ["Benchmark".ljust(50), "Relax"] + metrics) )
    print "-------------------------------------------------------------------------------"
    for bench in d:
        if r not in d[bench]:
            continue
        for metric in metrics:
            if metric not in d[bench][r]:
                continue
            k = [(d[bench][r][metric][meas]['mean'],d[bench][r][metric][meas]['std'],d[bench][r][metric][meas]['num']) for meas in d[bench][r][metric] if d.has_key(bench) and d[bench].has_key(r) and d[bench][r].has_key(metric)]
            num = sum([n for m,s,n in k])
            mean = sum([m*n for m,s,n in k])/num #sum([n for m,s,n in k])
            qs = [ m**2+s**2*(n-1)/n for m,s,n in k]
            q = sum([ q*n for (m,s,n), q in zip(k,qs)])/num # sum([n for m,s,n in k])
            std = math.sqrt(q-mean**2)
            d[bench][r][metric]['res'] = ufloat(mean,std)
            #print metric, bench, ufloat(mean,std)


        print "".join([bench.ljust(50)] + map(lambda x: x.ljust(17), [r] +[ "-" if m not in d[bench][r] else (str((d[bench][r][m]['res']*100).format("2.2")) + "%" ) for m in metrics ]))
        

