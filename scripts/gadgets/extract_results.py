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

pat = re.compile("(lns|agap|metr|k)div_monolithic_([^_]*)_([^_]*)_([a-zA-Z_0-9]*\.[a-zA-Z_0-9]*\.[a-zA-Z_0-9]*)_([0-9]+)_([0-9]+)_([^0-9]+)_(random|clrandom|original|cloriginal)_([0-9]+)_([0-9]+)(_.*|)_result.pickle")
# div_monolithic_lns_mips_gcc.alias.get_frame_alias_set_10_1000_br_hamming_clrandom_105_0.4_10000_constant.pickle
pat2 = re.compile("_([01]\.[0-9]+)_([0-9]+)_([a-z]+)")

filepat = re.compile("divs_[0-9]+_[0-9]$")


metrics = ["br_hamming", "levenshtein", "hamming", "diff_br_hamming", "reg_hamming", "hamm_reg_gadget", "reg_gadget", "cyc_gadget"]
rrates = rrates =  ["-", "0.1", "0.2", "0.4", "0.6", "0.7", "0.8", "0.9"]


# Sort by number of bblocks and then number of ins
benchmarks = [
		"sphinx3.profile.ptmr_init",
		"gcc.expmed.ceil_log2",
		"mesa.api.glIndexd",
		"h264ref.vlc.symbol2uvlc",
		"gobmk.owl_defendpat.autohelperowl_defendpat421",
		"mesa.api.glVertex2i",
		"hmmer.tophits.AllocFancyAli",
		"gobmk.owl_vital_apat.autohelperowl_vital_apat34",
		"gobmk.patterns.autohelperpat1088",
		"gobmk.owl_attackpat.autohelperowl_attackpat68",
		"gobmk.board.get_last_player",
		"h264ref.sei.UpdateRandomAccess",
		"gcc.xexit.xexit",
		"gcc.jump.unsigned_condition",
		"sphinx3.glist.glist_tail",
		"gcc.alias.get_frame_alias_set",
		"gcc.rtlanal.parms_set"]

# Sort by number of instructions
#benchmarks = [ "sphinx3.profile.ptmr_init", 
#		"sphinx3.glist.glist_tail",
#		"gobmk.board.get_last_player",
#		"gcc.expmed.ceil_log2",
#		"mesa.api.glIndexd",
#		"h264ref.vlc.symbol2uvlc",
#		"h264ref.sei.UpdateRandomAccess",
#		"gcc.xexit.xexit",
#		"gcc.alias.get_frame_alias_set",
#		"mesa.api.glVertex2i",
#		"gobmk.owl_defendpat.autohelperowl_defendpat421",
#		"gcc.jump.unsigned_condition",
#		"gcc.rtlanal.parms_set",
#		"hmmer.tophits.AllocFancyAli",
#		"gobmk.owl_vital_apat.autohelperowl_vital_apat34",
#		"gobmk.patterns.autohelperpat1088",
#		"gobmk.owl_attackpat.autohelperowl_attackpat68"]
#

# Values for histogram (<=) for every field
# [0,0], (0,5%], (5%,10%], (10%,20%], (20%,40%], (40%,60%], (60%,80%], (80%,100%]
#vals = [0.0, 0.1, 0.3, 0.6, 1.0]
vals = [0.0, 0.1, 0.4, 1.0]

def print_metric(metric):
    if metric == "diff_br_hamming": return "diff"
    elif metric == "br_hamming": return "br"
    elif metric == "hamming": return "hamm"
    elif metric == "levenshtein": return "lev"
    elif metric == "reg_hamming": return "reg"
    elif metric == "hamm_reg_gadget": return "hrg"
    elif metric == "reg_gadget": return "rg"
    elif metric == "cyc_gadget": return "cg"
    else: return "None"
    
 
if (len(sys.argv) < 5):
    print "Give as argument folder to the bench folders and the metric"
    print "python extract_results.py <divs_? folder> <max|both> <perc=true|false>" 
    exit (0)

path = sys.argv[1]
gmetric = sys.argv[2]
perc = sys.argv[3] == "true"
savefolder = sys.argv[4]
#agap = sys.argv[3]


def print_dat(d, vals):
        res = [ "%d%%"%(d[k]*100) if d.has_key(k) else "-" for k in vals ]
        return "|".join(res)

