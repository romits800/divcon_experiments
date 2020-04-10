#! env python


import cPickle as pickle
import visualize_interactive as vi

d_max_div = pickle.load(open("max_div_divs.pickle"))

for b in vi.benchmarks:
	vi.plot_maxdiv_lns_new(d_max_div, b, "hamming", "avg", 10, 0.8, "1", dist=False, path="results/maxdiv_lns_rs/")
	vi.plot_maxdiv_lns_new(d_max_div, b, "hamming", "avg", 10, 0.8, "1", dist=True, path="results/maxdiv_lns_rs/")

# LNS evaluation
vi.tex_max_lns_rs(d_max_div, "hamming", "avg", 10, 200, "1", ["0.7"], texname='results/maxdiv_lns_rs/max_lns_rs_table', show=False)

d_rest = pickle.load(open("rest_divs.pickle"))

vi.tex_agap(d_rest, "hamming", "avg", [0, 5, 10,20], 200, "1", "0.7", texname='results/rest/lns_gaps', show=False)

# Distance evaluation
vi.tex_distances(d_rest, "avg", "10", 200, "1", "0.7", ["hamming", "br_hamming", "levenshtein"], texname="results/rest/lns_distances", show=False)

# Generate figures for appendix - Selection of relax rate
colors = ['rosybrown', "firebrick", "darkred","chocolate", "darkorange", "khaki", "yellowgreen", "limegreen", 
	  "darkgreen", "steelblue", "darkblue", "slateblue", "darkorchid","purple", "crimson"]
vi.plot_rs_vs_lns(d_rest, "hamming", "avg", 10, colors, 200, "1", dist=False, path="results/rest/")
vi.plot_rs_vs_lns(d_rest, "hamming", "avg", 10, colors, 200, "1", path="results/rest/")
