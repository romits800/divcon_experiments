#!/usr/bin/bash -x

for i in {0..3}
do
    echo $i
    hex="0x1"
    cpu=$((hex << i))
    taskset `printf '0x%x\n' $cpu` nohup ./run_neigh_c.sh divs_${i} divs_dir_${i} divs_neigh_c_${i} &> out_c_${i} &
done
for i in {0..3}
do
    echo $i
    hex="0x10"
    cpu=$((hex << i))
    taskset `printf '0x%x\n' $cpu` nohup ./run_neigh_ci.sh divs_${i} divs_dir_${i} divs_neigh_ci_${i} &> out_ci_${i} &
done
for i in {0..3}
do
    echo $i
    hex="0x100"
    cpu=$((hex << i))
    taskset `printf '0x%x\n' $cpu` nohup ./run_neigh_all.sh divs_${i} divs_dir_${i} divs_neigh_all_${i} &> out_all_${i} &
done

