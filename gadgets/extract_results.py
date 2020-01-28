#! env python

# grep -E "(python create|^Average|^Number divs)" out2 &> out
with open("out") as f:
    k = f.readlines()

l = zip(k, k[1:], k[2:])[::3]

m = [ (i.split("/")[7], "diff" if "diff_br_hamming" in i else "br" if "br_hamming" in i else "hamm" if "hamming" in i else "lev" if "levenshtein" in i else "None" ,ij.split()[-1], j.split()[-1]) for i,ij,j in l]

print "\t\t".join(["Benchmark", "Metric", "Number Divs", "Gadget Survival"])
for i,j,k,l in m:
    print "\t\t".join([i, j, k,l])

