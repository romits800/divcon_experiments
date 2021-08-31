#! /bin/bash -x
echo $#
if [ $# -lt 1 ] 
then
   echo "missing argument"
   echo "gen_mirs_from_llvm less_100|more_100"
   exit 1
fi
select=$1

dname=mirfiles/Mips/mediabench/${select}

if [ ! -d $dname ]; then
    mkdir -p $dname
fi

llfiles=(`cut -f 1 -d "|" data/bench_${select}.txt`)
funcs=(`cut -f 2 -d "|" data/bench_${select}.txt`)
opt=-O2


for ((i=0;i<=${#llfiles[@]};i++))
#for llfile in ../unison/src/unison/test/fast/Mips/speed/*.ll
    do
        func=${funcs[i]}
        llfile=${llfiles[i]}
        rm /tmp/unison-*
        fname1=${llfile##*/}
        fname=${fname1%.*}
        fname=${fname}.${func}

        echo $fname
        if [ -f $dname/$fname.asm.mir ]
        then
            continue
        fi
        timeout 1m llc $llfile $opt -march=mips -mcpu=mips32 -unison -unison-no-clean -unison-only-functions $func
        cp /tmp/unison-*.asm.mir $dname/$fname.asm.mir
        cp /tmp/unison-*[!mn].mir $dname/$fname.mir
    done
