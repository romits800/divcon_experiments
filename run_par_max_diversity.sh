#!/usr/bin/bash -x

for i in {0..2}
do
    echo $i
    hex="0x1"
    cpu=$((hex << i))
    taskset `printf '0x%x\n' $cpu` nohup ./run_max_diversity_brham.sh divs_${i} divs_dir_${i} divs_br_${i} &> out_br_${i} &
done
for i in {0..2}
do
    echo $i
    hex="0x8"
    cpu=$((hex << i))
    taskset `printf '0x%x\n' $cpu` nohup ./run_max_diversity_lev.sh divs_${i} divs_dir_${i} divs_lev_${i} &> out_lev_${i} &
done
for i in {0..2}
do
    echo $i
    hex="0x40"
    cpu=$((hex << i))
    taskset `printf '0x%x\n' $cpu` nohup ./run_max_diversity_ham.sh divs_${i} divs_dir_${i} divs_ham_${i} &> out_ham_${i} &
done
for i in {0..2}
do
    echo $i
    hex="0x200"
    cpu=$((hex << i))
    taskset `printf '0x%x\n' $cpu` nohup ./run_max_diversity_dham.sh divs_${i} divs_dir_${i} divs_diff_${i} &> out_diff_${i} &
done

