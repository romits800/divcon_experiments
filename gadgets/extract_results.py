#! env python

# grep -E "(python create|^Average|^Number divs)" out2 &> out
import re
import sys
from uncertainties import ufloat
from uncertainties import unumpy  # Array manipulation
#import uncertainties
import math
import cPickle as pickle
import os

pat = re.compile("div_monolithic_([^_]*)_([^_]*)_([a-zA-Z_0-9]*\.[a-zA-Z_0-9]*\.[a-zA-Z_0-9]*)_([0-9]+)_([0-9]+)_([^0-9]+)_(random|clrandom|original|cloriginal)_([0-9]+)(_.*|)_result.pickle")
# div_monolithic_lns_mips_gcc.alias.get_frame_alias_set_10_1000_br_hamming_clrandom_105_0.4_10000_constant.pickle
pat2 = re.compile("_([01]\.[0-9]+)_([0-9]+)_([a-z]+)")

filepat = re.compile("divs_[0-9]+_[0-9]$")


metrics = ["br_hamming", "levenshtein", "hamming", "diff_br_hamming", "reg_hamming", "hamm_reg_gadget"]
rrates = rrates =  ["-", "0.1", "0.2", "0.4", "0.6", "0.8", "0.9"]

def print_metric(metric):
    if metric == "diff_br_hamming": return "diff"
    elif metric == "br_hamming": return "br"
    elif metric == "hamming": return "hamm"
    elif metric == "levenshtein": return "lev"
    elif metric == "reg_hamming": return "reg"
    elif metric == "hamm_reg_gadget": return "hrg"
    else: return "None"
    
 
if (len(sys.argv) < 3):
    print "Give as argument folder to the bench folders and the metric"
    print "python extract_results.py <divs_? folder> <max|both>"
    exit (0)

path = sys.argv[1]
gmetric = sys.argv[2]
#agap = sys.argv[3]


def print_dat(d):
        return "|".join(['%d%%:%d%%'%(int(k*100), int(d[k]*100)) for k in sorted(d.keys())])

# Open a file
l = dict()
d = dict()
for meas in os.listdir(path):

   fil = re.match(filepat,meas)
   if fil!= None:
   # if meas.startswith("divs"):
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
                data = inp[gmetric]['data']
                name = fil.split("/")[-1]
                m.append((data, name, numdivs, avg, std))
            else:
                print "Error", inp[gmetric]

        for dat,i,j,k1,k2 in m:
            a = re.match(pat,i)
            islns = True
            try:
                method, arch, bench, gap, nodivs, metric, branching, seed, rest = a.groups()
                # if gap!=agap: continue

                if not d.has_key(gap):
                    d[gap] = dict()
                if not d[gap].has_key(bench):
                    d[gap][bench] = dict()
                   
                if method == "lns":
                    b = re.match(pat2, rest)
                    try:
                        relax, base, lnsmeth = b.groups()
                    except:
                        print "Exception 1", rest, b
                else:
                    relax = '-'

                if not d[gap][bench].has_key(relax):
                    d[gap][bench][relax] = dict()
                if not d[gap][bench][relax].has_key(metric):
                    d[gap][bench][relax][metric] = dict()
                d[gap][bench][relax][metric][meas] = {'num': j, 'mean': k1, 'std': k2, 'data': dat}
            except:
                print "Exception 2", i

        print "".join(map(lambda x: x.ljust(17), ["Benchmark".ljust(50), "Relax"] + metrics) )
        for ag in d:
          for bench in d[ag]:
            for r in rrates:
                if r not in d[ag][bench]:
                    continue
                print "".join([bench.ljust(50)] + map(lambda x: x.ljust(17), [r ] +[  "-" if m not in d[ag][bench][r] or not d[ag][bench][r][m].has_key(meas) or d[ag][bench][r][m][meas]["mean"]== "Average" else (str(ufloat(d[ag][bench][r][m][meas]["mean"], d[ag][bench][r][m][meas]['std'])*100) + "%"  + " (" + str(d[ag][bench][r][m][meas]["num"]) + ")" ) for m in metrics ]))
                dat = dict()
                tdat = dict()
                vals = [0.0, 0.05, 0.1, 0.2, 0.4, 0.5, 0.7, 1.0]
                for m in metrics:
                    temp = dict() if m not in d[ag][bench][r] or not d[ag][bench][r][m].has_key(meas) or d[ag][bench][r][m][meas]["mean"]== "Average"  else d[ag][bench][r][m][meas]["data"]

                    allsum = float(sum(temp.values()))
                    if len(temp) > 0: 
                        dat[m] = dict()
                        tdat[m] = dict()
                    for i in temp:
                        for v in vals:
                            if i <= v:
                                if tdat[m].has_key(v):
                                    tdat[m][v] += temp[i]
                                else: 
                                    tdat[m][v] = temp[i]
                                break
                    if tdat.has_key(m):
                        for v in tdat[m]:
                            val = round(tdat[m][v]/allsum,2)
                            if val > 0.0 :
                                dat[m][v] = val

                #print "".join([bench.ljust(50)] + map(lambda x: x.ljust(17), [r ] +[ "-" if not dat.has_key(m) else print_dat(dat[m]) for m in metrics ]))
                
                
        print "-----------------------------------------------"
        for ag in d:
          for r in rrates:
            if not l.has_key(r): l[r] = dict()
            for metric in metrics:
                k = [ (d[ag][b][r][metric][meas]["mean"],d[ag][b][r][metric][meas]["std"],d[ag][b][r][metric][meas]['num'])  for b in d[ag] if d[ag][b].has_key(r) and d[ag][b][r].has_key(metric) and d[ag][b][r][metric].has_key(meas) and d[ag][b][r][metric][meas]["mean"] != "Average"]
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

          print "".join(map(lambda x: x.ljust(20), ["Relax/%s"%ag] + metrics) )
          for r in rrates:
            if r not in l:
                 continue
            results = [ ('-' if m not in l[r]  or meas not in l[r][m] or l[r][m]== "Average" else (l[r][m][meas]['res']*100).format("3.5")) + "%"  for m in metrics ]
            print "".join( map(lambda x: x.ljust(20), [r ] + results))

