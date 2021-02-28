#!/usr/bin/bash -x

path=$1

for i in $path/divs_*_*/divs_?
do
    echo $i
    taskset "0xffffff" python ${DIVCONEXP_PATH}/scripts/calculate_max_div_2_nodata.py -p $i &
    taskset "0xffffff" python ${DIVCONEXP_PATH}/scripts/calculate_rest_2_nodata.py -p $i &
done
#done
