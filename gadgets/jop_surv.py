import re
from capstone import *
from subprocess import *
import os, sys
import cPickle as pickle
import math

pat = r"(0x[0-9a-fA-F]+) : (.*)"

def filter_nops(code): return filter(lambda x: x != 'nop', code)
def strip(code): return map(lambda x: x.strip(), code)

if (len(sys.argv) < 3):
    print "Give as argument the path with the compiled binaries"
    print "python jop_surv.py <path-to-dot-o-files> <filename>"
    exit(0) 


path = sys.argv[1]
filename = ".".join(sys.argv[2].split(".")[:-1])

# Open a file
dirs = os.listdir( path )

max_num = 500

files = []
mncount = 0
for fil in dirs:
    if fil.endswith(".o"):
        newfile = os.path.join(path, fil)
        files.append(newfile)
        mncount += 1
        if (mncount >= max_num): break

d = dict()
print "Number divs", len(files)
d['numdivs'] = len(files)
# print files

pat2 = r".*Gadgets information\n=+\n(.*)Unique gadgets found: ([0-9]+).*"
t = [ [ 0. for i in files ] for j in files ] 
res = []
for iinp, inp in enumerate(files): 
    command = "ROPgadget.py --binary %s --rawArch mips --rawMode 32 --rawEndian little --nosys" %inp
    p1 = Popen(command.split(), stdout=PIPE)
    output,err = p1.communicate()

    #print output.split("\n")
    out, numbergadgets = re.match(pat2, output, re.DOTALL).groups()
    numbergadgets = int(numbergadgets)

    print "Number Gadgets", inp, numbergadgets

    if numbergadgets == 0:
        #d[inp] = { inp2: 0. for inp2 in files }
        continue
    #with open("test.ropgadget.txt") as f:
    #    a = [re.match(pat,i).groups() for i in f.readlines()]
    a = [re.match(pat,i).groups() for i in filter(lambda x: x!='', out.split("\n"))]

    b = [ (i,strip(j.split(";"))) for i,j in a]

    c = [ (int(i,16), filter_nops(j)) for i,j in b]


    addresses, code = zip(*c)
    maxgad = 20*4
    ## Not working need to take care of headers etc
    for iinp2, inp2 in enumerate(files):
        if iinp2 == iinp: continue
        #if inp == inp2: break

        fil = open(inp2, "rb").read()
        md = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 + CS_MODE_LITTLE_ENDIAN)

        count = 0.0
        for i,ad in enumerate(addresses):
            code2 = []
            for cod in md.disasm(fil[ad:ad+maxgad], ad):    
                code2.append("%s %s" %(cod.mnemonic,cod.op_str))
            code2 = filter_nops(strip(code2))
            for j, ci in enumerate(code[i]):
                if len(code2) <= j or ci != code2[j]:
                    break
            else:
                count += 1.0
        t[iinp][iinp2] = count/(1.0*numbergadgets)
        res.append((count, numbergadgets))



#for inp in d:
c,ng = zip(*res)
print "All Count", sum(c)
d["All Count"] = sum(c)
print "All Gadgets", sum(ng) 
d["All Gadgets"] = sum(ng)


def calc_stats(summa, d):
    s = sum(summa)
    c = len(summa)
    avg = s/c
    std = [(i-avg)**2 for i in summa]
    std = math.sqrt(sum(std)/(len(std)-1)) 
    conf = 2.* std/math.sqrt(len(summa))

    #data
    fd = dict()
    for i in summa:
        if df.has_key(i):
            df[i] += 1
        else:
            df[i] = 1

    d["data"] = df
    d["summa"] = s
    d["count"] = c
    d["avg"] = avg
    d["std"] = std
    d["conf"] = conf


summa = []
for i in range(len(t)):
    for j in range(i+1,len(t)):
        summa.append(max(t[i][j],t[j][i]))

d["max"] = dict()
calc_stats(summa, d["max"])

summa = []
for i in range(len(t)):
    for j in range(len(t)):
        if j==i: continue
        summa.append(t[i][j])

d["both"] = dict()
calc_stats(summa, d["both"])

pickle.dump(d, open(os.path.join(path , filename + "_result.pickle"), "w"))

# pickle.dump(t, open(filename + "_test.pickle", "w"))

