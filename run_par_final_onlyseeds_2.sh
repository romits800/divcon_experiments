#!/usr/bin/bash -x

seeds=`cat seeds3.txt`

seedar=($seeds)
for i in {0..4}
do
    s=${seedar[$i]}
    #s=${arrs[$i]}
    hex="0x1"
    cpu1=$((hex << i))
    cpu2=$((cpu1 << 5)) # << 12:its sibling - hyperthread
    m2=$((cpu1 | cpu2))
    ./run_many_seeds.sh $m2 "$s" &
done
