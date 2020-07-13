#!/usr/bin/bash -x


export PATH=${PATH}:${DIVCON_PATH}/src/solvers/gecode:${DIVCON_PATH}/src/solvers/multi_backend/minizinc/:${DIVCON_PATH}/src/solvers/multi_backend/:${MINIZINC_PATH}:${DIVCON_PATH}/src/solvers/multi_backend/common/ UNISON_DIR=${DIVCON_PATH}

flags="--disable-copy-dominance-constraints --disable-infinite-register-dominance-constraints --disable-operand-symmetry-breaking-constraints --disable-register-symmetry-breaking-constraints --disable-temporary-symmetry-breaking-constraints --disable-wcet-constraints"

#missing_files="/home/romi/didaktoriko/unison/romi_unison/divCon/src/unison/test/fast/Hexagon/speed/mesa.api.glIndexd.mir /home/romi/didaktoriko/unison/romi_unison/divCon/src/unison/test/fast/Hexagon/speed/sphinx3.glist.glist_tail.mir /home/romi/didaktoriko/unison/romi_unison/divCon/src/unison/test/fast/Hexagon/speed/sphinx3.profile.ptmr_init.mir"

#test_files="/home/romi/didaktoriko/unison/romi_unison/divCon/src/unison/test/fast/Mips/speed/gobmk.board.get_last_player.mir"
# In kbytes: 10Gbytes
ulimit -v 10485760


cp ../scripts/stats.py .

arch=mips
Arch="$(tr '[:lower:]' '[:upper:]' <<< ${arch:0:1})${arch:1}"
fullname=factorial.mir
fullnamenoext="${fullname%.*}" 		# filepath: file with path and extension
filename="${fullname##*/}" # filename: file without the path but with extension
fnoextension="${filename%.*}"   # filename without extension 
func="${fnoextension##*.}"	# function name
archc="${arch^}"
	
	# /usr/local/bin/uni
uni import --target=$archc $fullname -o $fnoextension.uni --function=$func --maxblocksize=50 --goal=size
uni linearize --target=$archc $fnoextension.uni -o $fnoextension.lssa.uni
uni extend --target=$archc $fnoextension.lssa.uni -o $fnoextension.ext.uni
uni augment --target=$archc $fnoextension.ext.uni -o $fnoextension.alt.uni
uni model --target=$archc $fnoextension.alt.uni -o $fnoextension.json 
gecode-presolver -o $fnoextension.ext.json -dzn $fnoextension.dzn --verbose $fnoextension.json
${DIVCON_PATH}/src/solvers/multi_backend/portfolio-solver -o $fnoextension.out.json --verbose $fnoextension.ext.json


branch="clrandom"
relax=0.7
lp=500
rest="constant"
seed=111
agap=10
ndivs=100
dist=hamming

time timeout 10m gecode-diversify  ${flags} --acceptable-gap $agap --relax $relax --seed $seed --distance ${dist} --restart $rest --restart-scale $lp --number-divs $ndivs --solver-file $fnoextension.out.json --use-optimal-for-diversification --div-method monolithic_lns -o $fnoextension.out.json --enable-solver-solution-brancher --branching ${branch}  --verbose $fnoextension.ext.json
python stats.py maxdiv_monolithic_lns_${arch}_${fnoextension}_${agap}_${ndivs}_${dist}_${branch}_${seed}_1_${relax}_${lp}_${rest} ${fnoextension} . .


for i in *.out.json; 
do 
    #uni export --keepnops --target=Mips ${path}/${bench}.alt.uni -o $i.unison.mir --basefile=${path}/${bench}.llvm.mir --solfile=$i; 
    uni export --keepnops --target=Mips ${fnoextension}.alt.uni -o $i.unison.mir --solfile=$i; 
done


for i in *.out.json.unison.mir
do
    inoext="${i%.*}"   # filename without extension 
    inoext2="${inoext%.*}"   # filename without extension 
    inoext3="${inoext2%.*}"   # filename without extension 
    inoext4="${inoext3%.*}"   # filename without extension 
    llc $i  -filetype=obj -march=mipsel -mcpu=mips32 -disable-post-ra -disable-tail-duplicate -disable-branch-fold -disable-block-placement -start-after livedebugvars -o $inoext4.o
done
 
