#!/usr/bin/bash -x

seeds=`cat seeds.txt`

for seed in seeds
do

for i in {0..0}
do
    taskset "0x3" nohup ./run_max_diversity_brham.sh divs_${i} divs_dir_${i} divs_br_${i} $seed &> out_br_${i} &
done
for i in {0..0}
do
    taskset "0xc" nohup ./run_max_diversity_lev.sh divs_${i} divs_dir_${i} divs_lev_${i} $seed &> out_lev_${i} &
done
for i in {0..0}
do
    taskset "0x30" nohup ./run_max_diversity_ham.sh divs_${i} divs_dir_${i} divs_ham_${i} $seed &> out_ham_${i} &
done
for i in {0..0}
do
    taskset "0xc0" nohup ./run_max_diversity_dham.sh divs_${i} divs_dir_${i} divs_diff_${i} $seed &> out_diff_${i} &
done

exit 0
done
