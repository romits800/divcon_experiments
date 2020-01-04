#! /bin/bash -x
#if [ $# -lt 2 ] 
#then
#   echo "missing argument"
#   exit 1
#fi
#=$1
dname=mirfiles/Mips

opt=-O2

for llfile in ../unison/src/unison/test/fast/Mips/speed/*.ll
    do
        rm /tmp/unison-*
        fname1=${llfile##*/}
        fname=${fname1%.*}
        llc $llfile $opt -march=mips -mcpu=mips32 -unison -unison-no-clean
        cp /tmp/unison-*.asm.mir $dname/$fname.asm.mir
        cp /tmp/unison-*[!mn].mir $dname/$fname.mir
    done
