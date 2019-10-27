
FUNCTION=factorial
TARGET=factorial.s
PRESOLVER_FLAGS=--verbose
SOLVER_FLAGS=--verbose
LLC_FLAGS=-disable-post-ra -disable-tail-duplicate -disable-branch-fold -disable-block-placement

.PHONY: clean

all: ${TARGET}


%.uni: %.mir
	uni import --target=Mips $< -o $@ --function ${FUNCTION} --maxblocksize=25 --goal=speed

%.lssa.uni:%.uni
	uni linearize --target=Mips $< -o $@

%.ext.uni:%.lssa.uni
	uni extend --target=Mips $< -o $@

%.alt.uni:%.ext.uni
	uni augment --target=Mips $< -o $@

%.llvm.mir:%.asm.mir
	uni normalize --target=Mips $< -o $@

%.json:%.alt.uni
	uni model --target=Mips $< -o $@ +RTS -K20M -RTS

%.ext.json:%.json
	gecode-presolver -o $@ ${PRESOLVER_FLAGS} $<

%.out.json:%.ext.json
	gecode-solver -o $@ ${SOLVER_FLAGS} $<

%.unison.mir:%.alt.uni %.out.json
	uni export --target=Mips $< -o $@ --solfile=$(word 2,$^)

%.s:%.unison.mir
	llc $< -march=mips -mcpu=mips32  ${LLC_FLAGS} -start-after livedebugvars -o $@


clean:
	${RM} *.json *.uni *.llvm.mir *.unison.mir ${TARGET}



