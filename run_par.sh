#!/usr/bin/bash -x

for i in {0..4}
do
    echo $i
    hex="0x1"
    cpu1=$((hex << i))
    cpu2=$((cpu1 << 5))
    m2=$((cpu1 | cpu2))
    taskset `printf '0x%x\n' $m2` nohup ./run.sh divs_${i} divs_dir_${i} &> out_${i} &
done