def compress_data(data):
    tmp = dict()
    ndat = dict()
    #temp = d[ag][bench][r][m][meas]["data"]
    allsum = sum(data.values())
    for i in data:
        for v in vals:
            if i <= v:
                if tmp.has_key(v):
                    tmp[v] += data[i]
                else: 
                    tmp[v] = data[i]
                break
    for v in tmp:
        val = round(tmp[v]/float(allsum),2)
        if val > 0.0 :
            ndat[v] = val
    return ndat


# Open a file
l = dict()
d = dict()
#dist_vs_gadgets = {'gadget': dict(), 'hamm': dict(), 'brhamm': dict(), 'brdiff': dict(), 'reghamm': dict(), 'lev': dict()}
#dist_vs_gadgets_points = dict()
d_rc = dict()

def update_dict(d, d1):
    for srate in d1:
        if d.has_key(srate):
            d[srate].update(d1[srate])
        else:
            d[srate] = d1[srate]

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
                #if inp.has_key("dist_vs_gadgets"):
                #    if type(inp['dist_vs_gadgets']) == type(dict()):
                #      for fiel in inp['dist_vs_gadgets']:
                #        update_dict(dist_vs_gadgets[fiel], inp['dist_vs_gadgets'][fiel])
                        #dist_vs_gadgets[fiel].update(inp['dist_vs_gadgets'][fiel])
                #if inp.has_key("dist_vs_gadgets_points"):
                #    update_dict(dist_vs_gadgets_points, inp['dist_vs_gadgets_points'])
                #if inp.has_key("rc"):
                #    update_dict(d_rc, inp['rc'])
            else:
                print "Error", inp[gmetric]

        for dat,i,j,k1,k2 in m:
            a = re.match(pat,i)
            islns = True
            try:
                experiment,method, arch, bench, gap, nodivs, metric, branching, seed, mindist, rest = a.groups()
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
                if not d[gap][bench][relax][metric].has_key(mindist):
                    d[gap][bench][relax][metric][mindist] = dict()
                d[gap][bench][relax][metric][mindist][meas] = {'num': j, 'mean': k1, 'std': k2, 'data': dat}
            except:
                print "Exception 2", i

        if not perc:
            print "".join(map(lambda x: x.ljust(17), ["Benchmark".ljust(50), "Relax"] + metrics) )
        else: 
            print "".join(["Benchmark".ljust(10), "Relax".ljust(10)] + map(lambda x: x.ljust(30), metrics) )
        for ag in d:
          print "-----------------------------------------------"
          print "-%s-"%ag
          print "-----------------------------------------------"
          mindist = "1"
          for bi,bench in enumerate(benchmarks,1):
            if not d[ag].has_key(bench): continue
            for r in rrates:
                if r not in d[ag][bench]:
                    continue
                if not perc:
                  print "".join([bench.ljust(50)] + map(lambda x: x.ljust(17), [r ] +[  "-" if not d[ag][bench][r].has_key(m)  or not d[ag][bench][r][m].has_key(mindist) or not d[ag][bench][r][m][mindist].has_key(meas) or d[ag][bench][r][m][mindist][meas]["mean"]== "Average" else (str(ufloat(d[ag][bench][r][m][mindist][meas]["mean"], d[ag][bench][r][m][mindist][meas]['std'])*100) + "%"  + " (" + str(d[ag][bench][r][m][mindist][meas]["num"]) + ")" ) for m in metrics ]))
                else: 
                  dat = dict()
                  #tdat = dict()
                  for m in metrics:
                    temp = dict() if not d[ag][bench][r].has_key(m) or not d[ag][bench][r][m].has_key(mindist) or not d[ag][bench][r][m][mindist].has_key(meas) or d[ag][bench][r][m][mindist][meas]["mean"]== "Average"  else d[ag][bench][r][m][mindist][meas]["data"]
                    dat[m] = compress_data(temp)

                  print "".join([("b" + str(bi)).ljust(10), r.ljust(10)] + map(lambda x: x.ljust(30),[ "-" if not dat.has_key(m) or not d[ag][bench][r].has_key(m) or not d[ag][bench][r][m].has_key(mindist) or not d[ag][bench][r][m][mindist].has_key(meas) else "%s(%d)"%(print_dat(dat[m], vals),d[ag][bench][r][m][mindist][meas]['num']) for m in metrics ]))

                
                
        print "-----------------------------------------------"
        for ag in d:
          print "-----------------------------------------------"
          print "-%s-"%ag
          print "-----------------------------------------------"
          mindist = "1"
          for r in rrates:
            if not l.has_key(r): l[r] = dict()
            for metric in metrics:
                k = [ (d[ag][b][r][metric][mindist][meas]["mean"],d[ag][b][r][metric][mindist][meas]["std"],d[ag][b][r][metric][mindist][meas]['num'])  for b in d[ag] if d[ag][b].has_key(r) and d[ag][b][r].has_key(metric) and d[ag][b][r][metric].has_key(mindist) and d[ag][b][r][metric][mindist].has_key(meas) and d[ag][b][r][metric][mindist][meas]["mean"] != "Average"]
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

