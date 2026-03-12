"""Negative-control generation for exported run bundles."""

from __future__ import annotations

import csv
from copy import deepcopy
from pathlib import Path
from typing import Any

from .common import EXPORTED_FILES, FALSIFICATION_DIR, METRICS_DIR, PAPER_DOCS_DIR, RUNS_DIR, load_json, reset_directory, sha256_digest, write_json
from .review import review_run_directory
from .runner import build_checkpoints
from .suite import load_tasks, validate_task_suite

SCENARIOS: list[dict[str, str]] = [
    {
        "name": "missing_intent",
        "description": "Remove the explicit intent object while preserving all downstream digests and receipt artifacts.",
        "targeted_failure": "intent_captured",
    },
    {
        "name": "missing_policy",
        "description": "Remove the persisted governance decision while preserving integrity and receipt bindings.",
        "targeted_failure": "policy_checked",
    },
    {
        "name": "forged_receipt",
        "description": "Forge one receipt artifact digest while leaving the trace integrity chain untouched.",
        "targeted_failure": "receipt_exported",
    },
    {
        "name": "payload_tamper",
        "description": "Modify the executed result payload after export without updating the stored digests.",
        "targeted_failure": "execution_verified",
    },
    {
        "name": "false_tamper_claim",
        "description": "Declare a tamper outcome without an independently corroborated digest mismatch.",
        "targeted_failure": "tamper_claim_rejected",
    },
]


def run_falsification_checks(source_mode: str = "evidence_chain") -> dict[str, Any]:
    tasks = load_tasks()
    validation = validate_task_suite(tasks)
    if not validation["valid"]:
        raise ValueError(f"task suite is invalid: {validation['errors']}")

    source_runs = collect_review_passing_runs(source_mode)
    base_dir = reset_directory(FALSIFICATION_DIR)
    per_bundle: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []

    for scenario in SCENARIOS:
        scenario_rows: list[dict[str, Any]] = []
        for source in source_runs:
            run_dir = materialize_scenario(base_dir, scenario["name"], source)
            review = review_run_directory(run_dir)
            row = {
                "task_id": source["task_id"],
                "source_mode": source_mode,
                "scenario": scenario["name"],
                "review": review,
            }
            scenario_rows.append(row)
            per_bundle.append(row)
        summaries.append(summarize_scenario(scenario, scenario_rows))

    output = {
        "title": "Falsification Checks",
        "description": (
            "Negative-control bundles derived from review-passing evidence-chain runs. Each scenario preserves or corrupts "
            "specific bundle properties to test whether the independent review contract can reject malformed evidence."
        ),
        "source_mode": source_mode,
        "source_bundle_count": len(source_runs),
        "scenarios": summaries,
        "per_bundle": per_bundle,
    }
    write_outputs(output)
    return output


def collect_review_passing_runs(source_mode: str) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    for task in load_tasks():
        run_dir = RUNS_DIR / task["task_id"] / source_mode
        review = review_run_directory(run_dir)
        if review["overall_status"] == "pass":
            sources.append({"task_id": task["task_id"], "run_dir": str(run_dir.resolve())})
    return sources


def materialize_scenario(base_dir: Path, scenario: str, source: dict[str, str]) -> Path:
    source_dir = Path(source["run_dir"])
    destination = reset_directory(base_dir / source["task_id"] / scenario)
    payloads = {name: load_json(source_dir / name) for name in EXPORTED_FILES}
    payloads = apply_scenario(payloads, scenario, source["task_id"])
    for name, payload in payloads.items():
        write_json(destination / name, payload)
    return destination


def apply_scenario(payloads: dict[str, Any], scenario: str, task_id: str) -> dict[str, Any]:
    mutated = deepcopy(payloads)
    scenario_mode = f"falsified_{scenario}"
    scenario_run_id = f"{task_id}-{scenario_mode}"
    set_bundle_identity(mutated, task_id, scenario_mode, scenario_run_id)

    if scenario == "missing_intent":
        mutated["intent.json"]["intent_captured"] = False
        mutated["intent.json"]["intent"] = None
        mutated["intent.json"].setdefault("notes", []).append("Falsification check removed the explicit intent object.")
        rebind_bundle(mutated)
        return mutated

    if scenario == "missing_policy":
        mutated["action.json"]["authorization_state"] = "untracked"
        mutated["action.json"]["policy"] = {
            "checked": False,
            "checkpoint_id": "not_recorded",
            "budget_policy": {"status": "not_recorded"},
            "approval_policy": {"status": "not_recorded"},
            "decision": {"status": "not_recorded", "reasons": ["Falsification check removed the persisted policy decision."]},
        }
        rebind_bundle(mutated)
        return mutated

    if scenario == "forged_receipt":
        rebind_bundle(mutated)
        artifacts = mutated["receipt.json"]["audit_receipt"]["artifacts"]
        artifacts[0]["sha256"] = mutate_digest_string(artifacts[0]["sha256"])
        mutated["receipt.json"]["audit_receipt"]["notes"].append("Falsification check forged one receipt digest.")
        return mutated

    if scenario == "payload_tamper":
        rebind_bundle(mutated)
        mutated["result.json"]["outputs"]["summary"] = "Tampered after export without updating trace or receipt digests."
        mutated["result.json"].setdefault("notes", []).append("Falsification check modified the result payload after export.")
        return mutated

    if scenario == "false_tamper_claim":
        mutated["result.json"]["status"] = "tamper_detected"
        mutated["result.json"]["goal_satisfied"] = False
        mutated["result.json"]["outputs"]["summary"] = "Declared a tamper condition without a corroborating digest mismatch."
        mutated["trace.json"]["integrity"]["verification_status"] = "tamper_detected"
        mutated["receipt.json"]["audit_receipt"]["integrity_summary"]["execution_verified"] = False
        mutated["receipt.json"]["audit_receipt"]["integrity_summary"]["verification_status"] = "tamper_detected"
        mutated["receipt.json"]["audit_receipt"]["integrity_summary"]["tamper_detected"] = True
        mutated["receipt.json"]["audit_receipt"]["notes"].append("Falsification check declared tamper without altering expected digests.")
        rebind_bundle(mutated, tamper_claim_without_mismatch=True)
        return mutated

    raise ValueError(f"unknown falsification scenario: {scenario}")


