#!/usr/bin/bash -x

seeds=`cat seeds3.txt`

seedar=($seeds)
for i in {0..4}
do
    s=${seedar[$i]}
    hex="0x1"
    cpu1=$((hex << i))
    cpu2=$((cpu1 << 5)) 
    procs=$((cpu1 | cpu2))


    bash -c "
        seeds=$s
        IFS=','; seedsarr=(\$seeds); unset IFS;
        for i in {0..3} 
        do
            s=\${seedsarr[\$i]}
            time taskset `printf '0x%x\n' $procs` nohup ./run_final.sh divs_\${i} divs_dir_\${i} divs_\${s}_\${i} \$s &> out_lns_\${s}_\${i}
        done" &

done
