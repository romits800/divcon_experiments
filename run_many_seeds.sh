#!/usr/bin/bash -x

proc=$1
seeds=$2


IFS=','; seedsarr=($seeds); unset IFS;
for i in {0..3} #s in $seedsarr;
do
    s=${seedsarr[$i]}
    time taskset `printf '0x%x\n' $proc` nohup ./run_final.sh divs_${i} divs_dir_${i} divs_${s}_${i} $s &> out_lns_${s}_${i}
done
