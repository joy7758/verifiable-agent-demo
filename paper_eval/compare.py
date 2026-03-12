"""Comparison pipeline for baseline vs evidence-chain runs."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .common import EXPORTED_FILES, METRICS_DIR, PAPER_DOCS_DIR, RUNS_DIR, load_json, write_json
from .review import review_run_directory
from .suite import load_tasks, validate_task_suite


def compare_runs() -> dict[str, Any]:
    tasks = load_tasks()
    validation = validate_task_suite(tasks)
    if not validation["valid"]:
        raise ValueError(f"task suite is invalid: {validation['errors']}")

    per_task: list[dict[str, Any]] = []
    summaries = {
        "baseline": _empty_summary("baseline"),
        "evidence_chain": _empty_summary("evidence_chain"),
    }

    for task in tasks:
        for mode in ("baseline", "evidence_chain"):
            run_dir = RUNS_DIR / task["task_id"] / mode
            row = evaluate_run(task, mode, run_dir)
            per_task.append(row)
            accumulate_summary(summaries[mode], row)

    for summary in summaries.values():
        finalize_summary(summary)

    output = {
        "modes": [summaries["baseline"], summaries["evidence_chain"]],
        "per_task": per_task,
    }
    write_outputs(output)
    return output


def evaluate_run(task: dict[str, Any], mode: str, run_dir: Path) -> dict[str, Any]:
    review = review_run_directory(run_dir)
    intent = load_json(run_dir / "intent.json")
    action = load_json(run_dir / "action.json")
    result = load_json(run_dir / "result.json")
    trace = load_json(run_dir / "trace.json")
    receipt = load_json(run_dir / "receipt.json")

    metrics = {
        "explicitness": score_explicitness(intent, action, result, receipt),
        "replayability": score_replayability(intent, action, trace, receipt),
        "tamper_sensitivity": score_tamper_sensitivity(task, trace),
        "audit_boundedness": score_audit_boundedness(receipt),
        "integration_surface": score_integration_surface(intent, action, trace, receipt),
    }
    return {
        "task_id": task["task_id"],
        "category": task["category"],
        "mode": mode,
        "result_status": result["status"],
        "review": review,
        "metrics": metrics,
    }


def score_explicitness(intent: dict[str, Any], action: dict[str, Any], result: dict[str, Any], receipt: dict[str, Any]) -> int:
    intent_object = intent.get("intent") or {}
    score = 0
    if intent.get("intent_captured") and intent_object.get("goal"):
        score += 1
    if action.get("policy", {}).get("checked"):
        score += 1
    if action.get("authorization_state") in {"approved", "blocked_budget", "blocked_approval"}:
        score += 1
    if result.get("status") and result.get("outputs", {}).get("summary"):
        score += 1
    if len(receipt.get("audit_receipt", {}).get("questions_answered", {})) == 4:
        score += 1
    return score


def score_replayability(intent: dict[str, Any], action: dict[str, Any], trace: dict[str, Any], receipt: dict[str, Any]) -> int:
    intent_object = intent.get("intent") or {}
    score = 0
    if intent_object.get("input_payload_snapshot"):
        score += 1
    if action.get("requested_action", {}).get("parameters"):
        score += 1
    if trace.get("execution", {}).get("deterministic_seed"):
        score += 1
    if len(trace.get("executed_steps", [])) >= 4:
        score += 1
    if len(receipt.get("audit_receipt", {}).get("artifacts", [])) >= 4:
        score += 1
    return score


def score_tamper_sensitivity(task: dict[str, Any], trace: dict[str, Any]) -> int:
    integrity = trace.get("integrity", {})
    score = 0
    if integrity.get("checked"):
        score += 1
    if integrity.get("subject_digests"):
        score += 1
    if integrity.get("expected_digests"):
        score += 1
    if integrity.get("verification_status") in {"verified", "tamper_detected", "skipped_by_policy"}:
        score += 1
    if task["tamper_case"]:
        if integrity.get("verification_status") == "tamper_detected":
            score += 1
    elif integrity.get("verification_status") == "verified":
        score += 1
    return score


def score_audit_boundedness(receipt: dict[str, Any]) -> int:
    audit_receipt = receipt.get("audit_receipt", {})
    score = 0
    if receipt.get("receipt_exported"):
        score += 1
    if audit_receipt.get("boundedness", {}).get("exported_files_count") == len(EXPORTED_FILES):
        score += 1
    if audit_receipt.get("boundedness", {}).get("allowed_files") == EXPORTED_FILES:
        score += 1
    if audit_receipt.get("boundedness", {}).get("artifact_digest_count") == 4:
        score += 1
    if len(audit_receipt.get("questions_answered", {})) == 4:
        score += 1
    return score


def score_integration_surface(
    intent: dict[str, Any], action: dict[str, Any], trace: dict[str, Any], receipt: dict[str, Any]
) -> int:
    return sum(
        [
            1 if intent.get("intent_captured") else 0,
            1 if action.get("requested_action") else 0,
            1 if action.get("policy", {}).get("checked") else 0,
            1 if trace.get("integrity", {}).get("checked") else 0,
            1 if receipt.get("receipt_exported") else 0,
        ]
    )


def _empty_summary(mode: str) -> dict[str, Any]:
    return {
        "mode": mode,
        "total_tasks": 0,
        "intent_captured_true": 0,
        "policy_checked_true": 0,
        "execution_verified_true": 0,
        "receipt_exported_true": 0,
        "overall_pass_or_policy_blocked": 0,
        "average_explicitness": 0.0,
        "average_replayability": 0.0,
        "average_tamper_sensitivity": 0.0,
        "average_audit_boundedness": 0.0,
        "average_integration_surface": 0.0,
    }


def accumulate_summary(summary: dict[str, Any], row: dict[str, Any]) -> None:
    summary["total_tasks"] += 1
    review = row["review"]
    summary["intent_captured_true"] += int(review["intent_captured"])
    summary["policy_checked_true"] += int(review["policy_checked"])
    summary["execution_verified_true"] += int(review["execution_verified"])
    summary["receipt_exported_true"] += int(review["receipt_exported"])
    summary["overall_pass_or_policy_blocked"] += int(review["overall_status"] in {"pass", "policy_blocked"})
    summary["average_explicitness"] += row["metrics"]["explicitness"]
    summary["average_replayability"] += row["metrics"]["replayability"]
    summary["average_tamper_sensitivity"] += row["metrics"]["tamper_sensitivity"]
    summary["average_audit_boundedness"] += row["metrics"]["audit_boundedness"]
    summary["average_integration_surface"] += row["metrics"]["integration_surface"]


def finalize_summary(summary: dict[str, Any]) -> None:
    total = summary["total_tasks"] or 1
    for field in (
        "average_explicitness",
        "average_replayability",
        "average_tamper_sensitivity",
        "average_audit_boundedness",
        "average_integration_surface",
    ):
        summary[field] = round(summary[field] / total, 2)


def write_outputs(output: dict[str, Any]) -> None:
    PAPER_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    markdown_path = PAPER_DOCS_DIR / "comparison-summary.md"
    csv_path = PAPER_DOCS_DIR / "comparison-summary.csv"
    json_path = METRICS_DIR / "comparison-summary.json"

    modes = output["modes"]
    markdown_lines = [
        "# Comparison Summary",
        "",
        "Generated from actual artifacts under `artifacts/runs/` using deterministic rule-based scoring.",
        "",
        "| mode | total_tasks | intent_captured_true | policy_checked_true | execution_verified_true | receipt_exported_true | avg_explicitness | avg_replayability | avg_tamper_sensitivity | avg_audit_boundedness | avg_integration_surface |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in modes:
        markdown_lines.append(
            "| {mode} | {total_tasks} | {intent_captured_true} | {policy_checked_true} | "
            "{execution_verified_true} | {receipt_exported_true} | {average_explicitness} | "
            "{average_replayability} | {average_tamper_sensitivity} | {average_audit_boundedness} | "
            "{average_integration_surface} |".format(**row)
        )
    markdown_lines.extend(
        [
            "",
            "Heuristic definitions are documented in `docs/paper_support/comparison-workflow.md`.",
        ]
    )
    markdown_path.write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "mode",
                "total_tasks",
                "intent_captured_true",
                "policy_checked_true",
                "execution_verified_true",
                "receipt_exported_true",
                "overall_pass_or_policy_blocked",
                "average_explicitness",
                "average_replayability",
                "average_tamper_sensitivity",
                "average_audit_boundedness",
                "average_integration_surface",
            ],
        )
        writer.writeheader()
        writer.writerows(modes)

    write_json(json_path, output)
