
.PHONY: clean

run-par:
	./run_par.sh

run-par-fast:
	./run_par_fast.sh


run-par-br:
	./run_par.sh branch

merge:
	./run_calculate.sh
	python merge.py &> outmerge

results:
	python generate_results.py

clean: 
	${RM} out* *.json *.uni *.llvm.mir

clean_divs:
	${RM} -rf divs_* divs.pickle
