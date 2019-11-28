#!/usr/bin/bash -x


flags="--disable-relax-y --disable-relax-y --disable-relax-r --disable-copy-dominance-constraints --disable-infinite-register-dominance-constraints --disable-operand-symmetry-breaking-constraints --disable-register-symmetry-breaking-constraints --disable-temporary-symmetry-breaking-constraints --disable-wcet-constraints"

# In kbytes: 10Gbytes
ulimit -v 10485760

RUN_DIR=.
if [ $# -ge 3 ]
then
    RUN_DIR=$3
fi
if [ ! -d $RUN_DIR ]
then
    mkdir $RUN_DIR
fi

cp stats.py $RUN_DIR

pushd $RUN_DIR


DIVS_PATH=divs
if [ $# -ge 1 ]
then
    DIVS_PATH=$1
fi

if [ ! -d $DIVS_PATH ]
then
    mkdir $DIVS_PATH
fi

DIVS_DIR=divs_dir
if [ $# -ge 2 ]
then
    DIVS_DIR=$2
fi





if [[ -z "${DIVCON_PATH}" ]]; then
  	echo "DIVCON_PATH variable not set. It should contain the PATH of the divCon repo."
	exit 0
fi


 
for arch in mips #hexagon #mips #arm
do
    Arch="$(tr '[:lower:]' '[:upper:]' <<< ${arch:0:1})${arch:1}"
    for i in $DIVCON_PATH/src/unison/test/fast/${Arch}/speed/*[!m].mir
    #for i in /home/romi/didaktoriko/unison/unison-experiments/experiments/${arch}/selected-functions/size-toplas/*[!m].mir
	
    do
	fullname=$i 		# filepath: file with path and extension
	fullnamenoext="${fullname%.*}" 		# filepath: file with path and extension
	filename="${fullname##*/}" # filename: file without the path but with extension
	fnoextension="${filename%.*}"   # filename without extension 
	func="${fnoextension##*.}"	# function name
        if [ "$func" == "cond-transfer" ]
        then
            func="reconstruct"
        fi
	archc="${arch^}"
	
	# /usr/local/bin/uni
	uni import --target=$archc $fullname -o $fnoextension.uni --function=$func --maxblocksize=50 --goal=speed
	# /usr/local/bin/uni
	uni linearize --target=$archc $fnoextension.uni -o $fnoextension.lssa.uni
	# /usr/local/bin/uni
	uni extend --target=$archc $fnoextension.lssa.uni -o $fnoextension.ext.uni
	# /usr/local/bin/uni
	uni augment --target=$archc $fnoextension.ext.uni -o $fnoextension.alt.uni
	# /usr/local/bin/uni
	uni normalize --target=$archc $fullnamenoext.asm.mir -o $fnoextension.llvm.mir
	# /usr/local/bin/uni
	uni model --target=$archc $fnoextension.alt.uni -o $fnoextension.json --basefile=$fnoextension.llvm.mir +RTS -K20M -RTS
	# /usr/local/bin/gecode-presolver
	gecode-presolver -o $fnoextension.ext.json --verbose $fnoextension.json
	# /usr/local/bin/gecode-solver
	if [ ! -f $fnoextension.out.json ]; then
            rm $fnoextension.out.json
        fi
	gecode-solver  -o $fnoextension.out.json --verbose $fnoextension.ext.json
	
        RESULT_PATH=${DIVS_PATH}/${fnoextension}

	mkdir $RESULT_PATH

	for agap in 10 #20 #2 5 10 20 50
	do
	    for ndivs in 100
	    do
	        for dist in "diff_br_hamming" "hamming" "br_hamming" "levenshtein"
		do
	            for branch in  "clrandom" "cloriginal" # "original"
                    do
                       for relax in 0.4 0.6 0.8 0.9 
                        do
                            for lp in 10000 #100000 
                            do
                                for rest in "constant"
                                do
                                    if [ ! -f $fnoextension.out.json ]; then
                                        echo "File not found! Falling back to llvm basefile"
                                        time timeout 5m gecode-diversify  ${flags} --acceptable-gap $agap --relax $relax --seed 12 --distance ${dist} --restart $rest --restart-base $lp --number-divs $ndivs --div-method monolithic_lns --divs-dir $DIVS_DIR -o $fnoextension.out.json --branching ${branch} --verbose $fnoextension.ext.json
                                    else
                                        time timeout 5m gecode-diversify  ${flags} --acceptable-gap $agap --relax $relax --seed 12 --distance ${dist} --restart $rest --restart-base $lp --number-divs $ndivs --solver-file $fnoextension.out.json --use-optimal-for-diversification --div-method monolithic_lns --divs-dir $DIVS_DIR -o $fnoextension.out.json --branching ${branch}  --verbose $fnoextension.ext.json
                                    fi
                                    python stats.py div_monolithic_lns_${arch}_${fnoextension}_${agap}_${ndivs}_${dist}_${branch}_${relax}_${lp}_${rest} ${fnoextension} ${DIVS_DIR} ${RESULT_PATH} 
                                    echo "Deleting the diversified files."
                                    rm ${DIVS_DIR}/*.$fnoextension.out.json
                                done # rest
                            done #lp
                        done # relax
                    done # branch
                done # dist
            done # ndivs
        done # agap
    done # files
done # arch



popd