#! /bin/bash -x
bench=$1


export PATH=${PATH}:/home/romi/didaktoriko/unison/romi_unison/divCon/src/solvers/gecode:/home/romi/didaktoriko/unison/romi_unison/divCon/src/solvers/multi_backend/minizinc/:/home/romi/didaktoriko/unison/romi_unison/divCon/src/solvers/multi_backend/:/home/romi/didaktoriko/misc/minizinc/MiniZincIDE-2.1.2-bundle-linux-x86_64/ UNISON_DIR=/home/romi/didaktoriko/unison/romi_unison/divCon/ #/home/romi/didaktoriko/unison/romi_unison/divCon/src/solvers/multi_backend/portfolio-solver -o test.out.json  --verbose test.ext.json
# /usr/local/bin/uni


for pic in divs_0/${bench}/*.pickle
do
    echo $pic
    rm *.out.json
    rm *.out.json.unison.mir
    rm *.o
    python create_bin.py `pwd`/$pic

    for i in *.out.json; 
    do 
        uni export --keepnops --target=Mips ${bench}.alt.uni -o $i.unison.mir --basefile=${bench}.llvm.mir --solfile=$i; 
    done

# /usr/local/bin/uni
#uni export --target=Mips $input.alt.uni -o $input.unison.mir --basefile=$input.llvm.mir --solfile=$input.out.json


#. /home/romi/opt/mcb32tools/environment

    for i in *.out.json.unison.mir
    do
        inoext="${i%.*}"   # filename without extension 
        inoext2="${inoext%.*}"   # filename without extension 
        inoext3="${inoext2%.*}"   # filename without extension 
        inoext4="${inoext3%.*}"   # filename without extension 
        llc $i -filetype=obj -march=mipsel -mcpu=mips32 -disable-post-ra -disable-tail-duplicate -disable-branch-fold -disable-block-placement -start-after livedebugvars -o $inoext4.o
    done
    python jop_surv.py `pwd`
done