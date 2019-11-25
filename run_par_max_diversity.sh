#!/usr/bin/bash -x

for i in {0..0}
do
    taskset "0x3" nohup ./run_max_diversity_brham.sh divs_${i} divs_dir_${i} divs_br_${i} &> out_br_${i} &
done
for i in {0..0}
do
    taskset "0xc" nohup ./run_max_diversity_lev.sh divs_${i} divs_dir_${i} divs_lev_${i} &> out_lev_${i} &
done
for i in {0..0}
do
    taskset "0x30" nohup ./run_max_diversity_ham.sh divs_${i} divs_dir_${i} divs_ham_${i} &> out_ham_${i} &
done
for i in {0..0}
do
    taskset "0xc0" nohup ./run_max_diversity_dham.sh divs_${i} divs_dir_${i} divs_diff_${i} &> out_diff_${i} &
done

