#!/usr/bin/env python3
"""Validate the paper evaluation task suite and print category counts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from paper_eval import load_tasks, validate_task_suite


def main() -> int:
    tasks = load_tasks()
    report = validate_task_suite(tasks)
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
