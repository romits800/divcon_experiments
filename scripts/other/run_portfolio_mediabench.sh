#! /bin/bash -x


if [ $# -lt 1 ] 
then
   echo "missing argument"
   echo "gen_mirs_from_llvm less_100|more_100"
   exit 1
fi
select=$1


export PATH=${PATH}:${DIVCON_PATH}/src/solvers/gecode:${DIVCON_PATH}/src/solvers/multi_backend/minizinc/:${DIVCON_PATH}/src/solvers/multi_backend/:/home/romi/didaktoriko/misc/minizinc/MiniZincIDE-2.1.2-bundle-linux-x86_64/:${DIVCON_PATH}/src/solvers/multi_backend/common/ UNISON_DIR=${DIVCON_PATH} 

ddir=$DIVCONEXP_PATH/mirfiles/Mips/mediabench/${select}
if [ ! -d $ddir ]; then
    echo "No folder:" $ddir
    exit
fi

sfolder=$DIVCONEXP_PATH/solution_files/mediabench/${select}

if [ ! -d $sfolder ]; then
    mkdir -p $sfolder
fi

#files=`cut -d' ' -f 1 $crypto_names`
#funcs=`cut -d' ' -f 2 $crypto_names`

for i in $ddir/jpeg.jc*[!m].mir
do
    input=$i 		# filepath: file with path and extension
    fullnamenoext="${input%.*}" # filepath: file with path and extension
    filename="${input##*/}" # filename: file without the path but with extension
    fnoextension="${filename%.*}"   # filename without extension 
    func="${fnoextension##*.}"	# function name
    sfile=$sfolder/$fnoextension


    # /usr/local/bin/uni
    uni import --target=Mips $input -o $sfile.uni --function=$func --maxblocksize=25 --goal=speed
    # /usr/local/bin/uni
    uni linearize --target=Mips $sfile.uni -o $sfile.lssa.uni
    # /usr/local/bin/uni
    uni extend --target=Mips $sfile.lssa.uni -o $sfile.ext.uni
    # /usr/local/bin/uni
    uni augment --target=Mips $sfile.ext.uni -o $sfile.alt.uni
    # /usr/local/bin/uni
    #uni normalize --target=Mips $sfile.asm.mir -o $sfile.llvm.mir
    # /usr/local/bin/uni
    #uni model --target=Mips $input.alt.uni -o $input.json --basefile=$input.llvm.mir +RTS -K20M -RTS
    uni model --target=Mips $sfile.alt.uni -o $sfile.json  #+RTS -K20M -RTS
    # /usr/local/bin/gecode-presolver
    gecode-presolver -t 1000000 -o $sfile.ext.json -dzn $sfile.dzn --verbose $sfile.json
    # /usr/local/bin/gecode-solver
    #gecode-solver  -o $input.out.json --verbose $input.ext.json

    #echo "/home/romi/didaktoriko/unison/romi_unison/unison/src/solvers/multi_backend/portfolio-solver -o $input.out.json --verbose $input.ext.json"
    #gecode: --global-budget 100
    ${DIVCON_PATH}/src/solvers/multi_backend/portfolio-solver -o $sfile.out.json --verbose $sfile.ext.json

    ## Sometimes chuffed does not sto running
    pkill fzn-chuffed
done
    #flags="--disable-copy-dominance-constraints --disable-infinite-register-dominance-constraints --disable-operand-symmetry-breaking-constraints --disable-register-symmetry-breaking-constraints --disable-temporary-symmetry-breaking-constraints --disable-wcet-constraints"


