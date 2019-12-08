#!/usr/bin/bash -x

if [ "$1" == "c" ]
then
for i in {0..5}
do
    echo $i
    hex="0x1"
    cpu1=$((hex << i))
    cpu2=$((cpu1 << 6))
    cpu=$((cpu1 | cpu2))
    taskset `printf '0x%x\n' $cpu` nohup ./run_neigh_c.sh divs_${i} divs_dir_${i} divs_neigh_c_${i} &> out_c_${i} &
    sleep 123
done
elif [ "$1" == "ci" ]
then
for i in {0..5}
do
    echo $i
    hex="0x1"
    cpu1=$((hex << i))
    cpu2=$((cpu1 << 6))
    cpu=$((cpu1 | cpu2))
    taskset `printf '0x%x\n' $cpu` nohup ./run_neigh_ci.sh divs_${i} divs_dir_${i} divs_neigh_ci_${i} &> out_ci_${i} &
    sleep 123
done
elif ["$1" == "all"]
then
for i in {0..5}
do
    echo $i
    hex="0x1"
    cpu1=$((hex << i))
    cpu2=$((cpu1 << 6))
    cpu=$((cpu1 | cpu2))
    taskset `printf '0x%x\n' $cpu` nohup ./run_neigh_all.sh divs_${i} divs_dir_${i} divs_neigh_all_${i} &> out_all_${i} &
    sleep 123
done
fi

