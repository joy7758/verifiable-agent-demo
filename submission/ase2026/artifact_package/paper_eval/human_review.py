"""Human review kit generation and result summarization."""

from __future__ import annotations

import csv
import shutil
from pathlib import Path
from typing import Any

from .common import EXPORTED_FILES, HUMAN_REVIEW_ARTIFACTS_DIR, HUMAN_REVIEW_DIR, REVIEW_QUESTIONS, ROOT_DIR, load_json, write_json

BLINDED_SAMPLES = [
    {"bundle_id": "bundle-001", "task_id": "task-001", "mode": "baseline", "focus": "read-only control"},
    {"bundle_id": "bundle-002", "task_id": "task-005", "mode": "baseline", "focus": "tool-call control"},
    {"bundle_id": "bundle-003", "task_id": "task-010", "mode": "baseline", "focus": "budget overflow control"},
    {"bundle_id": "bundle-004", "task_id": "task-015", "mode": "baseline", "focus": "tamper control"},
    {"bundle_id": "bundle-005", "task_id": "task-001", "mode": "evidence_chain", "focus": "read-only evidence chain"},
    {"bundle_id": "bundle-006", "task_id": "task-005", "mode": "evidence_chain", "focus": "tool-call evidence chain"},
    {"bundle_id": "bundle-007", "task_id": "task-010", "mode": "evidence_chain", "focus": "budget block evidence chain"},
    {"bundle_id": "bundle-008", "task_id": "task-015", "mode": "evidence_chain", "focus": "tamper-detected evidence chain"},
]


def generate_human_review_kit() -> dict[str, Any]:
    reviewer_dir = HUMAN_REVIEW_DIR / "reviewer"
    admin_dir = HUMAN_REVIEW_DIR / "admin"
    bundles_dir = HUMAN_REVIEW_DIR / "blinded_bundles"
    examples_dir = HUMAN_REVIEW_DIR / "examples"

    for path in (reviewer_dir, admin_dir, bundles_dir, examples_dir):
        path.mkdir(parents=True, exist_ok=True)

    answer_key = []
    reviewer_manifest_rows = []
    admin_manifest_rows = []

    for sample in BLINDED_SAMPLES:
        source_dir = ROOT_DIR / "artifacts" / "runs" / sample["task_id"] / sample["mode"]
        bundle_dir = bundles_dir / sample["bundle_id"]
        if bundle_dir.exists():
            shutil.rmtree(bundle_dir)
        bundle_dir.mkdir(parents=True, exist_ok=True)

        review_truth = derive_review_truth(source_dir)
        for filename in EXPORTED_FILES:
            shutil.copy2(source_dir / filename, bundle_dir / filename)

        answer_key.append(
            {
                "bundle_id": sample["bundle_id"],
                "hidden_condition": sample["mode"],
                "source_task_id": sample["task_id"],
                "bundle_path": str(bundle_dir.relative_to(HUMAN_REVIEW_DIR)),
                "correct_answers": review_truth,
            }
        )
        reviewer_manifest_rows.append(
            {
                "bundle_id": sample["bundle_id"],
                "bundle_path": str(bundle_dir.relative_to(HUMAN_REVIEW_DIR)),
                "task_focus": sample["focus"],
            }
        )
        admin_manifest_rows.append(
            {
                "bundle_id": sample["bundle_id"],
                "source_task_id": sample["task_id"],
                "hidden_condition": sample["mode"],
                "task_focus": sample["focus"],
            }
        )

    write_text(reviewer_dir / "instructions.md", reviewer_instructions_text())
    write_csv(reviewer_dir / "blinded-bundle-manifest.csv", reviewer_manifest_rows)
    write_csv(reviewer_dir / "review-sheet-template.csv", build_review_sheet_template())
    write_text(HUMAN_REVIEW_DIR / "README.md", human_review_readme_text())
    write_json(admin_dir / "answer-key.json", {"bundles": answer_key})
    write_csv(admin_dir / "bundle-manifest.csv", admin_manifest_rows)
    write_csv(examples_dir / "synthetic_review_sheet.csv", build_synthetic_review_sheet(answer_key))

    return {
        "bundle_count": len(BLINDED_SAMPLES),
        "reviewer_dir": str(reviewer_dir),
        "admin_dir": str(admin_dir),
        "examples_dir": str(examples_dir),
    }


