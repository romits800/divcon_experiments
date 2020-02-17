#! env python


def get_relax(d, bench, metric):
     rrates = [ "0.1", "0.2", "0.4", "0.6", "0.8", "0.9"]
     ls = []                                   
     for r in rrates:                 
         l = ufloat(-1.,0) if not d.has_key(bench) or not d[bench].has_key(r) or not d[bench][r].has_key(metric) else d[bench][r][metric]['res']
         if l > -1:     
             ls.append((l.nominal_value,get_num(r)))
     return ls

def plot_bench(d, metric):
     for bi,b in enumerate(sorted(d.keys()),1):
          yx = get_relax(d, b, metric)
          if len(yx) == 0: continue    
          y,x = zip(*yx)
          plt.plot(x,y,'ko')
          plt.plot(x,y,'--',label="b" + str(bi))
     plt.title(metric)
     plt.legend()
     plt.show()

def plot_metric(d, bench):
     metrics = ["hamming", "br_hamming", "diff_br_hamming", "levenshtein", "reg_hamming", "hamm_reg_gadget"]
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

