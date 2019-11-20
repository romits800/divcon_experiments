#!/usr/bin/bash -x


if [ "$1" == "branch" ]
then
    for i in {0..4}
    do
        echo $i
        hex="0x1"
        cpu1=$((hex << i))
        cpu2=$((cpu1 << 12))
        m2=$((cpu1 | cpu2))
        taskset `printf '0x%x\n' $m2` nohup ./run_br.sh divs_${i} divs_dir_${i} &> out_br_${i} &
    done
elif [ "$1" == "levenshtein" ]
then
    for i in {0..4}
    do
        echo $i
        hex="0x1"
        cpu1=$((hex << i))
        cpu2=$((cpu1 << 12))
        m2=$((cpu1 | cpu2))
        taskset `printf '0x%x\n' $m2` nohup ./run_lev.sh divs_${i} divs_dir_${i} &> out_lev_${i} &
    done
else
    for i in {0..4}
    do
        echo $i
        hex="0x1"
        cpu1=$((hex << i))
        cpu2=$((cpu1 << 12)) # its sibling - hyperthread
        m2=$((cpu1 | cpu2))
        taskset `printf '0x%x\n' $m2` nohup ./run.sh divs_${i} divs_dir_${i} &> out_${i} &
    done
fi

