#!/bin/bash
path=$1
output=$2

bash run_ex.sh $path &> ou3
grep -E "(python create|^MaxAverage|^Number divs)" ou3 > out
grep -E "(python create|^BothAverage|^Number divs)" ou3 > out1
python extract_results.py > $output
echo "Both" >> $output
python extract_results.py out1 >> $output
