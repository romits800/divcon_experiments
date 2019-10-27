
.PHONY: clean

run-par:
	./run_par.sh

run-par-br:
	./run_par.sh branch

merge:
	./run_calculate
	python merge &> outmerge

clean: 
	${RM} -rf divs_*
	${RM} *.json *.uni *.llvm.mir
