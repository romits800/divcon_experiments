import pandas as pd
from random import *


mediabench = ["mesa", "mpeg2", "ghostscript", "rasta", "epic", "pgp", "pegwit", "jpeg", "gsm", "g721", "adpcm"]

a = pd.read_csv("./stats.csv")
a = a[lambda row: row["app"].isin(mediabench)]

fil = a[lambda row: (row["mips-ins"] >= 100)  ]

rand = [randint(0,len(fil)) for i in range(20)]

# Select only mediabench 
#fil2 = fil[lambda row: row["app"].isin(mediabench)]
# print only a few columns
#ben[["id","app","mips-ins", "module"]]

ben = fil.loc[fil.index[rand]]

print ben["mips-ins"]

ben.to_csv("20_sel_more_100.csv")

path_to_ll = "/home/romi/didaktoriko/unison/unison-experiments/experiments/test-input/c/mediabench/mips_zip/build-mips/"
with open("bench_more_100.txt","w") as f:
   for i in ben.index:
       k =  ben["id"].loc[i].split(".")
       f.write(path_to_ll + k[0] + "/" + '.'.join([k[0],k[1]]) + ".ll" + "|" + k[2] + "\n")

