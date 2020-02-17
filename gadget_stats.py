#! env python

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

def get_relax(d, bench, metric):
     rrates = [ "0.1", "0.2", "0.4", "0.6", "0.8", "0.9"]
     ls = []                                   
     for r in rrates:                 
         l = ufloat(-1.,0) if not d.has_key(bench) or not d[bench].has_key(r) or not d[bench][r].has_key(metric) else d[bench][r][metric]['res']
         if l > -1:     
             ls.append((l.nominal_value,get_num(r)))
     return ls

def plot_bench(d, metric):
     for bi,b in enumerate(benchmarks,1):
          if not d.has_key(b): continue
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

