#!/usr/bin/bash -x

seeds=`cat seeds2.txt`

for seed in $seeds
do
#seedi=(${seed//,/ })
IFS=','; arrs=($seed); unset IFS;
for i in {0..4}
do
    s=${arrs[$i]}
    echo $i
    hex="0x1"
    cpu1=$((hex << i))
    cpu2=$((cpu1 << 5)) # << 12:its sibling - hyperthread
    m2=$((cpu1 | cpu2))
    time taskset `printf '0x%x\n' $m2` nohup ./run_final.sh divs_${i} divs_dir_${i} divs_${s}_${i} $s &> out_lns_${s}_${i} &
done
sleep 13h

while pgrep -f gecode-diversify; 
do
    sleep 1h
done

done