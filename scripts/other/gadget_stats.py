#! env python

import matplotlib.pyplot as plt
import numpy as np
from uncertainties import ufloat

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

rrates = [ "0.1", "0.2", "0.4", "0.6", "0.8", "0.9"]
metrics = ["hamming", "br_hamming", "diff_br_hamming", "levenshtein", "reg_hamming", "hamm_reg_gadget"]

def get_num(r):                       
     if r == '-':
         return 0    
     else:                                                                                                                                      
         return float(r) 

def get_relax(d, bench, metric):
     ls = []                                   
     for r in rrates:                 
         l = ufloat(-1.,0) if not d.has_key(bench) or not d[bench].has_key(r) or not d[bench][r].has_key(metric) else d[bench][r][metric]['res']
         if l > -1:     
             ls.append((l[0],get_num(r)))
     return ls

def plot_bench(d, metric):
     for bi,b in enumerate(benchmarks,1):
          if not d.has_key(b): continue
          yx = get_relax(d, b, metric)
          if len(yx) == 0: continue    
          y,x = zip(*yx)
          plt.plot(x,y,'ko')
          plt.plot(x,y,'--',label="b" + str(bi))
     yax = np.arange(0,1,0.05)
     plt.yticks(yax, map(lambda i: str(int(i)) + "%", 100*yax))
     plt.ylabel("Gadget survival")
     xax = np.array(x)
     plt.xticks(xax, map(lambda i: str(int(i)) + "%", 100*xax))
     plt.xlabel("LNS relax rate")
     plt.title(metric)
     plt.legend()
     plt.show()

def plot_metric(d, bench):
     if not d.has_key(bench): return

     for m in metrics:
          yx = get_relax(d, bench, m)
          if len(yx) == 0: continue    
          y,x = zip(*yx)
          plt.plot(x,y,'ko')
          plt.plot(x,y,'--',label=m)
     plt.title(bench)
     plt.legend()
     plt.show()

def plot_agap(d, relax, metric):
     agaps = sorted(d.keys(), key=lambda x:int(x))
     xticks = set()
     for bi,bench in enumerate(benchmarks,1):
	     ls = []
	     for agap in agaps:
		if not d[agap].has_key(bench) or not d[agap][bench].has_key(relax) or not d[agap][bench][relax].has_key(metric): continue
		l = int(agap),d[agap][bench][relax][metric]['res'][0]
		ls.append(l)
	     if len(ls) == 0: continue
	     x,y = zip(*ls)
	     xticks.update(x)
	     plt.plot(x,y,'ko')
	     plt.plot(x,y,'--',label="b" + str(bi))
     plt.xticks(list(xticks))
     plt.title("rel=%s, metric: %s" %(relax, metric))
     plt.legend()
     plt.show()

def plot_agap_two(d, relaxes, metrics):
    agaps = sorted(d.keys(), key=lambda x:int(x))
    for i, (relax,metric) in enumerate(zip(relaxes,metrics),1):
        xticks = set()
        ax = plt.subplot(220 + i)
        for bi,bench in enumerate(benchmarks,1):
             ls = []
	     for agap in agaps:
		if not d[agap].has_key(bench) or not d[agap][bench].has_key(relax) or not d[agap][bench][relax].has_key(metric): continue
		l = int(agap),100*d[agap][bench][relax][metric]['res'][0]
		ls.append(l)
	     if len(ls) == 0: continue
	     x,y = zip(*ls)
	     xticks.update(x)
	     ax.plot(x,y,'ko')
	     ax.plot(x,y,'--',label="b" + str(bi))
        ax.set_xticks(list(xticks))
        ax.legend()
        ax.set_title("rel=%s, metric: %s" %(relax, metric))
        ax.set_xlabel("Gap from optimal (%)")
        ax.set_ylabel("Gadget survival (%)")
    plt.show()

def plot_agap_rel(d, metric, bench):
     agaps = sorted(d.keys(), key=lambda x:int(x))
     xticks = set()
     for relax in rrates:
	     ls = []
	     for agap in agaps:
		if not d[agap].has_key(bench) or not d[agap][bench].has_key(relax) or not d[agap][bench][relax].has_key(metric): continue
		l = int(agap),d[agap][bench][relax][metric]['res'][0]
		ls.append(l)
	     if len(ls) == 0: continue
	     x,y = zip(*ls)
	     xticks.update(x)
	     plt.plot(x,y,'ko')
	     plt.plot(x,y,'--',label=relax)
     plt.xticks(list(xticks))
     yax = np.arange(0,1,0.05)
     plt.yticks(yax, map(lambda x: str(int(x)) + "%", 100*yax))
     plt.title("bench=%s, metric: %s" %(bench, metric))
     plt.legend()
     plt.show()