# print
# print "###############################################"
# print "#########      TOTAL (all seeds)      #########"
# print "###############################################"

# For all seeds
# for r in l:
#     for metric in l[r]:
#         k = [(l[r][metric][meas]['mean'],l[r][metric][meas]['std'],l[r][metric][meas]['num']) for meas in l[r][metric] if l.has_key(r) and l[r].has_key(metric)]
#         num = sum([n for m,s,n in k])
#         mean = sum([m*n for m,s,n in k])/num #sum([n for m,s,n in k])
#         qs = [ m**2+s**2*(n-1)/n for m,s,n in k]
#         q = sum([ q*n for (m,s,n), q in zip(k,qs)])/num # sum([n for m,s,n in k])
#         std = math.sqrt(q-mean**2)
#         l[r][metric]['res'] = ufloat(mean,std)
# 
# print "".join(map(lambda x: x.ljust(20), ["Relax"] + metrics) )
# for r in rrates:
#     if r not in l:
#          continue
#     results = [ ('-' if m not in l[r]  or 'res' not in l[r][m] or l[r][m]== "Average" else (l[r][m]['res']*100).format("3.5")) + "%"  for m in metrics ]
#     print "".join( map(lambda x: x.ljust(20), [r ] + results))
# 

print
print "###############################################"
print "#########      TOTAL (benchmarks)     #########"
print "###############################################"

for ag in d:
  for r in rrates:
    print "-------------------------------------------------------------------------------"
    print "-------------------------------------------------------------------------------"
    print "".join(map(lambda x: x.ljust(17), ["Benchmark".ljust(50), "Relax"] + metrics) )
    print "-------------------------------------------------------------------------------"
    for bench in d[ag]:
        if r not in d[ag][bench]:
            continue
        for metric in metrics:
            if metric not in d[ag][bench][r]:
                continue
            k = [(d[ag][bench][r][metric][meas]['mean'],d[ag][bench][r][metric][meas]['std'],d[ag][bench][r][metric][meas]['num']) for meas in d[ag][bench][r][metric] if d.has_key(ag) and d[ag].has_key(bench) and d[ag][bench].has_key(r) and d[ag][bench][r].has_key(metric)]
            num = sum([n for m,s,n in k])
            mean = sum([m*n for m,s,n in k])/num #sum([n for m,s,n in k])
            qs = [ m**2+s**2*(n-1)/n for m,s,n in k]
            q = sum([ q*n for (m,s,n), q in zip(k,qs)])/num # sum([n for m,s,n in k])
            std = math.sqrt(q-mean**2)
            d[ag][bench][r][metric]['res'] = (mean,std) #ufloat(mean,std)
            d[ag][bench][r][metric]['avgnum'] = num/len(k)
            #print metric, bench, ufloat(mean,std)


        print "".join([bench.ljust(50)] + map(lambda x: x.ljust(17), [r] +[ "-" if m not in d[ag][bench][r] else (str((ufloat(*d[ag][bench][r][m]['res'])*100).format("2.2")) + "% " + "(" + str(d[ag][bench][r][m]['avgnum']) +  ")") for m in metrics ]))
        
