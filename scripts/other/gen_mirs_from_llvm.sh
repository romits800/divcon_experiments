#! /bin/bash -x
#if [ $# -lt 2 ] 
#then
#   echo "missing argument"
#   exit 1
#fi
#=$1
dname=mirfiles/Mips/toplas/

opt=-O2

for llfile in /home/romi/didaktoriko/unison/unison-experiments/experiments/mips/selected-functions/size-toplas/*.ll
#for llfile in ../unison/src/unison/test/fast/Mips/speed/*.ll
    do
        rm /tmp/unison-*
        fname1=${llfile##*/}
        fname=${fname1%.*}
        if [ -f $dname/$fname.asm.mir ]
        then
            continue
        fi
        timeout 1m llc $llfile $opt -march=mips -mcpu=mips32 -unison -unison-no-clean
        cp /tmp/unison-*.asm.mir $dname/$fname.asm.mir
        cp /tmp/unison-*[!mn].mir $dname/$fname.mir
    done
