#! /bin/bash -x

export PATH=${PATH}:${DIVCON_PATH}/src/solvers/gecode:${DIVCON_PATH}/src/solvers/multi_backend/minizinc/:${DIVCON_PATH}/src/solvers/multi_backend/:/home/romi/didaktoriko/misc/minizinc/MiniZincIDE-2.1.2-bundle-linux-x86_64/:${DIVCON_PATH}/src/solvers/multi_backend/common/ UNISON_DIR=${DIVCON_PATH} 

ddir=$DIVCONEXP_PATH/mirfiles/Mips/crypto
# Source directory
crypto_names=$DIVCONEXP_PATH/data/crypto_filenames.txt

files=`cut -d' ' -f 1 $crypto_names`
#funcs="br_aes_big_encrypt br_aes_ct_bitslice_encrypt"
funcs=`cut -d' ' -f 2 $crypto_names`

afiles=($files)
afuncs=($funcs)

count=${#afiles[@]}
for i in `seq 1 $count`
do

    input=$ddir/${afiles[$i-1]}
    func=${afuncs[$i-1]}

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
    #uni model --target=Mips $input.alt.uni -o $input.json --basefile=$input.llvm.mir +RTS -K20M -RTS
    uni model --target=Mips $input.alt.uni -o $input.json  #+RTS -K20M -RTS
    # /usr/local/bin/gecode-presolver
    gecode-presolver -t 1000000 -o $input.ext.json -dzn $input.dzn --verbose $input.json
    # /usr/local/bin/gecode-solver
    #gecode-solver  -o $input.out.json --verbose $input.ext.json

    #echo "/home/romi/didaktoriko/unison/romi_unison/unison/src/solvers/multi_backend/portfolio-solver -o $input.out.json --verbose $input.ext.json"
    #--global-budget 100
    ${DIVCON_PATH}/src/solvers/multi_backend/portfolio-solver -o $input.out.json --verbose $input.ext.json

    ## Sometimes chuffed does not sto running
    pkill fzn-chuffed
done
    #flags="--disable-copy-dominance-constraints --disable-infinite-register-dominance-constraints --disable-operand-symmetry-breaking-constraints --disable-register-symmetry-breaking-constraints --disable-temporary-symmetry-breaking-constraints --disable-wcet-constraints"


