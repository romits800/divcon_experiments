
PDF_FILE=select_relax
FINAL_PDF=

.PHONY: ${PDF_FILE}.pdf all spellcheck

all: ${PDF_FILE}.pdf

${PDF_FILE}.pdf: clean ${PDF_FILE}.tex
	xelatex ${PDF_FILE}.tex
	xelatex ${PDF_FILE}.tex

build: ${PDF_FILE}.tex
	latexmk -pdf ${PDF_FILE}.tex

spellcheck: *.tex
	aspell -t -c ${PDF_FILE}.tex

clean:
	${RM} *~ *.aux *.log *.bbl *.blg *.out ${PDF_FILE}.pdf
