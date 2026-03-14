#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_ROOT="artifacts/demo_output"

cd "$ROOT_DIR"
python3 -m demo.agent --output-root "${OUTPUT_ROOT}"
cat "${OUTPUT_ROOT}/evidence/example_audit.json"
cat "${OUTPUT_ROOT}/evidence/result.json"
