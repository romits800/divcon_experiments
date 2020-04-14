
.PHONY: clean run-par

RUN_SCRIPT=run_par_final.sh

LOG_FILE=out_final
CLOG_FILE=out_calc
GLOG_FILE=out_gadg

RESULTS=divs_105_3 divs_330_0 divs_362_1 divs_393_2 divs_434_3 divs_453_0 divs_476_1 divs_539_2 divs_557_3 divs_655_0 divs_676_1 divs_714_2 divs_762_3 divs_770_0 divs_776_1 divs_798_2 divs_855_3 divs_965_0 divs_968_1 divs_973_2

all: run-par aggr gadgets

run-par:  ${RESULTS}
	bash -x ${RUN_SCRIPT}  &> ${LOG_FILE} &
	
aggr: rest_divs.pickle max_div_divs.pickle
	bash -x scripts/run_calculate.sh $(PWD) &> ${CLOG_FILE} &
	python scripts/merge_nodata.py -n max_div &> outmerge
	python scripts/merge_nodata.py -n rest &> outmerge

gadgets: hist_gaps_output0.7hamming.csv 
	bash -x scripts/run_jop.sh &> ${GLOG_FILE} &
	python scripts/extract_results.py . both true  &> out_extract_results

results:
	python scripts/generate_results.py $(PWD)

clean: 
	${RM} out* *.json *.uni *.llvm.mir

clean_divs:
	${RM} -rf divs_* divs.pickle