mindist = "1"
ks = sorted({ k for ag in d for bench in d[ag] for r in d[ag][bench] for m in d[ag][bench][r] for k in d[ag][bench][r][m]}, key = lambda x: int(x))
for ki in ks:
 for ag in d:
  print "-------------------------------------------------------------------------------"
  print "-------------------------------%s-------------------------------------------" %ag
  print "-------------------------------------------------------------------------------"
  for r in rrates:
    print "-------------------------------------------------------------------------------"
    print "-------------------------------------------------------------------------------"
    print "".join(map(lambda x: x.ljust(17), ["Benchmark".ljust(50), "Relax"] + metrics) )
    print "-------------------------------------------------------------------------------"
    for bench in d[ag]:
        if r not in d[ag][bench]:
            continue
        for metric in metrics:
            if not d[ag][bench][r].has_key(metric): continue
            if not d[ag][bench][r][metric].has_key(ki): continue
            k = [(d[ag][bench][r][metric][ki][meas]['mean'],d[ag][bench][r][metric][ki][meas]['std'],d[ag][bench][r][metric][ki][meas]['num']) for meas in d[ag][bench][r][metric][ki]]
            num = sum([n for m,s,n in k])
            mean = sum([m*n for m,s,n in k])/num #sum([n for m,s,n in k])
            qs = [ m**2+s**2*(n-1)/n for m,s,n in k]
            q = sum([ q*n for (m,s,n), q in zip(k,qs)])/num # sum([n for m,s,n in k])
            std = math.sqrt(q-mean**2)
            d[ag][bench][r][metric][ki]['res'] = (mean,std) #ufloat(mean,std)
            d[ag][bench][r][metric][ki]['avgnum'] = num/len(k)
            #print metric, bench, ufloat(mean,std)


        print "".join([bench.ljust(50)] + map(lambda x: x.ljust(17), [r] +[ "-" if not d[ag][bench][r].has_key(m) or not d[ag][bench][r][m].has_key(ki) else (str((ufloat(*d[ag][bench][r][m][ki]['res'])*100).format("2.2")) + "% " + "(" + str(d[ag][bench][r][m][ki]['avgnum']) +  ")") for m in metrics ]))
        

for ki in ks:
 for ag in d:
  for r in rrates:
    print "-------------------------------------------------------------------------------"
    print "".join(map(lambda x: x.ljust(17), ["Benchmark".ljust(50), "Relax"] + metrics) )
    print "-------------------------------------------------------------------------------"
    for bench in d[ag]:
        if r not in d[ag][bench]:
            continue
        for metric in metrics:
            if not d[ag][bench][r].has_key(metric): continue
            if not d[ag][bench][r][metric].has_key(ki): continue
            k = [(d[ag][bench][r][metric][ki][meas]['data'],d[ag][bench][r][metric][ki][meas]['num']) for meas in d[ag][bench][r][metric][ki] if meas.startswith("divs")]
            if len(k) == 0: continue
            ds, nums = zip(*k)
            
            data = dict()
            for di in ds:
                for v in di:
                    if data.has_key(v):
                        data[v] += di[v]
                    else:
                        data[v] = di[v]
            d[ag][bench][r][metric][ki]['data'] = data
            d[ag][bench][r][metric][ki]['avgnum'] = sum(nums)/len(nums)
            #print metric, bench, ufloat(mean,std)

