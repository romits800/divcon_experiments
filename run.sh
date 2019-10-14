#!/bin/bash -x


flags="--disable-copy-dominance-constraints --disable-infinite-register-dominance-constraints --disable-operand-symmetry-breaking-constraints --disable-register-symmetry-breaking-constraints --disable-temporary-symmetry-breaking-constraints"
#TODO: update with --disable-wcet-constraints
# flags="--disable-wcet-constraints --disable-copy-dominance-constraints --disable-infinite-register-dominance-constraints --disable-operand-symmetry-breaking-constraints --disable-register-symmetry-breaking-constraints --disable-temporary-symmetry-breaking-constraints"


for arch in  mips hexagon #mips #arm
do
    Arch="$(tr '[:lower:]' '[:upper:]' <<< ${arch:0:1})${arch:1}"
    # for i in /home/romi/didaktoriko/unison/unison-experiments/experiments/mips/selected-functions/size-toplas/gcc.attribs.handle_noinline_attribute.mir
    for i in /home/romi/didaktoriko/unison/romi_unison/divCon/src/unison/test/fast/${Arch}/speed/*[!m].mir
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
	gecode-solver  -o $fnoextension.out.json --verbose $fnoextension.ext.json
	#gecode-solver  -o $fnoextension.out.json --verbose $fnoextension.ext.json
	
	for agap in 10 20 #2 5 10 20 50
	do
	    for ndivs in 100
	    do
	        for dist in "diff_br_hamming" #"hamming" "br_hamming"
		do
		    if [ ! -f $fnoextension.out.json ]; then
                        echo "File not found! Falling back to llvm basefile"
		        time timeout 5m gecode-diversify --timeout 600000 ${flags} --acceptable-gap $agap --div-method monolithic_dfs --distance ${dist} --number-divs $ndivs  -o $fnoextension.out.json --verbose $fnoextension.ext.json
		    else
		        time timeout 5m gecode-diversify --timeout 600000 ${flags} --acceptable-gap $agap  --div-method monolithic_dfs --distance ${dist} --number-divs $ndivs --solver-file $fnoextension.out.json --use-optimal-for-diversification -o $fnoextension.out.json --verbose $fnoextension.ext.json
		    fi
		    python stats.py div_monolithic_dfs_${arch}_${fnoextension}_${agap}_${ndivs}_${dist} ${fnoextension} >> div_monolithic_dfs_${arch}_${fnoextension}_${agap}_${ndivs}_${dist}.txt
		    echo "Deleting the diversified files."
		    rm *.$fnoextension.out.json
		    #fi
		done
	    done #ndivs
	done # agap

	for agap in 10 20 #2 5 10 20 50
        do
	    for relax in 0.8 0.4
	    do
                for lp in 1000 10000 100000 
		do
		    for ndivs in 100 #100000 
		    do
                        for dist in "diff_br_hamming" #"hamming" "br_hamming" 
                        do
                            for rest in "constant"
                            do
                                if [ ! -f $fnoextension.out.json ]; then
                                    echo "File not found! Falling back to llvm basefile"
                                    time timeout 5m gecode-diversify --timeout 600000 ${flags} --acceptable-gap $agap --relax $relax --seed 12 --distance ${dist} --restart $rest --restart-base $lp --number-divs $ndivs --div-method monolithic_lns -o $fnoextension.out.json --verbose $fnoextension.ext.json
                                else
                                    time timeout 5m gecode-diversify --timeout 600000 ${flags} --acceptable-gap $agap --relax $relax --seed 12 --distance ${dist} --restart $rest --restart-base $lp --number-divs $ndivs --solver-file $fnoextension.out.json --use-optimal-for-diversification --div-method monolithic_lns -o $fnoextension.out.json --verbose $fnoextension.ext.json
                                fi
                                python stats.py div_monolithic_lns_${arch}_${fnoextension}_${agap}_${ndivs}_${dist}_${relax}_${lp}_${rest} ${fnoextension} >> div_monolithic_lns_${arch}_${fnoextension}_${agap}_${ndivs}_${dist}_${relax}_${lp}_${rest}.txt
                                echo "Deleting the diversified files."
                                rm *.$fnoextension.out.json
						#fi
                            done
                        done
                    done #ndivs
                done #lp aka luby param
            done #relax
	done #agap

	mkdir divs/${fnoextension}
	cp out divs/${fnoextension}/

	mv div_*${fnoextension}* divs/${fnoextension}/
    done # files
done # arch



