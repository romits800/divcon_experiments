#!/usr/bin/bash -x

for i in {1..5}
do
    bash -x ./run.sh divs_${i} divs_dir_${i} &> out_${i}
done

