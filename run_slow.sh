#!/usr/bin/bash -x


export PATH=${PATH}:${DIVCON_PATH}/src/solvers/gecode:${DIVCON_PATH}/src/solvers/multi_backend/minizinc/:${DIVCON_PATH}/src/solvers/multi_backend/:${MINIZINC_PATH}:${DIVCON_PATH}/src/solvers/multi_backend/common/ UNISON_DIR=${DIVCON_PATH}

flags="--disable-copy-dominance-constraints --disable-infinite-register-dominance-constraints --disable-operand-symmetry-breaking-constraints --disable-register-symmetry-breaking-constraints --disable-temporary-symmetry-breaking-constraints --disable-wcet-constraints"

#missing_files="/home/romi/didaktoriko/unison/romi_unison/divCon/src/unison/test/fast/Hexagon/speed/mesa.api.glIndexd.mir /home/romi/didaktoriko/unison/romi_unison/divCon/src/unison/test/fast/Hexagon/speed/sphinx3.glist.glist_tail.mir /home/romi/didaktoriko/unison/romi_unison/divCon/src/unison/test/fast/Hexagon/speed/sphinx3.profile.ptmr_init.mir"

#test_files="/home/romi/didaktoriko/unison/romi_unison/divCon/src/unison/test/fast/Mips/speed/gobmk.board.get_last_player.mir"
# In kbytes: 10Gbytes
#ulimit -v 10485760

