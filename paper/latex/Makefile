PYTHON ?= python3
LATEXMK ?= latexmk

.PHONY: all tables pdf clean

all: pdf

tables:
	$(PYTHON) scripts/generate_tables.py

pdf: tables
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error main.tex

clean:
	$(LATEXMK) -C