# {0.25: 1602, 0.0: 194588, 0.6: 107, 0.2: 9770, 0.4: 210, 0.1: 37773, 0.15: 11554, 0.3: 1138, 0.05: 20939, 0.45: 120, 0.7: 6, 0.35: 317, 0.55: 42, 0.65: 7, 0.5: 427}
# {0.25: 1833, 0.0: 221637, 0.6: 117, 0.2: 11492, 0.4: 236, 0.1: 43676, 0.15: 13872, 0.3: 1289, 0.05: 23182, 0.45: 130, 0.7: 6, 0.35: 378, 0.55: 54, 0.65: 9, 0.5: 489}

# Write outputs.
    
def formatout(v, bold=False):
    res = ufloat(*v['res'])
    num = str(v['avgnum'])
    vf = '{:.2f}'.format(res*100) + "%" + "(" + num +  ")"
    #vf = str(vf) + "%"
    if bold:
        return "\\textbf{" + vf + "}"
    else: 
        return vf
 
cmetrics = map(lambda x: x.replace("_", ""), metrics)

mindist = "1"
for ag in d:
  for r in rrates:
    with open(os.path.join(savefolder,"output" + r + ag + ".csv"), "w") as f:
        f.write(",".join(["Benchmark"] + cmetrics))
        f.write("\n")
        for bi,bench in enumerate(benchmarks, 1):
            if ag not in d: continue
            if bench not in d[ag]: continue
            if r not in d[ag][bench]: continue
            # find minimum values to mark
            data = [ (ufloat(*d[ag][bench][r][m][mindist]['res']),m) for m in metrics if d[ag][bench][r].has_key(m) and d[ag][bench][r][m].has_key(mindist)]
            mind = min(data, key=lambda (res,m): res)
            minds = filter(lambda (x,m): abs(x- mind[0]) < 0.005, data)
            _, minms = zip(*minds)
            data = ["b" + str(bi)] + [ "-" if not d[ag][bench][r].has_key(m) or not d[ag][bench][r][m].has_key(mindist) else formatout(d[ag][bench][r][m][mindist], m in minms) for m in metrics ]
            cdata = map (lambda x: x.replace("_", "\\_"), data)
            cdata = map (lambda x: x.replace("%", "\\%"), cdata)
            cdata = map (lambda x: x.replace("+/-", "$\\pm$"), cdata)
            f.write(",".join(cdata))
            f.write("\n")

# HIST
def formatdataout(v):
    dat = compress_data(v['data'])
    num = str(v['avgnum'])
    it = dat.items()
    mi,m = max(it, key=lambda (gs,v):v)
    fm = filter(lambda (xi,x): abs(x-m) <= 0.05, it)
    mis,ms = zip(*fm)
    res = {di:"%d"%(dat[di]*100) if dat.has_key(di) else "-" for di in vals }
    for mi in mis:
        res[mi] = "\\textbf{" + res[mi] + "}"
    vf = ",".join([ res[i] for i in vals]) + "," + num
    return vf
    #vf = str(vf) + "%"
 
mindist = "1"
for ag in d:
  for r in rrates:
    with open(os.path.join(savefolder,"hist_output" + r + ag + ".csv"), "w") as f:
        #f.write(",".join(["Benchmark"] + cmetrics))
        #f.write("\n")
        f.write(",".join([""] + [ ",".join(map(lambda x: "\\tiny{%s}"%x, [("$\\le$" if v>0 else "$=$") + str(int(v*100))   for v in vals] + ["num"]) ) for _ in cmetrics]))
        #f.write(",".join(["Benchmark"] + cmetrics))
        f.write("\n")
        for bi,bench in enumerate(benchmarks, 1):
            #if bench not in d[ag]: continue
            #if r not in d[ag][bench]: continue
            # find minimum values to mark
            data = ["b" + str(bi)] + [ ",".join([ "-" for _ in range(len(vals)+1)])  if  not d[ag].has_key(bench) or not d[ag][bench].has_key(r) or not d[ag][bench][r].has_key(m) or not d[ag][bench][r][m].has_key(mindist) else formatdataout(d[ag][bench][r][m][mindist]) for m in metrics ]
            cdata = map (lambda x: x.replace("_", "\\_"), data)
            cdata = map (lambda x: x.replace("%", "\\%"), cdata)
            cdata = map (lambda x: x.replace("+/-", "$\\pm$"), cdata)
            cdata = map (lambda x: x.replace("|", "$|$"), cdata)
            f.write(",".join(cdata))
            f.write("\n")
 
