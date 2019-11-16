#!/usr/bin/bash -x

for i in {0..1}
do
    echo $i
    hex="0x1"
    cpu=$((hex << i))
    taskset `printf '0x%x\n' $cpu` nohup ./run_br.sh divs_${i} divs_dir_${i} divs_br_${i} &> out_br_${i} &
done
for i in {0..1}
do
    echo $i
    hex="0x4"
    cpu=$((hex << i))
    taskset `printf '0x%x\n' $cpu` nohup ./run_lev.sh divs_${i} divs_dir_${i} divs_lev_${i} &> out_lev_${i} &
done
for i in {0..1}
do
    echo $i
    hex="0x10"
    cpu=$((hex << i))
    taskset `printf '0x%x\n' $cpu` nohup ./run.sh divs_${i} divs_dir_${i} divs_ham_diffham_${i} &> out_${i} &
done

