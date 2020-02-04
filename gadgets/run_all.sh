#!/bin/bash
bash run_ex.sh  &> ou3
grep -E "(python create|^MaxAverage|^Number divs)" ou3 > out
python extract_results.py
