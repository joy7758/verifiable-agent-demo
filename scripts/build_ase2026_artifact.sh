#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SUBMISSION_DIR="$ROOT_DIR/submission/ase2026"
BUILD_DIR="$SUBMISSION_DIR/.artifact_build"
PACKAGE_NAME="ase2026-anonymous-artifact"
STAGE_DIR="$BUILD_DIR/$PACKAGE_NAME"
PACKAGE_DIR="$SUBMISSION_DIR/artifact_package"
ARCHIVE_PATH="$SUBMISSION_DIR/${PACKAGE_NAME}.zip"

copy_file() {
  local rel_path="$1"
  mkdir -p "$STAGE_DIR/$(dirname "$rel_path")"
  cp "$ROOT_DIR/$rel_path" "$STAGE_DIR/$rel_path"
}

copy_dir() {
  local rel_path="$1"
  mkdir -p "$STAGE_DIR/$rel_path"
  cp -R "$ROOT_DIR/$rel_path"/. "$STAGE_DIR/$rel_path"/
}

copy_run_dir() {
  local rel_path="$1"
  mkdir -p "$STAGE_DIR/$(dirname "$rel_path")"
  cp -R "$ROOT_DIR/$rel_path" "$STAGE_DIR/$rel_path"
}

rm -rf "$BUILD_DIR" "$PACKAGE_DIR"
mkdir -p "$BUILD_DIR" "$STAGE_DIR"

paper_files=(
  "paper/latex/abstract.tex"
  "paper/latex/main.tex"
  "paper/latex/main.pdf"
  "paper/latex/Makefile"
  "paper/latex/refs.bib"
  "paper/latex/scripts/generate_tables.py"
  "paper/latex/sections/introduction.tex"
  "paper/latex/sections/method.tex"
  "paper/latex/sections/evaluation.tex"
  "paper/latex/sections/results.tex"
  "paper/latex/sections/related_work.tex"
  "paper/latex/sections/discussion.tex"
  "paper/latex/sections/conclusion.tex"
  "paper/latex/sections/data_availability.tex"
)

table_files=(
  "paper/latex/tables/ablation_summary.tex"
  "paper/latex/tables/external_comparison.tex"
  "paper/latex/tables/falsification_summary.tex"
  "paper/latex/tables/framework_pair_comparison.tex"
  "paper/latex/tables/main_comparison.tex"
)

metric_files=(
  "artifacts/metrics/comparison-summary.json"
  "artifacts/metrics/external-baseline-summary.json"
  "artifacts/metrics/ablation-summary.json"
  "artifacts/metrics/falsification-summary.json"
  "artifacts/metrics/framework-pair-summary.json"
  "artifacts/metrics/langchain-pair-summary.json"
)

summary_files=(
  "docs/paper_support/comparison-summary.md"
  "docs/paper_support/comparison-summary.csv"
  "docs/paper_support/external-baseline-summary.md"
  "docs/paper_support/external-baseline-summary.csv"
  "docs/paper_support/ablation-summary.md"
  "docs/paper_support/ablation-summary.csv"
  "docs/paper_support/falsification-summary.md"
  "docs/paper_support/falsification-summary.csv"
  "docs/paper_support/framework-pair-summary.md"
  "docs/paper_support/framework-pair-summary.csv"
  "docs/paper_support/langchain-pair-summary.md"
  "docs/paper_support/langchain-pair-summary.csv"
)

script_files=(
  "scripts/review_bundle.py"
  "scripts/reviewer_quick_check.py"
)

paper_eval_files=(
  "paper_eval/__init__.py"
  "paper_eval/common.py"
  "paper_eval/compare.py"
  "paper_eval/human_review.py"
  "paper_eval/modes.py"
  "paper_eval/review.py"
  "paper_eval/runner.py"
  "paper_eval/suite.py"
  "paper_eval/falsification.py"
)

schema_files=(
  "schemas/paper_eval/task.schema.json"
  "schemas/paper_eval/intent.schema.json"
  "schemas/paper_eval/action.schema.json"
  "schemas/paper_eval/result.schema.json"
  "schemas/paper_eval/trace.schema.json"
  "schemas/paper_eval/receipt.schema.json"
)

