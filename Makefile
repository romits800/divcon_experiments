
.PHONY: clean

run-par:
	./run_par.sh

run-par-br:
	./run_par.sh branch

merge:
	./run_calculate.sh
	python merge.py &> outmerge

clean: 
	${RM} -rf divs_* divs.pickle
	${RM} *.json *.uni *.llvm.mir
