#!/usr/bin/env python3
"""Generate falsified bundles and summarize how the independent review contract reacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from paper_eval import run_falsification_checks


def main() -> int:
    summary = run_falsification_checks()
    print(json.dumps(summary["scenarios"], indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
