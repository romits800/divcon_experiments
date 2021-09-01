import pandas as pd
from random import *



mediabench = "g721"
functions = ["alaw2linear", "alaw2ulaw", "g721_decoder", "g721_encoder", "g72x_init_state", 
             "linear2alaw", "linear2ulaw", "predictor_pole", "predictor_zero", "quantize", 
             "reconstruct", "step_size", "tandem_adjust_alaw", "tandem_adjust_ulaw", "ulaw2alaw",
             "ulaw2linear", "update"]

a = pd.read_csv("./stats.csv")
a = a[lambda row: (row["app"] == mediabench) & (row["function"].isin(functions))]



# Select only mediabench 
#fil2 = fil[lambda row: row["app"].isin(mediabench)]
# print only a few columns
#ben[["id","app","mips-ins", "module"]]

ben = a

print ben["mips-ins"]

ben.to_csv("20_sel_g721.csv")

path_to_ll = "/home/romi/didaktoriko/unison/unison-experiments/experiments/test-input/c/mediabench/mips_zip/build-mips/"
with open("bench_g721.txt","w") as f:
   for i in ben.index:
       k =  ben["id"].loc[i].split(".")
       f.write(path_to_ll + k[0] + "/" + '.'.join([k[0],k[1]]) + ".ll" + "|" + k[2] + "\n")