if [ $# -lt 4 ]
then
    echo "Required parameters not provided."
    echo "./run.sh <divs_path> <divs_dir> <run_path> <seed>"
    exit 1
fi

CURRENT_DIR=`pwd`

RUN_DIR=.
if [ $# -ge 3 ]
then
    RUN_DIR=$3
fi
if [ ! -d $RUN_DIR ]
then
    mkdir $RUN_DIR
fi

cp scripts/stats.py $RUN_DIR

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

seed=11
if [ $# -ge 4 ]
then
    seed=$4
fi



if [[ -z "${DIVCON_PATH}" ]]; then
  	echo "DIVCON_PATH variable not set. It should contain the PATH of the divCon repo."
	exit 0
fi

if [ -d ${CURRENT_DIR}/solution_files/toplas/ ]
then
    cp ${CURRENT_DIR}/solution_files/toplas/* .
fi
 
for arch in mips #hexagon #mips #arm
do
    Arch="$(tr '[:lower:]' '[:upper:]' <<< ${arch:0:1})${arch:1}"
    for i in ${CURRENT_DIR}/mirfiles/Mips/toplas/*.mir
    # for i in $DIVCON_PATH/src/unison/test/fast/${Arch}/speed/*[!m].mir
    # for i in /home/romi/didaktoriko/unison/unison-experiments/experiments/${arch}/selected-functions/size-toplas/*[!m].mir
    do
        if [[ "$i" == *.asm.mir ]]
        then 
            continue
        fi

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
# 	uni import --target=$archc $fullname -o $fnoextension.uni --function=$func --maxblocksize=50 --goal=speed
# 	# /usr/local/bin/uni
# 	uni linearize --target=$archc $fnoextension.uni -o $fnoextension.lssa.uni
# 	# /usr/local/bin/uni
# 	uni extend --target=$archc $fnoextension.lssa.uni -o $fnoextension.ext.uni
# 	# /usr/local/bin/uni
# 	uni augment --target=$archc $fnoextension.ext.uni -o $fnoextension.alt.uni
# 	# /usr/local/bin/uni
 	# uni normalize --target=$archc $fullnamenoext.asm.mir -o $fnoextension.llvm.mir
# 	# /usr/local/bin/uni
# t
# 	uni model --target=$archc $fnoextension.alt.uni -o $fnoextension.json 
# 	#uni model --target=$archc $fnoextension.alt.uni -o $fnoextension.json --basefile=$fnoextension.llvm.mir +RTS -K20M -RTS
# 	# /usr/local/bin/gecode-presolver
# 	gecode-presolver -o $fnoextension.ext.json -dzn $fnoextension.dzn --verbose $fnoextension.json
# 	# /usr/local/bin/gecode-solver
# 	if [ ! -f $fnoextension.out.json ]; then
#             rm $fnoextension.out.json
#         fi
        #gecode-solver  -o $fnoextension.out.json --verbose $fnoextension.ext.json
        #${DIVCON_PATH}/src/solvers/multi_backend/portfolio-solver -o $fnoextension.out.json --verbose $fnoextension.ext.json
        #pkill fzn-chuffed
        #if grep has $fnoextension.out.json | grep false
        #then
#            gecode-solver  -o $fnoextension.out.json --verbose $fnoextension.ext.json
        #fi

# 
# 	
#         RESULT_PATH=${DIVS_PATH}/${fnoextension}
# 
# 	mkdir $RESULT_PATH
# 
#         echo "LNS evaluation 1"
#         # LNS evaluation
 	for agap in 10 #2 5 10 20 50
 	do
 	    for ndivs in 200
 	    do
 	        for dist in "hamming" 
 		do
                     branch="clrandom"
# #                     if [ ! -f $fnoextension.out.json ]; then
# #                         echo "File not found! Falling back to llvm basefile"
# #                         time timeout 5m gecode-diversify ${flags} --acceptable-gap $agap --div-method monolithic_dfs --seed $seed --distance ${dist} --number-divs $ndivs --divs-dir $DIVS_DIR  -o $fnoextension.out.json --branching ${branch} --verbose $fnoextension.ext.json
# #                     else
# #                         time timeout 5m gecode-diversify  ${flags} --acceptable-gap $agap  --div-method monolithic_dfs --seed $seed --distance ${dist} --number-divs $ndivs --solver-file $fnoextension.out.json --use-optimal-for-diversification --divs-dir $DIVS_DIR -o $fnoextension.out.json --enable-solver-solution-brancher --branching ${branch} --verbose $fnoextension.ext.json
# #                     fi
# #                     python stats.py maxdiv_monolithic_dfs_${arch}_${fnoextension}_${agap}_${ndivs}_${dist}_${branch}_${seed}_1 ${fnoextension}  ${DIVS_DIR} ${RESULT_PATH} 
# #                     echo "Deleting the diversified files."
# #                     rm ${DIVS_DIR}/*.$fnoextension.out.json
#                     #fi
                     for relax in 0.7
                     do
                         for lp in 500 #10000 #100000 
                         do
                             for rest in "constant"
                             do
                                 if [ ! -f $fnoextension.out.json ]; then
                                     echo "File not found! Falling back to llvm basefile"
                                     time timeout 5m gecode-diversify  ${flags} --acceptable-gap $agap --relax $relax --seed $seed --distance ${dist} --restart $rest --restart-scale $lp --number-divs $ndivs --div-method monolithic_lns --divs-dir $DIVS_DIR -o $fnoextension.out.json --branching ${branch} --verbose $fnoextension.ext.json
                                 else
                                     time timeout 5m gecode-diversify  ${flags} --acceptable-gap $agap --relax $relax --seed $seed --distance ${dist} --restart $rest --restart-scale $lp --number-divs $ndivs --solver-file $fnoextension.out.json --use-optimal-for-diversification --div-method monolithic_lns --divs-dir $DIVS_DIR -o $fnoextension.out.json --enable-solver-solution-brancher --branching ${branch}  --verbose $fnoextension.ext.json
                                 fi
                                 python stats.py maxdiv_monolithic_lns_${arch}_${fnoextension}_${agap}_${ndivs}_${dist}_${branch}_${seed}_1_${relax}_${lp}_${rest} ${fnoextension} ${DIVS_DIR} ${RESULT_PATH} 
                                 echo "Deleting the diversified files."
                                 rm ${DIVS_DIR}/*.$fnoextension.out.json
                             done # rest
                         done #lp
                     done # relax
                 done # dist
             done # ndivs
         done # agap



    done # files
done # arch



popd
