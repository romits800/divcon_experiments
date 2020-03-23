#! /bin/bash -x
bench=$1
path=$2


export PATH=${PATH}:/home/romi/didaktoriko/unison/romi_unison/divCon/src/solvers/gecode:/home/romi/didaktoriko/unison/romi_unison/divCon/src/solvers/multi_backend/minizinc/:/home/romi/didaktoriko/unison/romi_unison/divCon/src/solvers/multi_backend/:/home/romi/didaktoriko/misc/minizinc/MiniZincIDE-2.1.2-bundle-linux-x86_64/ UNISON_DIR=/home/romi/didaktoriko/unison/romi_unison/divCon/ #/home/romi/didaktoriko/unison/romi_unison/divCon/src/solvers/multi_backend/portfolio-solver -o test.out.json  --verbose test.ext.json
# /usr/local/bin/uni

pushd $path
cp ../create_bin.py .
cp ../jop_rc.py .

for pic in divs_?/${bench}/*.pickle
#for pic in ${path}/divs_?/${bench}/*.pickle 
do
    if [[ "$pic" == *_result.pickle ]]
    then
        continue
    fi  
    if [[ "$pic" == *maxdiv*.pickle ]]
    then
        continue
    fi
    if [[ "$pic" == *lnsdiv*.pickle ]]
    then
        continue
    fi

    echo $pic
    rm *.out.json
    rm *.out.json.unison.mir
    rm *.o
    python create_bin.py `pwd`/$pic

    for i in *.out.json; 
    do 
        #uni export --keepnops --target=Mips ${path}/${bench}.alt.uni -o $i.unison.mir --basefile=${path}/${bench}.llvm.mir --solfile=$i; 
        uni export --keepnops --target=Mips ${bench}.alt.uni -o $i.unison.mir --solfile=$i; 
    done


#. /home/romi/opt/mcb32tools/environment

    for i in *.out.json.unison.mir
    do
        inoext="${i%.*}"   # filename without extension 
        inoext2="${inoext%.*}"   # filename without extension 
        inoext3="${inoext2%.*}"   # filename without extension 
        inoext4="${inoext3%.*}"   # filename without extension 
        llc $i -filetype=obj -march=mipsel -mcpu=mips32 -disable-post-ra -disable-tail-duplicate -disable-branch-fold -disable-block-placement -start-after livedebugvars -o $inoext4.o
    done
    python jop_rc.py `pwd` $pic
done

popd 

