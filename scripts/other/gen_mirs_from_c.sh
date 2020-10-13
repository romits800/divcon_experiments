#! /bin/bash -x

# Destination Directory
ddir=$DIVCONEXP_PATH/mirfiles/Mips/crypto
# Source directory
sdir=$DIVCONEXP_PATH/crypto_libs/BearSSL/src/symcipher
CLANGD=/home/romi/repo/llvm-project/build/bin/
CFLAGS="-I /home/romi/unison/divcon_experiments/crypto_libs/BearSSL/src/ -I /home/romi/unison/divcon_experiments/crypto_libs/BearSSL/inc/"

files=$sdir/aes_ct.c
files=/home/romi/unison/divcon_experiments/example_function/fact.c

opt=-O2

for cfile in $files
#for llfile in ../unison/src/unison/test/fast/Mips/speed/*.ll
    do
        $CLANGD/clang $CFLAGS -O2 -mllvm -debug-pass=Arguments -S -emit-llvm $cfile
        rm /tmp/unison-*
        fname1=${cfile##*/}
        fname=${fname1%.*}
        if [ -f $ddir/$fname.asm.mir ]
        then
            continue
        fi
        timeout 1m llc $fname.ll $opt -march=mips -mcpu=mips32 -unison -unison-no-clean
        cp /tmp/unison-*.asm.mir $ddir/$fname.asm.mir
        cp /tmp/unison-*[!mn].mir $ddir/$fname.mir
    done
