#!/usr/bin/bash -x

for i in 0 1 2 3 4
do 
    echo divs_*_${i}/divs_${i}; 
    taskset "0x800" python calculate_max_div_2_nodata.py -p divs_*_${i}/divs_${i}/
done
