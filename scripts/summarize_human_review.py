#!/usr/bin/env python3
"""Summarize completed human review sheets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from paper_eval.common import HUMAN_REVIEW_ARTIFACTS_DIR, HUMAN_REVIEW_DIR
from paper_eval.human_review import summarize_human_review


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize completed human review sheets.")
    parser.add_argument("--sheet", action="append", required=True, help="Path to a completed review CSV.")
    parser.add_argument("--kit-dir", default=str(HUMAN_REVIEW_DIR))
    parser.add_argument(
        "--output-prefix",
        default=str(HUMAN_REVIEW_ARTIFACTS_DIR / "human-review-summary"),
        help="Output path prefix without extension.",
    )
    args = parser.parse_args()

    summary = summarize_human_review(
        [Path(sheet).resolve() for sheet in args.sheet],
        kit_dir=Path(args.kit_dir).resolve(),
        output_prefix=Path(args.output_prefix).resolve(),
    )
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
