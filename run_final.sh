#!/usr/bin/bash -x


flags="--disable-copy-dominance-constraints --disable-infinite-register-dominance-constraints --disable-operand-symmetry-breaking-constraints --disable-register-symmetry-breaking-constraints --disable-temporary-symmetry-breaking-constraints --disable-wcet-constraints"

#missing_files="/home/romi/didaktoriko/unison/romi_unison/divCon/src/unison/test/fast/Hexagon/speed/mesa.api.glIndexd.mir /home/romi/didaktoriko/unison/romi_unison/divCon/src/unison/test/fast/Hexagon/speed/sphinx3.glist.glist_tail.mir /home/romi/didaktoriko/unison/romi_unison/divCon/src/unison/test/fast/Hexagon/speed/sphinx3.profile.ptmr_init.mir"

#test_files="/home/romi/didaktoriko/unison/romi_unison/divCon/src/unison/test/fast/Mips/speed/gobmk.board.get_last_player.mir"
# In kbytes: 10Gbytes
ulimit -v 10485760

if [ $# -lt 4 ]
then
    echo "Required parameters not provided."
    echo "./run.sh <divs_path> <divs_dir> <run_path> <seed>"
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

seed=11
if [ $# -ge 4 ]
then
    seed=$4
fi



if [[ -z "${DIVCON_PATH}" ]]; then
  	echo "DIVCON_PATH variable not set. It should contain the PATH of the divCon repo."
	exit 0
fi


 
for arch in mips #hexagon #mips #arm
do
    Arch="$(tr '[:lower:]' '[:upper:]' <<< ${arch:0:1})${arch:1}"
    for i in ${CURRENT_DIR}/mirfiles/Mips/fast/*[!m].mir
    # for i in $DIVCON_PATH/src/unison/test/fast/${Arch}/speed/*[!m].mir
    # for i in /home/romi/didaktoriko/unison/unison-experiments/experiments/${arch}/selected-functions/size-toplas/*[!m].mir
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

        echo "LNS evaluation 1"
        # LNS evaluation
	for agap in 10 #2 5 10 20 50
	do
	    for ndivs in 200
	    do
	        for dist in "hamming" 
		do
 	            branch="cloriginal" 
                     if [ ! -f $fnoextension.out.json ]; then
                         echo "File not found! Falling back to llvm basefile"
                         time timeout 30m gecode-diversify ${flags} --acceptable-gap $agap --div-method max_div --seed $seed --distance ${dist} --number-divs $ndivs --divs-dir $DIVS_DIR  -o $fnoextension.out.json --branching ${branch} --verbose $fnoextension.ext.json
                     else
                         time timeout 30m gecode-diversify ${flags} --acceptable-gap $agap  --div-method max_div --seed $seed --distance ${dist} --number-divs $ndivs --solver-file $fnoextension.out.json --use-optimal-for-diversification --divs-dir $DIVS_DIR -o $fnoextension.out.json --branching ${branch} --verbose $fnoextension.ext.json
                     fi
                     python stats.py maxdiv_monolithic_dfs_${arch}_${fnoextension}_${agap}_${ndivs}_${dist}_${branch}_${seed}_1 ${fnoextension}  ${DIVS_DIR} ${RESULT_PATH} 
                     echo "Deleting the diversified files."
                     rm ${DIVS_DIR}/*.$fnoextension.out.json

                    branch="clrandom"
                    if [ ! -f $fnoextension.out.json ]; then
                        echo "File not found! Falling back to llvm basefile"
                        time timeout 30m gecode-diversify ${flags} --acceptable-gap $agap --div-method monolithic_dfs --seed $seed --distance ${dist} --number-divs $ndivs --divs-dir $DIVS_DIR  -o $fnoextension.out.json --branching ${branch} --verbose $fnoextension.ext.json
                    else
                        time timeout 30m gecode-diversify  ${flags} --acceptable-gap $agap  --div-method monolithic_dfs --seed $seed --distance ${dist} --number-divs $ndivs --solver-file $fnoextension.out.json --use-optimal-for-diversification --divs-dir $DIVS_DIR -o $fnoextension.out.json --branching ${branch} --verbose $fnoextension.ext.json
                    fi
                    python stats.py maxdiv_monolithic_dfs_${arch}_${fnoextension}_${agap}_${ndivs}_${dist}_${branch}_${seed}_1 ${fnoextension}  ${DIVS_DIR} ${RESULT_PATH} 
                    echo "Deleting the diversified files."
                    rm ${DIVS_DIR}/*.$fnoextension.out.json
                    #fi
                    for relax in 0.8
                    do
                        for lp in 5000 10000 #100000 
                        do
                            for rest in "constant"
                            do
                                if [ ! -f $fnoextension.out.json ]; then
                                    echo "File not found! Falling back to llvm basefile"
                                    time timeout 30m gecode-diversify  ${flags} --acceptable-gap $agap --relax $relax --seed $seed --distance ${dist} --restart $rest --restart-scale $lp --number-divs $ndivs --div-method monolithic_lns --divs-dir $DIVS_DIR -o $fnoextension.out.json --branching ${branch} --verbose $fnoextension.ext.json
                                else
                                    time timeout 30m gecode-diversify  ${flags} --acceptable-gap $agap --relax $relax --seed $seed --distance ${dist} --restart $rest --restart-scale $lp --number-divs $ndivs --solver-file $fnoextension.out.json --use-optimal-for-diversification --div-method monolithic_lns --divs-dir $DIVS_DIR -o $fnoextension.out.json --branching ${branch}  --verbose $fnoextension.ext.json
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



        echo "LNS evaluation 2"
        # LNS evaluation 2
	for agap in 10 #2 5 10 20 50
	do
	    for ndivs in 200
	    do
	        for dist in "hamming" 
		do
                    branch="clrandom"
                    if [ ! -f $fnoextension.out.json ]; then
                        echo "File not found! Falling back to llvm basefile"
                        time timeout 10m gecode-diversify ${flags} --acceptable-gap $agap --div-method monolithic_dfs --seed $seed --distance ${dist} --number-divs $ndivs --divs-dir $DIVS_DIR  -o $fnoextension.out.json --branching ${branch} --verbose $fnoextension.ext.json
                    else
                        time timeout 10m gecode-diversify  ${flags} --acceptable-gap $agap  --div-method monolithic_dfs --seed $seed --distance ${dist} --number-divs $ndivs --solver-file $fnoextension.out.json --use-optimal-for-diversification --divs-dir $DIVS_DIR -o $fnoextension.out.json --branching ${branch} --verbose $fnoextension.ext.json
                    fi
                    python stats.py lnsdiv_monolithic_dfs_${arch}_${fnoextension}_${agap}_${ndivs}_${dist}_${branch}_${seed}_1 ${fnoextension}  ${DIVS_DIR} ${RESULT_PATH} 
                    echo "Deleting the diversified files."
                    rm ${DIVS_DIR}/*.$fnoextension.out.json
                    #fi
                    for relax in 0.0 0.05 0.1 0.15 0.2 0.25 0.3 0.4 0.5 0.6 0.7 0.8 0.9
                    do
                        for lp in 10000 #100000 
                        do
                            for rest in "constant"
                            do
                                if [ ! -f $fnoextension.out.json ]; then
                                    echo "File not found! Falling back to llvm basefile"
                                    time timeout 10m gecode-diversify  ${flags} --acceptable-gap $agap --relax $relax --seed $seed --distance ${dist} --restart $rest --restart-scale $lp --number-divs $ndivs --div-method monolithic_lns --divs-dir $DIVS_DIR -o $fnoextension.out.json --branching ${branch} --verbose $fnoextension.ext.json
                                else
                                    time timeout 10m gecode-diversify  ${flags} --acceptable-gap $agap --relax $relax --seed $seed --distance ${dist} --restart $rest --restart-scale $lp --number-divs $ndivs --solver-file $fnoextension.out.json --use-optimal-for-diversification --div-method monolithic_lns --divs-dir $DIVS_DIR -o $fnoextension.out.json --branching ${branch}  --verbose $fnoextension.ext.json
                                fi
                                python stats.py lnsdiv_monolithic_lns_${arch}_${fnoextension}_${agap}_${ndivs}_${dist}_${branch}_${seed}_1_${relax}_${lp}_${rest} ${fnoextension} ${DIVS_DIR} ${RESULT_PATH} 
                                echo "Deleting the diversified files."
                                rm ${DIVS_DIR}/*.$fnoextension.out.json
                            done # rest
                        done #lp
                    done # relax
                done # dist
            done # ndivs
        done # agap




        echo "Agap evaluation"
        # Agap evaluation
	for agap in 0 2 5 10 20 #2 5 10 20 50
	do
	    for ndivs in 200
	    do
	        for dist in "hamming" #"reg_hamming" "hamming"
		do
                    branch="clrandom"
                    if [ ! -f $fnoextension.out.json ]; then
                        echo "File not found! Falling back to llvm basefile"
                        time timeout 10m gecode-diversify ${flags} --acceptable-gap $agap --div-method monolithic_dfs --seed $seed --distance ${dist} --number-divs $ndivs --divs-dir $DIVS_DIR  -o $fnoextension.out.json --branching ${branch} --verbose $fnoextension.ext.json
                    else
                        time timeout 10m gecode-diversify  ${flags} --acceptable-gap $agap  --div-method monolithic_dfs --seed $seed --distance ${dist} --number-divs $ndivs --solver-file $fnoextension.out.json --use-optimal-for-diversification --divs-dir $DIVS_DIR -o $fnoextension.out.json --branching ${branch} --verbose $fnoextension.ext.json
                    fi
                    python stats.py agapdiv_monolithic_dfs_${arch}_${fnoextension}_${agap}_${ndivs}_${dist}_${branch}_${seed}_1 ${fnoextension}  ${DIVS_DIR} ${RESULT_PATH} 
                    echo "Deleting the diversified files."
                    rm ${DIVS_DIR}/*.$fnoextension.out.json
                    #fi
                    for relax in 0.8
                    do
                        for lp in 10000 #100000 
                        do
                            for rest in "constant"
                            do
                                if [ ! -f $fnoextension.out.json ]; then
                                    echo "File not found! Falling back to llvm basefile"
                                    time timeout 10m gecode-diversify  ${flags} --acceptable-gap $agap --relax $relax --seed $seed --distance ${dist} --restart $rest --restart-scale $lp --number-divs $ndivs --div-method monolithic_lns --divs-dir $DIVS_DIR -o $fnoextension.out.json --branching ${branch} --verbose $fnoextension.ext.json
                                else
                                    time timeout 10m gecode-diversify  ${flags} --acceptable-gap $agap --relax $relax --seed $seed --distance ${dist} --restart $rest --restart-scale $lp --number-divs $ndivs --solver-file $fnoextension.out.json --use-optimal-for-diversification --div-method monolithic_lns --divs-dir $DIVS_DIR -o $fnoextension.out.json --branching ${branch}  --verbose $fnoextension.ext.json
                                fi
                                python stats.py agapdiv_monolithic_lns_${arch}_${fnoextension}_${agap}_${ndivs}_${dist}_${branch}_${seed}_1_${relax}_${lp}_${rest} ${fnoextension} ${DIVS_DIR} ${RESULT_PATH} 
                                echo "Deleting the diversified files."
                                rm ${DIVS_DIR}/*.$fnoextension.out.json
                            done # rest
                        done #lp
                    done # relax
                done # dist
            done # ndivs
        done # agap





        echo "Distance Evaluation"
        # Distance Evaluation
	for agap in 0 10 #2 5 10 20 50
	do
	    for ndivs in 200
	    do
	        for dist in "br_reg_hamming" "reg_hamming" "hamm_reg_gadget" "diff_br_hamming" "hamming" "br_hamming" "levenshtein" 
		do
                    branch="clrandom"
                    if [ ! -f $fnoextension.out.json ]; then
                        echo "File not found! Falling back to llvm basefile"
                        time timeout 10m gecode-diversify ${flags} --acceptable-gap $agap --div-method monolithic_dfs --seed $seed --distance ${dist} --number-divs $ndivs --divs-dir $DIVS_DIR  -o $fnoextension.out.json --branching ${branch} --verbose $fnoextension.ext.json
                    else
                        time timeout 10m gecode-diversify  ${flags} --acceptable-gap $agap  --div-method monolithic_dfs --seed $seed --distance ${dist} --number-divs $ndivs --solver-file $fnoextension.out.json --use-optimal-for-diversification --divs-dir $DIVS_DIR -o $fnoextension.out.json --branching ${branch} --verbose $fnoextension.ext.json
                    fi
                    python stats.py metrdiv_monolithic_dfs_${arch}_${fnoextension}_${agap}_${ndivs}_${dist}_${branch}_${seed}_1 ${fnoextension}  ${DIVS_DIR} ${RESULT_PATH} 
                    echo "Deleting the diversified files."
                    rm ${DIVS_DIR}/*.$fnoextension.out.json
                    #fi
                    for relax in 0.8
                    do
                        for lp in 10000 #100000 
                        do
                            for rest in "constant"
                            do
                                if [ ! -f $fnoextension.out.json ]; then
                                    echo "File not found! Falling back to llvm basefile"
                                    time timeout 10m gecode-diversify  ${flags} --acceptable-gap $agap --relax $relax --seed $seed --distance ${dist} --restart $rest --restart-scale $lp --number-divs $ndivs --div-method monolithic_lns --divs-dir $DIVS_DIR -o $fnoextension.out.json --branching ${branch} --verbose $fnoextension.ext.json
                                else
                                    time timeout 10m gecode-diversify  ${flags} --acceptable-gap $agap --relax $relax --seed $seed --distance ${dist} --restart $rest --restart-scale $lp --number-divs $ndivs --solver-file $fnoextension.out.json --use-optimal-for-diversification --div-method monolithic_lns --divs-dir $DIVS_DIR -o $fnoextension.out.json --branching ${branch}  --verbose $fnoextension.ext.json
                                fi
                                python stats.py metrdiv_monolithic_lns_${arch}_${fnoextension}_${agap}_${ndivs}_${dist}_${branch}_${seed}_1_${relax}_${lp}_${rest} ${fnoextension} ${DIVS_DIR} ${RESULT_PATH} 
                                echo "Deleting the diversified files."
                                rm ${DIVS_DIR}/*.$fnoextension.out.json
                            done # rest
                        done #lp
                    done # relax
                done # dist
            done # ndivs
        done # agap




        echo "k-dist Evaluation"
        # Distance Evaluation
	for agap in 10 #2 5 10 20 50
	do
	    for ndivs in 200
	    do
	        for dist in "reg_hamming" "hamm_reg_gadget" "hamming"
		do
	          for mdist in 1 2 5 10 20
                  do
                    branch="clrandom"
                    if [ ! -f $fnoextension.out.json ]; then
                        echo "File not found! Falling back to llvm basefile"
                        time timeout 10m gecode-diversify ${flags} --acceptable-gap $agap --div-method monolithic_dfs --seed $seed --distance ${dist} --number-divs $ndivs --divs-dir $DIVS_DIR  -o $fnoextension.out.json --min-dist $mdist --branching ${branch} --verbose $fnoextension.ext.json
                    else
                        time timeout 10m gecode-diversify  ${flags} --acceptable-gap $agap  --div-method monolithic_dfs --seed $seed --distance ${dist} --number-divs $ndivs --solver-file $fnoextension.out.json --use-optimal-for-diversification --divs-dir $DIVS_DIR -o $fnoextension.out.json --min-dist $mdist --branching ${branch} --verbose $fnoextension.ext.json
                    fi
                    python stats.py kdiv_monolithic_dfs_${arch}_${fnoextension}_${agap}_${ndivs}_${dist}_${branch}_${seed}_${mdist} ${fnoextension}  ${DIVS_DIR} ${RESULT_PATH} 
                    echo "Deleting the diversified files."
                    rm ${DIVS_DIR}/*.$fnoextension.out.json
                    #fi
                    for relax in 0.8
                    do
                        for lp in 10000 #100000 
                        do
                            for rest in "constant"
                            do
                                if [ ! -f $fnoextension.out.json ]; then
                                    echo "File not found! Falling back to llvm basefile"
                                    time timeout 10m gecode-diversify  ${flags} --acceptable-gap $agap --relax $relax --seed $seed --distance ${dist} --restart $rest --restart-scale $lp --number-divs $ndivs --div-method monolithic_lns --divs-dir $DIVS_DIR -o $fnoextension.out.json --min-dist $mdist --branching ${branch} --verbose $fnoextension.ext.json
                                else
                                    time timeout 10m gecode-diversify  ${flags} --acceptable-gap $agap --relax $relax --seed $seed --distance ${dist} --restart $rest --restart-scale $lp --number-divs $ndivs --solver-file $fnoextension.out.json --use-optimal-for-diversification --div-method monolithic_lns --divs-dir $DIVS_DIR -o $fnoextension.out.json --min-dist $mdist --branching ${branch}  --verbose $fnoextension.ext.json
                                fi
                                python stats.py kdiv_monolithic_lns_${arch}_${fnoextension}_${agap}_${ndivs}_${dist}_${branch}_${seed}_${mdist}_${relax}_${lp}_${rest} ${fnoextension} ${DIVS_DIR} ${RESULT_PATH} 
                                echo "Deleting the diversified files."
                                rm ${DIVS_DIR}/*.$fnoextension.out.json
                            done # rest
                        done #lp
                    done # relax
                  done # mdist
                done # dist
            done # ndivs
        done # agap








    done # files
done # arch



popd