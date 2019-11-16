
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

clean: 
	${RM} *.json *.uni *.llvm.mir

clean_divs:
	${RM} -rf divs_* divs.pickle
