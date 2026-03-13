"""Shared constants and helpers for the paper evaluation harness."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
TASK_DIR = ROOT_DIR / "evaluation" / "tasks"
RUNS_DIR = ROOT_DIR / "artifacts" / "runs"
REVIEWS_DIR = ROOT_DIR / "artifacts" / "reviews"
FALSIFICATION_DIR = REVIEWS_DIR / "falsification"
METRICS_DIR = ROOT_DIR / "artifacts" / "metrics"
PAPER_DOCS_DIR = ROOT_DIR / "docs" / "paper_support"
SCHEMAS_DIR = ROOT_DIR / "schemas" / "paper_eval"
HUMAN_REVIEW_DIR = ROOT_DIR / "evaluation" / "human_review"
HUMAN_REVIEW_ARTIFACTS_DIR = ROOT_DIR / "artifacts" / "human_review"

SCHEMA_VERSION = "paper-eval.v1"
EXPORTED_FILES = [
    "intent.json",
    "action.json",
    "result.json",
    "trace.json",
    "receipt.json",
]

EXPECTED_CATEGORY_COUNTS = {
    "read_only_query": 4,
    "tool_call": 4,
    "budget_constrained": 3,
    "approval_required": 3,
    "tamper_scenario": 2,
}

REVIEW_QUESTIONS = [
    "was_intent_captured",
    "was_policy_checked",
    "was_execution_verified",
    "was_receipt_exported",
]

RUN_MODE_HOURS = {
    "baseline": 0,
    "external_baseline": 1,
    "no_intent": 2,
    "no_governance": 3,
    "no_integrity": 4,
    "no_receipt": 5,
    "evidence_chain": 6,
    "external_evidence_chain": 7,
    "langchain_baseline": 8,
    "langchain_evidence_chain": 9,
}


def canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_digest(payload: Any) -> str:
    return f"sha256:{hashlib.sha256(canonical_json(payload).encode('utf-8')).hexdigest()}"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def reset_directory(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def mutate_digest(digest: str) -> str:
    prefix, value = digest.split(":", 1)
    replacement = "0" if value[0] != "0" else "1"
    return f"{prefix}:{replacement}{value[1:]}"


def stable_timestamp(task_id: str, mode: str, second_offset: int = 0) -> str:
    task_number = int(task_id.split("-")[-1])
    hour = RUN_MODE_HOURS.get(mode, 23)
    minute = task_number
    second = second_offset
    return f"2026-03-01T{hour:02d}:{minute:02d}:{second:02d}Z"


def relative_to_root(path: Path) -> str:
    return str(path.relative_to(ROOT_DIR))
