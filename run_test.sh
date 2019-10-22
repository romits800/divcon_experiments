#! /bin/bash -x
input=$1

export PATH=${PATH}:/home/romi/didaktoriko/unison/romi_unison/divCon/src/solvers/gecode:/home/romi/didaktoriko/unison/romi_unison/divCon/src/solvers/multi_backend/minizinc/:/home/romi/didaktoriko/unison/romi_unison/divCon/src/solvers/multi_backend/:/home/romi/didaktoriko/misc/minizinc/MiniZincIDE-2.1.2-bundle-linux-x86_64/ UNISON_DIR=/home/romi/didaktoriko/unison/romi_unison/divCon/ #/home/romi/didaktoriko/unison/romi_unison/divCon/src/solvers/multi_backend/portfolio-solver -o test.out.json  --verbose test.ext.json
# /usr/local/bin/uni
echo "uni import --target=Mips $input.mir -o $input.uni --function=$input --maxblocksize=25 --goal=speed"
uni import --target=Mips $input.mir -o $input.uni --function=$input --maxblocksize=25 --goal=speed
# /usr/local/bin/uni
echo "uni linearize --target=Mips $input.uni -o $input.lssa.uni"
uni linearize --target=Mips $input.uni -o $input.lssa.uni
# /usr/local/bin/uni
echo "uni extend --target=Mips $input.lssa.uni -o $input.ext.uni"
uni extend --target=Mips $input.lssa.uni -o $input.ext.uni
# /usr/local/bin/uni
echo "uni augment --target=Mips $input.ext.uni -o $input.alt.uni"
uni augment --target=Mips $input.ext.uni -o $input.alt.uni
# /usr/local/bin/uni
echo "uni normalize --target=Mips $input.asm.mir -o $input.llvm.mir"
uni normalize --target=Mips $input.asm.mir -o $input.llvm.mir
# /usr/local/bin/uni
echo "uni model --target=Mips $input.alt.uni -o $input.json --basefile=$input.llvm.mir +RTS -K20M -RTS"
uni model --target=Mips $input.alt.uni -o $input.json --basefile=$input.llvm.mir +RTS -K20M -RTS
# /usr/local/bin/gecode-presolver
echo "gecode-presolver -o $input.ext.json -dzn $input.dzn --verbose $input.json"
gecode-presolver -o $input.ext.json -dzn $input.dzn --verbose $input.json
# /usr/local/bin/gecode-solver
echo "gecode-solver  -o $input.out.json --verbose $input.ext.json"
gecode-solver  -o $input.out.json --verbose $input.ext.json

#echo "/home/romi/didaktoriko/unison/romi_unison/unison/src/solvers/multi_backend/portfolio-solver -o $input.out.json --verbose $input.ext.json"
#/home/romi/didaktoriko/unison/romi_unison/unison/src/solvers/multi_backend/portfolio-solver -o $input.out.json --verbose $input.ext.json

flags="--disable-copy-dominance-constraints --disable-infinite-register-dominance-constraints --disable-operand-symmetry-breaking-constraints --disable-register-symmetry-breaking-constraints --disable-temporary-symmetry-breaking-constraints"

echo "gecode-diversify $flags --acceptable-gap $3 --relax 0.8 --seed 12 --number-divs 100 --restart constant --restart-base 1000 --distance $2 --div-method monolithic_lns -o $input.out.json --use-optimal-for-diversification --solver-file $input.out.json  --verbose $input.ext.json"
gecode-diversify $flags --acceptable-gap $3 --relax 0.8 --seed 12 --number-divs 100 --restart constant --restart-base 1000 --distance $2 --div-method monolithic_lns -o $input.out.json --use-optimal-for-diversification --solver-file $input.out.json  --verbose $input.ext.json


for i in *.${input}.out.json; 
do 
    uni export --keepnops --target=Mips $input.alt.uni -o $i.unison.mir --basefile=${input}.llvm.mir --solfile=$i; 
done

# /usr/local/bin/uni
#uni export --target=Mips $input.alt.uni -o $input.unison.mir --basefile=$input.llvm.mir --solfile=$input.out.json



