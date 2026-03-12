#!/usr/bin/env python3
"""CLI wrapper for deterministic paper evaluation runs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from paper_eval import list_modes, run_suite


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the paper evaluation harness.")
    parser.add_argument("--mode", required=True, choices=list_modes())
    parser.add_argument("--task-id", help="Optional single task id.")
    args = parser.parse_args()

    summary = run_suite(mode=args.mode, task_id=args.task_id)
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
