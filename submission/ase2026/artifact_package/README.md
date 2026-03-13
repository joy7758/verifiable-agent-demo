# ASE 2026 Anonymous Artifact Package

This package supports reviewer verification for the manuscript:

`From Observability to Verifiability: An Execution Evidence Architecture for Agentic Software Systems`

## Purpose

The package is intentionally small. It lets reviewers inspect the frozen anonymous manuscript, the 16-task suite definition, the exported-bundle contract, the metric summaries used by the paper, a small set of representative sample bundles, and the scripts needed to regenerate LaTeX tables and re-run bundle review checks.

## Package Structure

- `manuscript.pdf`: convenience copy of the anonymous manuscript PDF
- `paper/latex/`: manuscript source snapshot and LaTeX table generator
- `evaluation/tasks/`: 16-task controlled suite inputs
- `artifacts/metrics/`: JSON summaries for main, external-baseline, ablation, falsification, and same-framework comparisons
- `artifacts/runs/`: representative sample run bundles
- `artifacts/reviews/falsification/`: representative falsified bundles
- `docs/paper_support/`: Markdown and CSV summaries aligned with the paper tables
- `docs/exported-bundle-contract.md`: compact description of the five-file export contract
- `paper_eval/` and `scripts/`: bundle-review logic and quick-check helpers

## Quick Start

Run the reviewer quick check from the package root:

```bash
python3 scripts/reviewer_quick_check.py
```

Inspect a sample bundle directly:

```bash
python3 scripts/review_bundle.py --run-dir artifacts/runs/task-001/evidence_chain --human
python3 scripts/review_bundle.py --run-dir artifacts/reviews/falsification/task-012/policy_bypass_claim --human
```

Regenerate LaTeX tables:

```bash
cd paper/latex
python3 scripts/generate_tables.py
```

Rebuild the manuscript PDF if a LaTeX environment is available:

```bash
cd paper/latex
make pdf
```

## What Can Be Regenerated

- table fragments under `paper/latex/tables/` from the packaged metric summaries
- bundle-review verdicts for the included sample bundles
- the anonymous manuscript PDF, provided a compatible LaTeX toolchain is available

## Synthetic Content

No human-study artifact is required for the paper's main claims, so synthetic smoke-test materials are intentionally omitted from this package. The included bundles and summaries are deterministic evaluation artifacts used to support the manuscript's bounded claims.

## Limitations

- This package is optimized for reviewer inspection rather than full rerun of every framework integration.
- The metrics are frozen summaries rather than fresh benchmark executions.
- Public DOI release is intentionally deferred during double-anonymous review.
