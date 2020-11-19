#! /bin/bash -x

# Destination Directory
ddir=$DIVCONEXP_PATH/mirfiles/Mips/crypto
# Source directory
sdir=$DIVCONEXP_PATH/crypto_libs/bearSSL/src/symcipher
#CLANGD=/home/romi/repo/llvm-project/build/bin/
CFLAGS=" -target mipsel -I $DIVCONEXP_PATH/crypto_libs/bearSSL/src/ -I $DIVCONEXP_PATH/crypto_libs/bearSSL/inc/"

files=$sdir/aes_ct.c
#files=/home/romi/unison/divcon_experiments/example_function/fact.c

opt=-O2

for cfile in $files
#for llfile in ../unison/src/unison/test/fast/Mips/speed/*.ll
    do
        clang-3.8 $CFLAGS -O2 -mllvm -debug-pass=Arguments -S -emit-llvm $cfile
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
clang-3.8 -I ./crypto_libs/libsodium-stable/src/libsodium/include/ -I ./crypto_libs/libsodium-stable/src/libsodium/include/sodium/ -target mipsel  -O2  -S -emit-llvm ./crypto_libs/libsodium-stable/src/libsodium/crypto_core/salsa/ref/core_salsa_ref.c 
llc core_salsa_ref.ll -O2 -march=mips -unison -unison-no-clean
