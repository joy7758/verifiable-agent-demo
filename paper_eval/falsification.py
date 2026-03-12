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
        "source_status": "pass",
    },
    {
        "name": "missing_policy",
        "description": "Remove the persisted governance decision while preserving integrity and receipt bindings.",
        "targeted_failure": "policy_checked",
        "source_status": "pass",
    },
    {
        "name": "forged_receipt",
        "description": "Forge one receipt artifact digest while leaving the trace integrity chain untouched.",
        "targeted_failure": "receipt_exported",
        "source_status": "pass",
    },
    {
        "name": "payload_tamper",
        "description": "Modify the executed result payload after export without updating the stored digests.",
        "targeted_failure": "execution_verified",
        "source_status": "pass",
    },
    {
        "name": "false_tamper_claim",
        "description": "Declare a tamper outcome without an independently corroborated digest mismatch.",
        "targeted_failure": "tamper_claim_rejected",
        "source_status": "pass",
    },
    {
        "name": "cross_run_replay_mismatch",
        "description": "Replace the trace with one from a different review-passing run while rebinding the receipt to the current bundle.",
        "targeted_failure": "execution_verified",
        "source_status": "pass",
    },
    {
        "name": "cross_bundle_receipt_swap",
        "description": "Swap in a receipt from a different review-passing bundle without updating its artifact digests.",
        "targeted_failure": "receipt_exported",
        "source_status": "pass",
    },
    {
        "name": "policy_bypass_claim",
        "description": "Rewrite a policy-blocked bundle to claim successful completion while leaving the blocked policy decision in place.",
        "targeted_failure": "policy_result_consistency",
        "source_status": "policy_blocked",
    },
]


def run_falsification_checks(source_mode: str = "evidence_chain") -> dict[str, Any]:
    tasks = load_tasks()
    validation = validate_task_suite(tasks)
    if not validation["valid"]:
        raise ValueError(f"task suite is invalid: {validation['errors']}")

    base_dir = reset_directory(FALSIFICATION_DIR)
    per_bundle: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    scenario_sources: dict[str, list[dict[str, str]]] = {}

    for scenario in SCENARIOS:
        source_runs = scenario_sources.setdefault(
            scenario["source_status"], collect_source_runs(source_mode, {scenario["source_status"]})
        )
        scenario_rows: list[dict[str, Any]] = []
        for source in source_runs:
            run_dir = materialize_scenario(base_dir, scenario, source, source_runs)
            review = review_run_directory(run_dir)
            row = {
                "task_id": source["task_id"],
                "source_mode": source_mode,
                "scenario": scenario["name"],
                "source_status": source["review_status"],
                "review": review,
            }
            scenario_rows.append(row)
            per_bundle.append(row)
        summaries.append(summarize_scenario(scenario, scenario_rows))

    output = {
        "title": "Falsification Checks",
        "description": (
            "Negative-control bundles derived from review-passing and policy-blocked evidence-chain runs. Each scenario "
            "preserves or corrupts specific bundle properties to test whether the independent review contract can reject "
            "malformed evidence."
        ),
        "source_mode": source_mode,
        "source_status_counts": {key: len(value) for key, value in scenario_sources.items()},
        "scenarios": summaries,
        "per_bundle": per_bundle,
    }
    write_outputs(output)
    return output


def collect_source_runs(source_mode: str, allowed_statuses: set[str]) -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    for task in load_tasks():
        run_dir = RUNS_DIR / task["task_id"] / source_mode
        review = review_run_directory(run_dir)
        if review["overall_status"] in allowed_statuses:
            sources.append(
                {
                    "task_id": task["task_id"],
                    "run_dir": str(run_dir.resolve()),
                    "review_status": review["overall_status"],
                }
            )
    return sources


def materialize_scenario(
    base_dir: Path,
    scenario: dict[str, str],
    source: dict[str, str],
    scenario_sources: list[dict[str, str]],
) -> Path:
    source_dir = Path(source["run_dir"])
    destination = reset_directory(base_dir / source["task_id"] / scenario["name"])
    payloads = {name: load_json(source_dir / name) for name in EXPORTED_FILES}
    partner_payloads = None
    if scenario["name"] in {"cross_run_replay_mismatch", "cross_bundle_receipt_swap"}:
        partner = select_partner_source(source, scenario_sources)
        partner_dir = Path(partner["run_dir"])
        partner_payloads = {name: load_json(partner_dir / name) for name in EXPORTED_FILES}
    payloads = apply_scenario(payloads, scenario, source["task_id"], partner_payloads=partner_payloads)
    for name, payload in payloads.items():
        write_json(destination / name, payload)
    return destination


