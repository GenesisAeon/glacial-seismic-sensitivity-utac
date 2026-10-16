# Build the P133 preprint. Requires pdflatex, biber and latexmk (TeX Live).
PY ?= python

all: P133_preprint.pdf

figures:
	$(PY) figures/make_paper_figures.py

bib:
	$(PY) bib/build_bib.py

P133_preprint.pdf: P133_preprint.tex references.bib
	latexmk -pdf -interaction=nonstopmode P133_preprint.tex

clean:
	latexmk -c P133_preprint.tex

.PHONY: all figures bib clean