def derive_review_truth(run_dir: Path) -> dict[str, bool]:
    intent = load_json(run_dir / "intent.json")
    action = load_json(run_dir / "action.json")
    trace = load_json(run_dir / "trace.json")
    receipt = load_json(run_dir / "receipt.json")
    return {
        "was_intent_captured": bool(intent.get("intent_captured")) and isinstance(intent.get("intent"), dict),
        "was_policy_checked": bool(action.get("policy", {}).get("checked")),
        "was_execution_verified": bool(trace.get("integrity", {}).get("checked"))
        and trace.get("integrity", {}).get("verification_status") == "verified",
        "was_receipt_exported": bool(receipt.get("receipt_exported"))
        and bool(receipt.get("audit_receipt", {}).get("artifacts")),
    }


def build_review_sheet_template() -> list[dict[str, str]]:
    rows = []
    for sample in BLINDED_SAMPLES:
        rows.append(
            {
                "reviewer_id": "",
                "bundle_id": sample["bundle_id"],
                "condition_hidden": "yes",
                "answer_1": "",
                "answer_2": "",
                "answer_3": "",
                "answer_4": "",
                "confidence": "",
                "time_spent_seconds": "",
                "uncertainty_notes": "",
            }
        )
    return rows


def build_synthetic_review_sheet(answer_key: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for index, item in enumerate(answer_key, start=1):
        truth = item["correct_answers"]
        answers = [
            truth["was_intent_captured"],
            truth["was_policy_checked"],
            truth["was_execution_verified"],
            truth["was_receipt_exported"],
        ]
        if item["bundle_id"] in {"bundle-002", "bundle-007"}:
            answers[2] = not answers[2]
        rows.append(
            {
                "reviewer_id": "synthetic-reviewer-01",
                "bundle_id": item["bundle_id"],
                "condition_hidden": "yes",
                "answer_1": bool_to_text(answers[0]),
                "answer_2": bool_to_text(answers[1]),
                "answer_3": bool_to_text(answers[2]),
                "answer_4": bool_to_text(answers[3]),
                "confidence": str(4 if index % 2 else 3),
                "time_spent_seconds": str(90 + index * 11),
                "uncertainty_notes": "Synthetic example data for smoke testing only.",
            }
        )
    return rows


def summarize_human_review(
    sheets: list[Path],
    *,
    kit_dir: Path | None = None,
    output_prefix: Path | None = None,
) -> dict[str, Any]:
    root_dir = kit_dir or HUMAN_REVIEW_DIR
    answer_key_path = root_dir / "admin" / "answer-key.json"
    answer_key_payload = load_json(answer_key_path)
    answer_key = {item["bundle_id"]: item for item in answer_key_payload["bundles"]}
    rows = load_review_rows(sheets)

    condition_stats: dict[str, dict[str, Any]] = {}
    overall_errors = {question: 0 for question in REVIEW_QUESTIONS}
    processed_rows = 0

    for row in rows:
        bundle_id = row["bundle_id"]
        if bundle_id not in answer_key:
            raise ValueError(f"unknown bundle_id in review sheet: {bundle_id}")
        key = answer_key[bundle_id]
        condition = key["hidden_condition"]
        stats = condition_stats.setdefault(
            condition,
            {
                "condition": condition,
                "rows": 0,
                "question_total": 0,
                "question_correct": 0,
                "confidence_sum": 0.0,
                "time_sum": 0.0,
                "error_count": 0,
                "question_errors": {question: 0 for question in REVIEW_QUESTIONS},
            },
        )

        stats["rows"] += 1
        processed_rows += 1
        stats["confidence_sum"] += float(row["confidence"])
        stats["time_sum"] += float(row["time_spent_seconds"])

        for question, field_name in zip(REVIEW_QUESTIONS, ("answer_1", "answer_2", "answer_3", "answer_4"), strict=True):
            stats["question_total"] += 1
            if parse_bool(row[field_name]) == key["correct_answers"][question]:
                stats["question_correct"] += 1
            else:
                stats["error_count"] += 1
                stats["question_errors"][question] += 1
                overall_errors[question] += 1

    by_condition = []
    for condition in ("baseline", "evidence_chain"):
        stats = condition_stats.get(condition)
        if stats is None:
            continue
        row_count = stats["rows"] or 1
        question_total = stats["question_total"] or 1
        by_condition.append(
            {
                "condition": condition,
                "bundle_reviews": stats["rows"],
                "question_accuracy": round(stats["question_correct"] / question_total, 4),
                "mean_confidence": round(stats["confidence_sum"] / row_count, 2),
                "mean_review_time_seconds": round(stats["time_sum"] / row_count, 2),
                "error_count": stats["error_count"],
                "question_errors": stats["question_errors"],
            }
        )

    summary = {
        "sheet_count": len(sheets),
        "row_count": processed_rows,
        "by_condition": by_condition,
        "overall_error_counts": overall_errors,
        "source_sheets": [str(path) for path in sheets],
        "answer_key": str(answer_key_path),
        "synthetic_example": any("synthetic" in path.name for path in sheets),
    }

    if output_prefix is not None:
        write_summary_outputs(summary, output_prefix)
    return summary


def load_review_rows(sheets: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sheets:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if not row.get("reviewer_id") or not row.get("bundle_id"):
                    continue
                rows.append({key: (value or "").strip() for key, value in row.items()})
    if not rows:
        raise ValueError("no completed review rows found in provided sheets")
    return rows


def write_summary_outputs(summary: dict[str, Any], output_prefix: Path) -> None:
    output_prefix.parent.mkdir(parents=True, exist_ok=True)
    json_path = output_prefix.with_suffix(".json")
    csv_path = output_prefix.with_suffix(".csv")
    md_path = output_prefix.with_suffix(".md")

    write_json(json_path, summary)
    write_csv(csv_path, summary["by_condition"])
    lines = [
        "# Human Review Summary",
        "",
        "Synthetic example." if summary["synthetic_example"] else "Collected review sheets.",
        "",
        "| condition | bundle_reviews | question_accuracy | mean_confidence | mean_review_time_seconds | error_count |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary["by_condition"]:
        lines.append(
            "| {condition} | {bundle_reviews} | {question_accuracy} | {mean_confidence} | "
            "{mean_review_time_seconds} | {error_count} |".format(**row)
        )
    lines.extend(
        [
            "",
            f"Source sheets: {', '.join(summary['source_sheets'])}",
            f"Answer key: {summary['answer_key']}",
        ]
    )
    write_text(md_path, "\n".join(lines) + "\n")


def reviewer_instructions_text() -> str:
    return """# Reviewer Instructions

Review each blinded bundle independently.

For every bundle:

1. Inspect the five JSON files in the bundle directory.
2. Answer the four yes/no questions in the review sheet.
3. Record confidence on a 1-5 scale.
4. Record total time spent in seconds.
5. Add uncertainty notes if any field was hard to interpret.

Question mapping:

- `answer_1`: was intent captured?
- `answer_2`: was policy checked?
- `answer_3`: was execution verified?
- `answer_4`: was receipt exported?

Timing guidance:

- Start timing when you open a bundle.
- Stop timing when you finish the row for that bundle.
- If interrupted, note the interruption in `uncertainty_notes`.

Scoring guidance:

- Answer `yes` only when the bundle makes the capability explicit.
- Use `no` when the capability is absent, only implied, or cannot be verified from the files.
- Do not guess the hidden condition.
"""


def human_review_readme_text() -> str:
    return """# Human Review Kit

This directory contains a lightweight blinded review kit for comparing baseline and evidence-chain bundles.

Structure:

- `reviewer/` contains instructions, the blinded bundle manifest, and the blank review-sheet template.
- `admin/` contains the hidden answer key and an unblinded bundle manifest for summarization.
- `blinded_bundles/` contains copied run bundles with stable `bundle-XXX` identifiers.
- `examples/` contains synthetic example review sheets for smoke testing only.
"""


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"yes", "true", "1"}:
        return True
    if normalized in {"no", "false", "0"}:
        return False
    raise ValueError(f"unsupported boolean value: {value!r}")


def bool_to_text(value: bool) -> str:
    return "yes" if value else "no"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0]) if rows else []
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
