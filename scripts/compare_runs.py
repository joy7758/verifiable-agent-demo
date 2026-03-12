#!/usr/bin/env python3
"""Generate baseline vs evidence-chain comparison outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from paper_eval import compare_runs


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate comparison summaries from actual run artifacts.")
    parser.add_argument("--modes", nargs="+", help="Ordered list of modes to compare.")
    parser.add_argument("--output-stem", default="comparison-summary")
    parser.add_argument("--title", default="Comparison Summary")
    parser.add_argument(
        "--description",
        default="Generated from actual artifacts under `artifacts/runs/` using deterministic rule-based scoring.",
    )
    parser.add_argument("--doc-reference", default="docs/paper_support/comparison-workflow.md")
    args = parser.parse_args()

    summary = compare_runs(
        args.modes,
        output_stem=args.output_stem,
        title=args.title,
        description=args.description,
        doc_reference=args.doc_reference,
    )
    print(json.dumps(summary["modes"], indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
