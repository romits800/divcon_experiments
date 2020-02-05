#!/bin/bash
path=$1

for i in $path/divs_?/*.*; 
do 
    bench="${i##*/}"; ./create_o.sh $bench $path
done