rrates2 = ["-", "0.7"]
for ag in d:
  for m in metrics:
    with open(os.path.join(savefolder,"hist_output" + m + ag + ".csv"), "w") as f:

        f.write(",".join([""] + [ ",".join(map(lambda x: "\\tiny{%s}"%x, [("$\\le$" if v>0 else "$=$") + str(int(v*100))   for v in vals] + ["num"]) ) for _ in rrates2]))
        f.write("\n")
        for bi,bench in enumerate(benchmarks, 1):
            if not d.has_key(ag): continue
            if not d[ag].has_key(bench): continue
            #if not d[ag][bench].has_key(r): continue
            #if not d[ag][bench][r].has_key(m): continue
            #if not d[ag][bench][r][m].has_key(mindist): continue
            # find minimum values to mark
            data = [ (ufloat(*d[ag][bench][r][m][mindist]['res']),r) for r in rrates if d[ag][bench].has_key(r) and d[ag][bench][r].has_key(m) and d[ag][bench][r][m].has_key(mindist) ]
            data = ["b" + str(bi)] + [ ",".join([ "-" for _ in range(len(vals)+1)])  if  not d[ag].has_key(bench) or not d[ag][bench].has_key(r) or not d[ag][bench][r].has_key(m) or not d[ag][bench][r][m].has_key(mindist) else formatdataout(d[ag][bench][r][m][mindist]) for r in rrates2]
            if data == []: continue
            cdata = map (lambda x: x.replace("_", "\\_"), data)
            cdata = map (lambda x: x.replace("%", "\\%"), cdata)
            cdata = map (lambda x: x.replace("+/-", "$\\pm$"), cdata)
            cdata = map (lambda x: x.replace("|", "$|$"), cdata)
            f.write(",".join(cdata))
            f.write("\n")

   
for ag in d:
  for m in metrics:
    with open(os.path.join(savefolder,"output" + m + ag + ".csv"), "w") as f:
        f.write(",".join(["Benchmark"] + rrates))
        f.write("\n")
        for bi,bench in enumerate(benchmarks, 1):
            if not d.has_key(ag): continue
            if not d[ag].has_key(bench): continue
            #if not d[ag][bench].has_key(r): continue
            #if not d[ag][bench][r].has_key(m): continue
            #if not d[ag][bench][r][m].has_key(mindist): continue
            # find minimum values to mark
            data = [ (ufloat(*d[ag][bench][r][m][mindist]['res']),r) for r in rrates if d[ag][bench].has_key(r) and d[ag][bench][r].has_key(m) and d[ag][bench][r][m].has_key(mindist) ]
            if data == []: continue
            mind = min(data, key=lambda (res,r): res)
            minds = filter(lambda (x,r): abs(x- mind[0]) < 0.005, data)
            _, minms = zip(*minds)
            data = ["b" + str(bi)] + [ "-" if not d[ag][bench].has_key(r) or not d[ag][bench][r].has_key(m) or not d[ag][bench][r][m].has_key(mindist)  else formatout(d[ag][bench][r][m][mindist], r in minms) for r in rrates ]
            cdata = map (lambda x: x.replace("_", "\\_"), data)
            cdata = map (lambda x: x.replace("%", "\\%"), cdata)
            cdata = map (lambda x: x.replace("+/-", "$\\pm$"), cdata)
            f.write(",".join(cdata))
            f.write("\n")

agaps = sorted(d.keys(), key=lambda x: int(x))
print "agaps", agaps
for m in metrics:
  for r in rrates:
    with open(os.path.join(savefolder,"gaps_output" + m + r + ".csv"), "w") as f:
        f.write(",".join(["Benchmark"] + agaps ))
        f.write("\n")
        for bi,bench in enumerate(benchmarks, 1):
            # find minimum values to mark
            data = [ (ufloat(*d[ag][bench][r][m][mindist]['res']),ag) for ag in agaps if d[ag].has_key(bench) and d[ag][bench].has_key(r)  and d[ag][bench][r].has_key(m) and d[ag][bench][r][m].has_key(mindist)]
            if data == []: continue
            mind = min(data, key=lambda (res,ag): res)
            minds = filter(lambda (x,ag): abs(x- mind[0]) < 0.005, data)
            _, minms = zip(*minds)
            data = ["b" + str(bi)] + [ "-" if not d[ag].has_key(bench) or not d[ag][bench].has_key(r) or not d[ag][bench][r].has_key(m)  or not d[ag][bench][r][m].has_key(mindist) else formatout(d[ag][bench][r][m][mindist], ag in minms) for ag in agaps ]
            cdata = map (lambda x: x.replace("_", "\\_"), data)
            cdata = map (lambda x: x.replace("%", "\\%"), cdata)
            cdata = map (lambda x: x.replace("+/-", "$\\pm$"), cdata)
            f.write(",".join(cdata))
            f.write("\n")
 
  
