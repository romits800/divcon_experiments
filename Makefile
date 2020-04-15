
.PHONY: clean run-par

SCRIPTS_PATH = scripts
GADG_PATH = ${SCRIPTS_PATH}/gadgets
RUN_SCRIPT = run_par_final.sh
CALC_SCRIPT = ${SCRIPTS_PATH}/run_calculate.sh
MERGE_SCRIPT = ${SCRIPTS_PATH}/merge_nodata.py
GADG_SCRIPT = ${GADG_PATH}/run_jop.sh
EXTRACT_SCRIPT = ${GADG_PATH}/extract_results.py
GENRES_SCRIPT = ${SCRIPTS_PATH}/generate_results.py 

LOG_FILE = out_final
CLOG_FILE = out_calc
GLOG_FILE = out_gadg
MLOG_FILE = out_merge
ELOG_FILE = out_extract

export SHELL := /bin/bash

RESULTS = divs_105_3 divs_330_0 divs_362_1 divs_393_2 divs_434_3 divs_453_0 divs_476_1 divs_539_2 divs_557_3 divs_655_0 divs_676_1 divs_714_2 divs_762_3 divs_770_0 divs_776_1 divs_798_2 divs_855_3 divs_965_0 divs_968_1 divs_973_2

PICKLES = rest_divs.pickle max_div_divs.pickle

OUTFILE = hist_gaps_output0.7hamming.csv 

all: run-par aggr merge gadgets results

run-par: ${RUN_SCRIPT}
	@echo "bash -x ${RUN_SCRIPT} > ${LOG_FILE} 2>&1"
	bash -x ${RUN_SCRIPT}  > ${LOG_FILE} 2>&1 &
	
aggr: ${CALC_SCRIPT} 
	@echo "bash -x ${CALC_SCRIPT} $(PWD) &> ${CLOG_FILE}"
	bash -x ${CALC_SCRIPT} $(PWD) &> ${CLOG_FILE} 

merge: ${MERGE_SCRIPT}
	@echo "python ${MERGE_SCRIPT} -n max_div &> ${MLOG_FILE}"
	python ${MERGE_SCRIPT} -n max_div &> ${MLOG_FILE}
	@echo "python ${MERGE_SCRIPT} -n rest &> ${MLOG_FILE}"
	python ${MERGE_SCRIPT} -n rest &> ${MLOG_FILE}

gadgets: ${GADG_SCRIPT}
	@echo "bash -x ${GADG_SCRIPT} ${PWD}/${GADG_PATH} ${PWD} &> ${GLOG_FILE}"
	bash -x ${GADG_SCRIPT} ${PWD}/${GADG_PATH}  ${PWD} &> ${GLOG_FILE}

extract: ${EXTRACT_SCRIPT}
	@echo "python ${EXTRACT_SCRIPT} ${PWD} both true  &> ${ELOG_FILE}"
	python ${EXTRACT_SCRIPT} ${PWD} both true  &> ${ELOG_FILE}

results: ${GENRES_SCRIPT} 
	python ${GENRES_SCRIPT} $(PWD)

clean: 
	${RM} ${PICKLES} ${OUTFILE} *.csv

clean-divs: 
	${RM} -rf ${RESULTS} 
