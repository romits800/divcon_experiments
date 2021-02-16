#! /bin/bash -x
input=$1
func=$2

export PATH=${PATH}:/home/romi/didaktoriko/unison/romi_unison/divCon/src/solvers/gecode:/home/romi/didaktoriko/unison/romi_unison/divCon/src/solvers/multi_backend/minizinc/:/home/romi/didaktoriko/unison/romi_unison/divCon/src/solvers/multi_backend/:/home/romi/didaktoriko/misc/minizinc/MiniZincIDE-2.1.2-bundle-linux-x86_64/ UNISON_DIR=/home/romi/didaktoriko/unison/romi_unison/divCon/ #/home/romi/didaktoriko/unison/romi_unison/divCon/src/solvers/multi_backend/portfolio-solver -o test.out.json  --verbose test.ext.json
# /usr/local/bin/uni
uni import --target=Mips $input.mir -o $input.uni --function=$func --maxblocksize=25 --goal=speed
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

#echo "/home/romi/didaktoriko/unison/romi_unison/unison/src/solvers/multi_backend/portfolio-solver -o $input.out.json --verbose $input.ext.json"
#/home/romi/didaktoriko/unison/romi_unison/unison/src/solvers/multi_backend/portfolio-solver -o $input.out.json --verbose $input.ext.json

flags="--disable-copy-dominance-constraints --disable-infinite-register-dominance-constraints --disable-operand-symmetry-breaking-constraints --disable-register-symmetry-breaking-constraints --disable-temporary-symmetry-breaking-constraints --disable-wcet-constraints"

gecode-diversify $flags --acceptable-gap 45 --relax 0.7 --seed 12 --number-divs 100 --restart constant --restart-scale 1000 --distance hamming --div-method monolithic_lns -o $input.out.json --use-optimal-for-diversification --solver-file $input.out.json  --branching clrandom --verbose $input.ext.json

exit 1

for i in *.${input}.out.json; 
do 
    uni export --keepnops --target=Mips $input.alt.uni -o $i.unison.mir --basefile=${input}.llvm.mir --solfile=$i; 
done

# /usr/local/bin/uni
#uni export --target=Mips $input.alt.uni -o $input.unison.mir --basefile=$input.llvm.mir --solfile=$input.out.json


#. /home/romi/opt/mcb32tools/environment

for i in *.${input}.out.json.unison.mir
do
    inoext="${i%.*}"   # filename without extension 
    inoext2="${inoext%.*}"   # filename without extension 
    inoext3="${inoext2%.*}"   # filename without extension 
    inoext4="${inoext3%.*}"   # filename without extension 
    llc $i -filetype=obj -march=mips -mcpu=mips32 -disable-post-ra -disable-tail-duplicate -disable-branch-fold -disable-block-placement -start-after livedebugvars -o $inoext4.o

    #mipsel-mcb32-elf-gcc -march=mips32r2 -msoft-float -Wa,-msoft-float -G 0 -ffreestanding -march=mips32r2 -msoft-float -Wa,-msoft-float -march=mips32r2 -msoft-float -msoft-float -c -MD -o $inoext4.s.o $inoext4.s
done
