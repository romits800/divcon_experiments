#!/usr/bin/bash -x

for i in {0..1}
do
    echo $i
    hex="0x1"
    cpu=$((hex << i))
    taskset `printf '0x%x\n' $cpu` nohup ./run_max_diversity_brham.sh divs_${i} divs_dir_${i} divs_br_${i} &> out_br_${i} &
done
for i in {0..1}
do
    echo $i
    hex="0x4"
    cpu=$((hex << i))
    taskset `printf '0x%x\n' $cpu` nohup ./run_max_diversity_lev.sh divs_${i} divs_dir_${i} divs_lev_${i} &> out_lev_${i} &
done
for i in {0..1}
do
    echo $i
    hex="0x10"
    cpu=$((hex << i))
    taskset `printf '0x%x\n' $cpu` nohup ./run_max_diversity_ham.sh divs_${i} divs_dir_${i} divs_ham_ham_${i} &> out_${i} &
done
for i in {0..1}
do
    echo $i
    hex="0x40"
    cpu=$((hex << i))
    taskset `printf '0x%x\n' $cpu` nohup ./run_max_diversity_dham.sh divs_${i} divs_dir_${i} divs_ham_diff_${i} &> out_${i} &
done

