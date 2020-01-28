#!/bin/bash

for i in divs_0/*.*; 
do 
    bench="${i##*/}"; ./create_o.sh $bench 
done
