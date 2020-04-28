#! env python


import cPickle as pickle
import visualize_interactive as vi
import os
import sys

if len(sys.argv) < 2:
	print "Give the path to divcon_experiments as the first argument"

res_folder = os.path.join(sys.argv[1], "results")

pickles = "pickles"
maxdiv = "maxdiv_lns_rs"
rest = "rest"

d_max_div = pickle.load(open(os.path.join(res_folder, pickles, "max_div_divs.pickle")))

for b in vi.benchmarks:
    if d_max_div.has_key(b):
	vi.plot_maxdiv_lns_new(d_max_div, b, "hamming", "avg", 10, 0.8, "1", dist=False, path=os.path.join(res_folder, maxdiv))
	vi.plot_maxdiv_lns_new(d_max_div, b, "hamming", "avg", 10, 0.8, "1", dist=True, path=os.path.join(res_folder, maxdiv))

# LNS evaluation
vi.tex_max_lns_rs(d_max_div, "hamming", "avg", 10, 200, "1", ["0.7"], texname=os.path.join(res_folder, maxdiv, "max_lns_rs_table"), show=False)

d_rest = pickle.load(open(os.path.join(res_folder, pickles, "rest_divs.pickle")))

vi.tex_agap(d_rest, "hamming", "avg", [0, 5, 10,20], 200, "1", "0.7", texname=os.path.join(res_folder, rest, "lns_gaps"), show=False)

# Benchmarks
vi.tex_benchmarks(texname=os.path.join(res_folder, rest, "benchmarks"))

# Distance evaluation
vi.tex_distances(d_rest, "avg", "10", 200, "1", "0.7", ["hamming", "levenshtein"], texname=os.path.join(res_folder, rest, "lns_distances"), show=False)

# Generate figures for appendix - Selection of relax rate
colors = ['rosybrown', "firebrick", "darkred","chocolate", "darkorange", "khaki", "yellowgreen", "limegreen",
	  "darkgreen", "steelblue", "darkblue", "slateblue", "darkorchid","purple", "crimson"]
vi.plot_rs_vs_lns(d_rest, "hamming", "avg", 10, colors, 200, "1", dist=False, path=os.path.join(res_folder, rest))
vi.plot_rs_vs_lns(d_rest, "hamming", "avg", 10, colors, 200, "1", path=os.path.join(res_folder, rest))
