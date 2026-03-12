# LaTeX Manuscript Draft

This directory contains the English LaTeX manuscript draft for the execution-evidence paper.

## Structure

- `main.tex`: manuscript entry point
- `abstract.tex`: abstract body
- `sections/`: main paper sections
- `tables/`: generated LaTeX table fragments
- `figures/`: reserved for future verified figures
- `scripts/generate_tables.py`: regenerates table fragments from repository JSON summaries
- `refs.bib`: placeholder bibliography file with TODO notes only

## Compile

From this directory:

```bash
make
```

Or explicitly:

```bash
python3 scripts/generate_tables.py
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

The output PDF is written as `main.pdf`.

## Regenerate tables

The LaTeX tables are generated from these repository files:

- `../../artifacts/metrics/comparison-summary.json`
- `../../artifacts/metrics/external-baseline-summary.json`
- `../../artifacts/metrics/ablation-summary.json`

To refresh them:

```bash
python3 scripts/generate_tables.py
```

## Notes

- The manuscript is grounded in the current checked-in repository state.
- No external citations have been invented. Related-work citation TODOs remain in comments until references are verified.
- No figures are currently shipped; add only verified figures that match the repository implementation and outputs.