# Write outputs.
    
def formatout(v, bold=False):
    vf = '{:.2f}'.format(v*100) + "%"
    #vf = str(vf) + "%"
    if bold:
        return "\\textbf{" + vf + "}"
    else: 
        return vf
 
cmetrics = map(lambda x: x.replace("_", ""), metrics)
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


for ag in d:
  for r in rrates:
    with open("output" + r + ag + ".csv", "w") as f:
        f.write(",".join(["Benchmark"] + cmetrics))
        f.write("\n")
        for bi,bench in enumerate(benchmarks, 1):
            if ag not in d: continue
            if bench not in d[ag]: continue
            if r not in d[ag][bench]: continue
            # find minimum values to mark
            data = [ (ufloat(*d[ag][bench][r][m]['res']),m) for m in metrics if m in d[ag][bench][r] ]
            mind = min(data, key=lambda (res,m): res)
            minds = filter(lambda (x,m): abs(x- mind[0]) < 0.005, data)
            _, minms = zip(*minds)
            data = ["b" + str(bi)] + [ "-" if m not in d[ag][bench][r] else formatout(ufloat(*d[ag][bench][r][m]['res']), m in minms) for m in metrics ]
            cdata = map (lambda x: x.replace("_", "\\_"), data)
            cdata = map (lambda x: x.replace("%", "\\%"), cdata)
            cdata = map (lambda x: x.replace("+/-", "$\\pm$"), cdata)
            f.write(",".join(cdata))
            f.write("\n")
    
for ag in d:
  for m in metrics:
    with open("output" + m + ag + ".csv", "w") as f:
        f.write(",".join(["Benchmark"] + rrates))
        f.write("\n")
        for bi,bench in enumerate(benchmarks, 1):
            if not d.has_key(ag): continue
            if not d[ag].has_key(bench): continue
            if not d[ag][bench].has_key(r): continue
            if not d[ag][bench][r].has_key(m): continue
            # find minimum values to mark
            data = [ (ufloat(*d[ag][bench][r][m]['res']),r) for r in rrates if r in d[ag][bench] and m in d[ag][bench][r] ]
            mind = min(data, key=lambda (res,r): res)
            minds = filter(lambda (x,r): abs(x- mind[0]) < 0.005, data)
            _, minms = zip(*minds)
            data = ["b" + str(bi)] + [ "-" if r not in d[ag][bench] or m not in d[ag][bench][r] else formatout(ufloat(*d[ag][bench][r][m]['res']), r in minms) for r in rrates ]
            cdata = map (lambda x: x.replace("_", "\\_"), data)
            cdata = map (lambda x: x.replace("%", "\\%"), cdata)
            cdata = map (lambda x: x.replace("+/-", "$\\pm$"), cdata)
            f.write(",".join(cdata))
            f.write("\n")

agaps = sorted(d.keys(), key=lambda x: int(x))
for m in metrics:
  for r in rrates:
    with open("gaps_output" + m + r + ".csv", "w") as f:
        f.write(",".join(["Benchmark"] + agaps ))
        f.write("\n")
        for bi,bench in enumerate(benchmarks, 1):
            # find minimum values to mark
            data = [ (ufloat(*d[ag][bench][r][m]['res']),ag) for ag in agaps if d[ag].has_key(bench) and d[ag][bench].has_key(r) and d[ag][bench][r].has_key(m) ]
            if data == []: continue
            mind = min(data, key=lambda (res,ag): res)
            minds = filter(lambda (x,ag): abs(x- mind[0]) < 0.005, data)
            _, minms = zip(*minds)
            data = ["b" + str(bi)] + [ "-" if not d[ag].has_key(bench) or not d[ag][bench].has_key(r) or not  d[ag][bench][r].has_key(m)  else formatout(ufloat(*d[ag][bench][r][m]['res']), ag in minms) for ag in agaps ]
            cdata = map (lambda x: x.replace("_", "\\_"), data)
            cdata = map (lambda x: x.replace("%", "\\%"), cdata)
            cdata = map (lambda x: x.replace("+/-", "$\\pm$"), cdata)
            f.write(",".join(cdata))
            f.write("\n")
 
 
with open("benchmarks.csv", "w") as f:
    f.write(",".join(["Bid", "Benchmark"]))
    f.write("\n")
    for bi,b in enumerate(benchmarks,1):
        b = b.replace("_", "\\_")
        b = b.replace("%", "\\%")
        b = b.replace("+/-", "$\\pm$")
 
        f.write(",".join(["b" + str(bi), b])) 
        f.write("\n")
    
    
pickle.dump(d, open("divs_gadgets.pickle", "w"))
