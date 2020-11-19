prog=$1
clang-3.8 -O2 -mllvm -debug-pass=Arguments -S -emit-llvm $1.c

rm /tmp/unison-*
timeout 1m llc $prog.ll -O3 -march=mips -mcpu=mips32 -unison -unison-no-clean
cp /tmp/unison-*.asm.mir $prog.asm.mir
cp /tmp/unison-*[!mn].mir $prog.mir
