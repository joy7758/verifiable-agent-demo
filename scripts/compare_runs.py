#!/usr/bin/env python3
"""Generate baseline vs evidence-chain comparison outputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from paper_eval import compare_runs


def main() -> int:
    summary = compare_runs()
    print(json.dumps(summary["modes"], indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
