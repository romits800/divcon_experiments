#! /bin/bash -x

# Destination Directory
ddir=$DIVCONEXP_PATH/mirfiles/Mips/crypto/bearSSL
# Source directory
sdir=$DIVCONEXP_PATH/crypto_libs/bearSSL/src/symcipher
#CLANGD=/home/romi/repo/llvm-project/build/bin/
opt=-O2
CFLAGS=" $opt -target mipsel -I $DIVCONEXP_PATH/crypto_libs/bearSSL/src/ -I $DIVCONEXP_PATH/crypto_libs/bearSSL/inc/"

# files=$sdir/aes_ct.c
#files="$sdir/aes_big_enc.c $sdir/aes_ct_enc.c"
#files="$sdir/aes_big_enc.c $sdir/aes_ct_enc.c"
crypto_names=$DIVCONEXP_PATH/data/crypto_filenames.txt

files=`cut -d' ' -f 1 $crypto_names`
#funcs="br_aes_big_encrypt br_aes_ct_bitslice_encrypt"
funcs=`cut -d' ' -f 2 $crypto_names`
afiles=($files)
afuncs=($funcs)

count=${#afiles[@]}
for i in `seq 1 $count`
do
    cfile=${afiles[$i-1]}
    cfunc=${afuncs[$i-1]}
    rm /tmp/unison-*
    fname1=${cfile##*/}
    fname=${fname1%.*}
    if [ -f $ddir/$fname.asm.mir ]
    then
        continue
    fi
    clang-3.8 $CFLAGS -S -emit-llvm $sdir/$cfile
    timeout 1m llc $fname.ll $opt -march=mips -mcpu=mips32 -unison -unison-no-clean -unison-only-functions="$cfunc"
    cp /tmp/unison-*.asm.mir $ddir/$fname.$cfunc.asm.mir
    cp /tmp/unison-*[!mn].mir $ddir/$fname.$cfunc.mir
done
#files=/home/romi/unison/divcon_experiments/example_function/fact.c


#clang-3.8 -I ./crypto_libs/libsodium-stable/src/libsodium/include/ -I ./crypto_libs/libsodium-stable/src/libsodium/include/sodium/ -target mipsel  -O2  -S -emit-llvm ./crypto_libs/libsodium-stable/src/libsodium/crypto_core/salsa/ref/core_salsa_ref.c 
#llc core_salsa_ref.ll -O2 -march=mips -unison -unison-no-clean
