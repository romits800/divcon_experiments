#!/usr/bin/bash -x

seeds=`cat seeds.txt`

for seed in $seeds
do
for i in {0..5}
do
    echo $i
    hex="0x1"
    cpu1=$((hex << i))
    cpu2=$((cpu1 << 6)) # << 12:its sibling - hyperthread
    m2=$((cpu1 | cpu2))
    time taskset `printf '0x%x\n' $m2` nohup ./run_max_diversity.sh divs_${i} divs_dir_${i} divs_md_${seed}_${i} $seed &> out_all_${seed}_${i} &
done
sleep 30h
# 
while pgrep -f gecode-diversify; 
do
    sleep 1h
done


done