sample_run_dirs=(
  "artifacts/runs/task-001/baseline"
  "artifacts/runs/task-001/evidence_chain"
  "artifacts/runs/task-001/external_baseline"
  "artifacts/runs/task-001/external_evidence_chain"
  "artifacts/runs/task-001/langchain_baseline"
  "artifacts/runs/task-001/langchain_evidence_chain"
  "artifacts/runs/task-001/no_intent"
  "artifacts/runs/task-001/no_governance"
  "artifacts/runs/task-001/no_integrity"
  "artifacts/runs/task-001/no_receipt"
  "artifacts/runs/task-012/evidence_chain"
  "artifacts/runs/task-015/evidence_chain"
)

falsification_dirs=(
  "artifacts/reviews/falsification/task-001/payload_tamper"
  "artifacts/reviews/falsification/task-001/cross_run_replay_mismatch"
  "artifacts/reviews/falsification/task-012/policy_bypass_claim"
)

for path in "${paper_files[@]}" "${table_files[@]}" "${metric_files[@]}" "${summary_files[@]}" "${script_files[@]}" "${paper_eval_files[@]}" "${schema_files[@]}"; do
  copy_file "$path"
done

copy_dir "evaluation/tasks"

for path in "${sample_run_dirs[@]}" "${falsification_dirs[@]}"; do
  copy_run_dir "$path"
done

cp "$ROOT_DIR/paper/latex/main.pdf" "$STAGE_DIR/manuscript.pdf"

mkdir -p "$STAGE_DIR/docs"
cat > "$STAGE_DIR/docs/exported-bundle-contract.md" <<'EOF'
# Exported Bundle Contract

Each exported run bundle contains exactly five JSON files:

- `intent.json`
- `action.json`
- `result.json`
- `trace.json`
- `receipt.json`

The contract is shared across the local baseline, the full evidence chain, the live-framework baselines, the same-framework wrapped paths, and the four ablations.

Review logic:

- recomputes bundle identity consistency across all five files
- recomputes integrity digests and receipt artifact digests
- distinguishes reviewable success, policy-blocked, tamper-detected, and partial outcomes
- rejects falsified bundles when cross-file contradictions or digest mismatches appear

Included sample bundles cover:

- local baseline versus full evidence chain
- minimal live CrewAI and LangChain baselines and their wrapped evidence-chain counterparts
- four single-stage ablations
- one policy-blocked bundle
- one tamper-detected bundle
- representative falsification cases for payload tampering, replay mismatch, and policy-bypass claims
EOF

cat > "$STAGE_DIR/README.md" <<'EOF'
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
EOF

python3 - "$ROOT_DIR" "$STAGE_DIR" <<'PY'
import os
import sys
from pathlib import Path

repo_root = Path(sys.argv[1]).resolve()
stage_dir = Path(sys.argv[2]).resolve()
repo_prefix = f"{repo_root}{os.sep}"

text_suffixes = {
    ".bib",
    ".csv",
    ".json",
    ".md",
    ".py",
    ".schema.json",
    ".tex",
    ".txt",
}

for path in stage_dir.rglob("*"):
    if not path.is_file():
        continue
    suffix = "".join(path.suffixes) if len(path.suffixes) > 1 else path.suffix
    if suffix not in text_suffixes:
        continue
    text = path.read_text()
    updated = text.replace(repo_prefix, "")
    updated = updated.replace(str(repo_root), ".")
    updated = updated.replace(
        "https://example.com/verifiable-agent-demo/",
        "https://example.com/anonymous-artifact/",
    )
    updated = updated.replace("verifiable-agent-demo", "anonymous-artifact")
    if updated != text:
        path.write_text(updated)
PY

python3 - "$BUILD_DIR" "$PACKAGE_NAME" "$ARCHIVE_PATH" <<'PY'
import sys
import zipfile
from pathlib import Path

build_dir = Path(sys.argv[1])
package_name = sys.argv[2]
archive_path = Path(sys.argv[3])
root = build_dir / package_name

with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for path in sorted(root.rglob("*")):
        if path.is_file():
            zf.write(path, arcname=str(Path(package_name) / path.relative_to(root)))
PY

mkdir -p "$PACKAGE_DIR"
cp -R "$STAGE_DIR"/. "$PACKAGE_DIR"/
rm -rf "$BUILD_DIR"
