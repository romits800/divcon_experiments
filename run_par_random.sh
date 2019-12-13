#!/usr/bin/bash -x


for i in {0..5}
do
    echo $i
    hex="0x1"
    cpu1=$((hex << i))
    cpu2=$((cpu1 << 6)) # << 12:its sibling - hyperthread
    m2=$((cpu1 | cpu2))
    taskset `printf '0x%x\n' $m2` nohup ./run_random.sh divs_${i} divs_dir_${i} divs_random_${i}  &> out_random_${i} &
    sleep 123 
done
