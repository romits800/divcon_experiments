#! /bin/bash -x
if [ $# -lt 2 ] 
then
    echo "missing argument"
    exit 1
fi
input=$1
fname=$2

opt=
rm /tmp/unison-*
#export PATH=${PATH}:/home/romi/didaktoriko/unison/romi_unison/unison/src/solvers/gecode:/home/romi/didaktoriko/unison/romi_unison/unison/src/solvers/multi_backend/minizinc/:/home/romi/didaktoriko/unison/romi_unison/unison/src/solvers/multi_backend/:/home/romi/didaktoriko/misc/minizinc/MiniZincIDE-2.1.2-bundle-linux-x86_64/ UNISON_DIR=/home/romi/didaktoriko/unison/romi_unison/unison/ #/home/romi/didaktoriko/unison/romi_unison/unison/src/solvers/multi_backend/portfolio-solver -o test.out.json  --verbose test.ext.json
clang $opt -S -target mips -emit-llvm  $input.c
llc $input.ll $opt -march=mips -mcpu=mips32 -unison -unison-no-clean
cp /tmp/unison-*.asm.mir $input.asm.mir
ls /tmp/unison-*[!mn].mir
cp /tmp/unison-*[!mn].mir $input.mir
# /usr/local/bin/uni
uni import --target=Mips $input.mir -o $input.uni --function=$fname --maxblocksize=25 --goal=speed
# /usr/local/bin/uni
uni linearize --target=Mips $input.uni -o $input.lssa.uni
# /usr/local/bin/uni
uni extend --target=Mips $input.lssa.uni -o $input.ext.uni
# /usr/local/bin/uni
uni augment --target=Mips $input.ext.uni -o $input.alt.uni
# /usr/local/bin/uni
uni normalize --target=Mips $input.asm.mir -o $input.llvm.mir
# /usr/local/bin/uni
uni model --target=Mips $input.alt.uni -o $input.json --basefile=$input.llvm.mir +RTS -K20M -RTS
# /usr/local/bin/gecode-presolver
gecode-presolver -o $input.ext.json -dzn $input.dzn --verbose $input.json
# /usr/local/bin/gecode-solver
gecode-solver  -o $input.out.json --verbose $input.ext.json
# /usr/local/bin/uni
uni export --keepnops --target=Mips $input.alt.uni -o $input.unison.mir --basefile=$input.llvm.mir --solfile=$input.out.json



