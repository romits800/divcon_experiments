import re
from capstone import *
from subprocess import *
import os

pat = r"(0x[0-9a-fA-F]+) : (.*)"

def filter_nops(code): return filter(lambda x: x != 'nop', code)
def strip(code): return map(lambda x: x.strip(), code)


# Open a file
path = "/home/romi/didaktoriko/teaching/is1200/labs/gadgets/"
dirs = os.listdir( path )

# This would print all the files and directories
files = []

for fil in dirs:
    if fil.endswith(".o"):
        files.append(path + fil)
print len(files)

pat2 = r".*Gadgets information\n=+\n(.*)Unique gadgets found: ([0-9]+).*"
t = [ [ 0. for i in files ] for j in files ] 
for iinp, inp in enumerate(files): 
    command = "ROPgadget.py --binary %s --rawArch mips --rawMode 32 --rawEndian little" %inp
    p1 = Popen(command.split(), stdout=PIPE)
    output,err = p1.communicate()

    #print output.split("\n")
    out, numbergadgets = re.match(pat2, output, re.DOTALL).groups()
    numbergadgets = int(numbergadgets)

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

#for inp in d:

summa = 0.
count = 0.

for i in range(len(t)):
    for j in range(i+1,len(t)):
        summa += max(t[i][j],t[j][i])
        count += 1.
print summa
print count
print summa/count
