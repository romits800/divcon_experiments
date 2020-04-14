#!/usr/bin/bash -x

for i in divs_*_*/divs_?
do
    echo $i
    taskset "0xffffff" python calculate_max_div_2_nodata.py -p $i &
    taskset "0xffffff" python calculate_rest_2_nodata.py -p $i &
done

#done
