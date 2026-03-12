#!/usr/bin/env python3
"""Review an exported run bundle and emit JSON by default."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from paper_eval import review_run_directory


def main() -> int:
    parser = argparse.ArgumentParser(description="Review a paper evaluation run directory.")
    parser.add_argument("--run-dir", required=True, help="Path to artifacts/runs/<task_id>/<mode>")
    parser.add_argument("--human", action="store_true", help="Print a human-readable summary.")
    args = parser.parse_args()

    review = review_run_directory(args.run_dir)
    if args.human:
        print(f"run_dir: {review['run_dir']}")
        print(f"task_id: {review['task_id']}")
        print(f"mode: {review['mode']}")
        print(f"intent_captured: {review['intent_captured']}")
        print(f"policy_checked: {review['policy_checked']}")
        print(f"execution_verified: {review['execution_verified']}")
        print(f"receipt_exported: {review['receipt_exported']}")
        print(f"overall_status: {review['overall_status']}")
        if review["missing_or_failed_checks"]:
            print("missing_or_failed_checks:")
            for item in review["missing_or_failed_checks"]:
                print(f"- {item}")
        print(f"summary: {review['summary']}")
    else:
        print(json.dumps(review, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