#for ag in d:
for m in metrics:
  for r in rrates:
    with open(os.path.join(savefolder,"hist_gaps_output" + r + m + ".csv"), "w") as f:
        #f.write(",".join(["Benchmark"] + cmetrics))
        #f.write("\n")
        f.write(",".join([""] + [ ",".join(map(lambda x: "\\tiny{%s}"%x, [("$\\le$" if v>0 else "$=$") + str(int(v*100))   for v in vals] + ["num"]) ) for _ in agaps]))
        #f.write(",".join(["Benchmark"] + cmetrics))
        f.write("\n")
        for bi,bench in enumerate(benchmarks, 1):
            # find minimum values to mark
            data = ["b" + str(bi)] + [ ",".join([ "-" for _ in range(len(vals)+1)]) if  not d.has_key(ag) or not d[ag].has_key(bench) or not d[ag][bench].has_key(r) or not d[ag][bench][r].has_key(m) or not d[ag][bench][r][m].has_key(mindist) else formatdataout(d[ag][bench][r][m][mindist]) for ag in agaps ]
            cdata = map (lambda x: x.replace("_", "\\_"), data)
            cdata = map (lambda x: x.replace("%", "\\%"), cdata)
            cdata = map (lambda x: x.replace("+/-", "$\\pm$"), cdata)
            cdata = map (lambda x: x.replace("|", "$|$"), cdata)
            f.write(",".join(cdata))
            f.write("\n")

print "ks", ks
for ag in agaps:
 for m in metrics:
  for r in rrates:
    with open(os.path.join(savefolder,"hist_k_output" + r + m + ag + ".csv"), "w") as f:
        #f.write(",".join(["Benchmark"] + cmetrics))
        #f.write("\n")
        f.write(",".join([""] + [ ",".join(map(lambda x: "\\tiny{%s}"%x, [("$\\le$" if v>0 else "$=$") + str(int(v*100))   for v in vals] + ["num"]) ) for _ in agaps]))
        #f.write(",".join(["Benchmark"] + cmetrics))
        f.write("\n")
        for bi,bench in enumerate(benchmarks, 1):
            # find minimum values to mark
            data = ["b" + str(bi)] + [ ",".join([ "-" for _ in range(len(vals)+1)]) if  not d.has_key(ag) or not d[ag].has_key(bench) or not d[ag][bench].has_key(r) or not d[ag][bench][r].has_key(m) or not d[ag][bench][r][m].has_key(k) else formatdataout(d[ag][bench][r][m][k]) for k in ks ]
            cdata = map (lambda x: x.replace("_", "\\_"), data)
            cdata = map (lambda x: x.replace("%", "\\%"), cdata)
            cdata = map (lambda x: x.replace("+/-", "$\\pm$"), cdata)
            cdata = map (lambda x: x.replace("|", "$|$"), cdata)
            f.write(",".join(cdata))
            f.write("\n")


with open(os.path.join(savefolder,"benchmarks.csv"), "w") as f:
    f.write(",".join(["Bid", "Benchmark"]))
    f.write("\n")
    for bi,b in enumerate(benchmarks,1):
        b = b.replace("_", "\\_")
        b = b.replace("%", "\\%")
        b = b.replace("+/-", "$\\pm$")
 
        f.write(",".join(["b" + str(bi), b])) 
        f.write("\n")
    
    
pickle.dump(d, open("divs_gadgets.pickle", "w"))
#pickle.dump(d_rc, open("d_rc.pickle", "w"))

#pickle.dump(dist_vs_gadgets, open("dist_vs_gadgets.pickle", "w"))
#pickle.dump(dist_vs_gadgets_points, open("dist_vs_gadgets_points.pickle", "w"))