def set_bundle_identity(payloads: dict[str, Any], task_id: str, mode: str, run_id: str) -> None:
    for name, payload in payloads.items():
        payload["task_id"] = task_id
        payload["mode"] = mode
        payload["run_id"] = run_id
        if name == "result.json":
            payload["outputs"]["artifact_directory"] = str(FALSIFICATION_DIR / task_id / mode)


def rebind_bundle(payloads: dict[str, Any], *, tamper_claim_without_mismatch: bool = False) -> None:
    subject_digests = {
        "intent.json": sha256_digest(payloads["intent.json"]),
        "action.json": sha256_digest(payloads["action.json"]),
        "result.json": sha256_digest(payloads["result.json"]),
    }

    trace = payloads["trace.json"]
    integrity = trace.get("integrity") or {}
    if integrity.get("checked"):
        integrity["subject_digests"] = dict(subject_digests)
        if integrity.get("verification_status") == "tamper_detected" and not tamper_claim_without_mismatch:
            expected = dict(subject_digests)
            expected["result.json"] = mutate_digest_string(expected["result.json"])
            integrity["expected_digests"] = expected
        else:
            integrity["expected_digests"] = dict(subject_digests)
        integrity["checkpoints"] = build_checkpoints(trace["run_id"], list(subject_digests.values()))

    trace_digest = sha256_digest(trace)
    receipt = payloads["receipt.json"]
    if receipt.get("receipt_exported"):
        receipt["audit_receipt"]["artifacts"] = [
            {"path": "intent.json", "role": "intent", "sha256": subject_digests["intent.json"]},
            {"path": "action.json", "role": "action", "sha256": subject_digests["action.json"]},
            {"path": "result.json", "role": "result", "sha256": subject_digests["result.json"]},
            {"path": "trace.json", "role": "trace", "sha256": trace_digest},
        ]
        receipt["audit_receipt"]["boundedness"]["exported_files_count"] = len(EXPORTED_FILES)
        receipt["audit_receipt"]["boundedness"]["allowed_files"] = EXPORTED_FILES
        receipt["audit_receipt"]["boundedness"]["artifact_digest_count"] = 4


def summarize_scenario(scenario: dict[str, str], rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    summary = {
        "scenario": scenario["name"],
        "description": scenario["description"],
        "targeted_failure": scenario["targeted_failure"],
        "total_bundles": total,
        "detected_bundles": 0,
        "detection_rate": 0.0,
        "intent_captured_true": 0,
        "policy_checked_true": 0,
        "execution_verified_true": 0,
        "receipt_exported_true": 0,
        "status_counts": {},
    }
    for row in rows:
        review = row["review"]
        if review["overall_status"] != "pass":
            summary["detected_bundles"] += 1
        summary["intent_captured_true"] += int(review["intent_captured"])
        summary["policy_checked_true"] += int(review["policy_checked"])
        summary["execution_verified_true"] += int(review["execution_verified"])
        summary["receipt_exported_true"] += int(review["receipt_exported"])
        status = review["overall_status"]
        summary["status_counts"][status] = summary["status_counts"].get(status, 0) + 1
    summary["detection_rate"] = round(summary["detected_bundles"] / (total or 1), 2)
    return summary


def write_outputs(output: dict[str, Any]) -> None:
    PAPER_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    markdown_path = PAPER_DOCS_DIR / "falsification-summary.md"
    csv_path = PAPER_DOCS_DIR / "falsification-summary.csv"
    json_path = METRICS_DIR / "falsification-summary.json"

    lines = [
        "# Falsification Summary",
        "",
        output["description"],
        "",
        f"Source bundles: {output['source_bundle_count']} review-passing `{output['source_mode']}` runs.",
        "",
        "| scenario | total_bundles | detected_bundles | detection_rate | intent_captured_true | policy_checked_true | execution_verified_true | receipt_exported_true |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in output["scenarios"]:
        lines.append(
            "| {scenario} | {total_bundles} | {detected_bundles} | {detection_rate} | {intent_captured_true} | "
            "{policy_checked_true} | {execution_verified_true} | {receipt_exported_true} |".format(**row)
        )
    lines.extend(
        [
            "",
            "Scenario definitions are documented in `docs/paper_support/falsification-workflow.md`.",
        ]
    )
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "scenario",
                "description",
                "targeted_failure",
                "total_bundles",
                "detected_bundles",
                "detection_rate",
                "intent_captured_true",
                "policy_checked_true",
                "execution_verified_true",
                "receipt_exported_true",
                "status_counts",
            ],
        )
        writer.writeheader()
        for row in output["scenarios"]:
            flat = dict(row)
            flat["status_counts"] = "; ".join(f"{key}={value}" for key, value in sorted(row["status_counts"].items()))
            writer.writerow(flat)

    write_json(json_path, output)


def mutate_digest_string(digest: str) -> str:
    prefix, value = digest.split(":", 1)
    replacement = "0" if value[0] != "0" else "1"
    return f"{prefix}:{replacement}{value[1:]}"
