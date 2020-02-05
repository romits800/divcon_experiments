#! env python

# grep -E "(python create|^Average|^Number divs)" out2 &> out
import re
import sys

pat = re.compile("div_monolithic_([^_]*)_([^_]*)_([a-zA-Z_0-9]*\.[a-zA-Z_0-9]*\.[a-zA-Z_0-9]*)_([0-9]+)_([0-9]+)_([^0-9]+)_(random|clrandom|original|cloriginal)_([0-9]+)(_.*|).pickle")
# div_monolithic_lns_mips_gcc.alias.get_frame_alias_set_10_1000_br_hamming_clrandom_105_0.4_10000_constant.pickle
pat2 = re.compile("_([01]\.[0-9]+)_([0-9]+)_([a-z]+)")

def print_metric(metric):
    if metric == "diff_br_hamming": return "diff"
    elif metric == "br_hamming": return "br"
    elif metric == "hamming": return "hamm"
    elif metric == "levenshtein": return "lev"
    else: return "None"
    
 
filename = "out"
if (len(sys.argv) > 1):
    filename = sys.argv[1]

with open(filename) as f:
    k = f.readlines()

l = zip(k, k[1:], k[2:])
l = filter(lambda (x,y,z): "python" in x and "python" not in z, l) #[::3]

m = [ (i.split("/")[-1],ij.split()[-1], j.split()[-1]) for i,ij,j in l]

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
## 
#         if (print_metric(metric) == arg1):
#             print "\t\t".join([bench, print_metric(metric), method, "-" if method != "lns" else relax,  j, k])
#     else:
#         print "\t\t".join([bench, print_metric(metric), method, "-" if method != "lns" else relax,  j, k])
# 

metrics = ["br_hamming", "levenshtein", "hamming", "diff_br_hamming"]
rrates = ["-"]
print "\t\t".join(["Benchmark", "Relax"] + metrics )
for bench in d:
    #print bench, 
    for r in rrates:
        if r not in d[bench]:
            continue
        #print print_metric(m),  
        print "\t".join([bench, r ,"\t".join([  "-" if m not in d[bench][r] or d[bench][r][m]["gadgets"]== "Average" else (str(round(float(d[bench][r][m]["gadgets"])*100,2)) + "%"  + " (" + d[bench][r][m]["divs"] + ")" ) for m in metrics ])])
        
        
#     
print "###############################################"
l = dict()
for r in rrates:
    if not l.has_key(r): l[r] = dict()
    for m in metrics:
        if not l[r].has_key(m): l[r][m] = dict()
        k = [ float(d[b][r][m]["gadgets"])  for b in d if d[b].has_key(r) and d[b][r].has_key(m) and d[b][r][m]["gadgets"] != "Average"]
#         if len(k)>0:
        l[r][m] = sum(k)/len(k)
#        print r, m, sum(k)/len(k)
#print l
# 
# 
print "\t\t".join(["Relax"] + metrics )
for r in rrates:
    if r not in l:
         continue
#     #print print_metric(m),  
    print "\t".join([r ,"\t".join([ (str(round(float(l[r][m])*100,2)) if l[r][m]!= "Average" else "-") + "%"  for m in metrics if m in l[r]])])
#         
        

