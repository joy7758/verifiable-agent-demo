#!/usr/bin/env python3
"""Run a small reviewer-oriented sanity check over the anonymous ASE 2026 artifact."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from paper_eval import review_run_directory


REQUIRED_FILES = [
    "manuscript.pdf",
    "README.md",
    "artifacts/metrics/comparison-summary.json",
    "artifacts/metrics/external-baseline-summary.json",
    "artifacts/metrics/ablation-summary.json",
    "artifacts/metrics/falsification-summary.json",
    "paper/latex/main.tex",
    "paper/latex/scripts/generate_tables.py",
    "scripts/review_bundle.py",
]

SAMPLE_REVIEWS = {
    "artifacts/runs/task-001/baseline": "partial",
    "artifacts/runs/task-001/evidence_chain": "pass",
    "artifacts/runs/task-012/evidence_chain": "policy_blocked",
    "artifacts/runs/task-015/evidence_chain": "tamper_detected",
    "artifacts/reviews/falsification/task-001/payload_tamper": "partial",
    "artifacts/reviews/falsification/task-012/policy_bypass_claim": "partial",
}


def main() -> int:
    missing = [path for path in REQUIRED_FILES if not (ROOT_DIR / path).exists()]
    if missing:
        print("missing required files:")
        for path in missing:
            print(f"- {path}")
        return 1

    subprocess.run(
        [sys.executable, "scripts/generate_tables.py"],
        check=True,
        cwd=ROOT_DIR / "paper" / "latex",
    )

    generated_tables = [
        "paper/latex/tables/framework_pair_comparison.tex",
        "paper/latex/tables/ablation_summary.tex",
        "paper/latex/tables/falsification_summary.tex",
    ]
    for path in generated_tables:
        if not (ROOT_DIR / path).exists():
            print(f"missing generated table: {path}")
            return 1

    failed_reviews: list[str] = []
    for run_dir, expected_status in SAMPLE_REVIEWS.items():
        review = review_run_directory(ROOT_DIR / run_dir)
        actual_status = review["overall_status"]
        if actual_status != expected_status:
            failed_reviews.append(f"{run_dir}: expected {expected_status}, got {actual_status}")

    if failed_reviews:
        print("sample review checks failed:")
        for item in failed_reviews:
            print(f"- {item}")
        return 1

    print("reviewer quick check passed")
    print("verified files:")
    for path in REQUIRED_FILES:
        print(f"- {path}")
    print("sample bundle statuses:")
    for run_dir, expected_status in SAMPLE_REVIEWS.items():
        print(f"- {run_dir}: {expected_status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