def apply_scenario(
    payloads: dict[str, Any],
    scenario: dict[str, str],
    task_id: str,
    *,
    partner_payloads: dict[str, Any] | None = None,
) -> dict[str, Any]:
    mutated = deepcopy(payloads)
    scenario_name = scenario["name"]
    scenario_mode = f"falsified_{scenario_name}"
    scenario_run_id = f"{task_id}-{scenario_mode}"
    set_bundle_identity(mutated, task_id, scenario_mode, scenario_run_id)

    if scenario_name == "missing_intent":
        mutated["intent.json"]["intent_captured"] = False
        mutated["intent.json"]["intent"] = None
        mutated["intent.json"].setdefault("notes", []).append("Falsification check removed the explicit intent object.")
        rebind_bundle(mutated)
        return mutated

    if scenario_name == "missing_policy":
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

    if scenario_name == "forged_receipt":
        rebind_bundle(mutated)
        artifacts = mutated["receipt.json"]["audit_receipt"]["artifacts"]
        artifacts[0]["sha256"] = mutate_digest_string(artifacts[0]["sha256"])
        mutated["receipt.json"]["audit_receipt"]["notes"].append("Falsification check forged one receipt digest.")
        return mutated

    if scenario_name == "payload_tamper":
        rebind_bundle(mutated)
        mutated["result.json"]["outputs"]["summary"] = "Tampered after export without updating trace or receipt digests."
        mutated["result.json"].setdefault("notes", []).append("Falsification check modified the result payload after export.")
        return mutated

    if scenario_name == "false_tamper_claim":
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

    if scenario_name == "cross_run_replay_mismatch":
        if partner_payloads is None:
            raise ValueError("cross_run_replay_mismatch requires a partner bundle")
        mutated["trace.json"] = deepcopy(partner_payloads["trace.json"])
        set_bundle_identity(mutated, task_id, scenario_mode, scenario_run_id)
        mutated["trace.json"]["execution"]["deterministic_seed"] = partner_payloads["trace.json"]["execution"]["deterministic_seed"]
        refresh_receipt_artifacts(mutated)
        mutated["receipt.json"]["audit_receipt"]["notes"].append(
            "Falsification check replaced the trace with one from a different run without rebinding its integrity chain."
        )
        return mutated

    if scenario_name == "cross_bundle_receipt_swap":
        if partner_payloads is None:
            raise ValueError("cross_bundle_receipt_swap requires a partner bundle")
        rebind_bundle(mutated)
        mutated["receipt.json"] = deepcopy(partner_payloads["receipt.json"])
        set_bundle_identity(mutated, task_id, scenario_mode, scenario_run_id)
        mutated["receipt.json"]["audit_receipt"].setdefault("notes", []).append(
            "Falsification check swapped in a receipt from a different run without updating artifact digests."
        )
        return mutated

    if scenario_name == "policy_bypass_claim":
        mutated["result.json"]["status"] = "completed"
        mutated["result.json"]["goal_satisfied"] = True
        mutated["result.json"]["outputs"]["summary"] = "Claimed successful completion despite the persisted blocked policy decision."
        simulated_response = mutated["result.json"]["outputs"].get("simulated_response") or {}
        if simulated_response:
            simulated_response["status"] = "completed"
        mutated["trace.json"]["execution"]["performed"] = True
        mutated["trace.json"]["integrity"]["verification_status"] = "verified"
        for step in mutated["trace.json"].get("executed_steps") or []:
            if step.get("step") == "execution_skipped":
                step["step"] = "execution_performed"
                step["detail"] = simulated_response.get("requested_tool") or "policy bypass claim"
        receipt_integrity = mutated["receipt.json"]["audit_receipt"]["integrity_summary"]
        receipt_integrity["execution_verified"] = True
        receipt_integrity["verification_status"] = "verified"
        receipt_integrity["tamper_detected"] = False
        mutated["receipt.json"]["audit_receipt"]["notes"].append(
            "Falsification check rewrote a blocked bundle to claim successful execution without changing the policy decision."
        )
        rebind_bundle(mutated)
        return mutated

    raise ValueError(f"unknown falsification scenario: {scenario_name}")


def set_bundle_identity(payloads: dict[str, Any], task_id: str, mode: str, run_id: str) -> None:
    for name, payload in payloads.items():
        payload["task_id"] = task_id
        payload["mode"] = mode
        payload["run_id"] = run_id
        if name == "result.json":
            payload["outputs"]["artifact_directory"] = str(FALSIFICATION_DIR / task_id / mode)
        if name == "trace.json":
            execution = payload.get("execution") or {}
            if "deterministic_seed" in execution:
                execution["deterministic_seed"] = run_id


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
    refresh_receipt_artifacts(payloads, subject_digests=subject_digests, trace_digest=trace_digest)


def refresh_receipt_artifacts(
    payloads: dict[str, Any],
    *,
    subject_digests: dict[str, str] | None = None,
    trace_digest: str | None = None,
) -> None:
    if subject_digests is None:
        subject_digests = {
            "intent.json": sha256_digest(payloads["intent.json"]),
            "action.json": sha256_digest(payloads["action.json"]),
            "result.json": sha256_digest(payloads["result.json"]),
        }
    if trace_digest is None:
        trace_digest = sha256_digest(payloads["trace.json"])
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


def select_partner_source(source: dict[str, str], scenario_sources: list[dict[str, str]]) -> dict[str, str]:
    ordered = sorted(scenario_sources, key=lambda item: item["task_id"])
    if len(ordered) < 2:
        raise ValueError("partnered falsification scenarios require at least two source bundles")
    index = next(idx for idx, item in enumerate(ordered) if item["task_id"] == source["task_id"])
    return ordered[(index + 1) % len(ordered)]


def summarize_scenario(scenario: dict[str, str], rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    summary = {
        "scenario": scenario["name"],
        "description": scenario["description"],
        "targeted_failure": scenario["targeted_failure"],
        "source_status": scenario["source_status"],
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
        "Source bundles by status:",
        "",
        *[f"- `{status}`: {count} source `{output['source_mode']}` runs." for status, count in sorted(output["source_status_counts"].items())],
        "",
        "| scenario | source_status | total_bundles | detected_bundles | detection_rate | intent_captured_true | policy_checked_true | execution_verified_true | receipt_exported_true |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in output["scenarios"]:
        lines.append(
            "| {scenario} | {source_status} | {total_bundles} | {detected_bundles} | {detection_rate} | {intent_captured_true} | "
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
                "source_status",
                "total_bundles",
                "detected_bundles",
                "detection_rate",
                "intent_captured_true",
                "policy_checked_true",
                "execution_verified_true",
                "receipt_exported_true",
                "status_counts",
            ],
            lineterminator="\n",
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
