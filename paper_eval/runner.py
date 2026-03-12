"""Deterministic baseline and evidence-chain runners for the paper task suite."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from .common import EXPORTED_FILES, RUNS_DIR, SCHEMA_VERSION, mutate_digest, relative_to_root, reset_directory, sha256_digest, stable_timestamp, write_json
from .suite import find_task, load_tasks, validate_task_suite


def run_suite(mode: str, task_id: str | None = None) -> dict[str, Any]:
    tasks = load_tasks()
    validation = validate_task_suite(tasks)
    if not validation["valid"]:
        raise ValueError(f"task suite is invalid: {validation['errors']}")

    selected_tasks = [find_task(task_id, tasks)] if task_id else tasks
    run_dirs = [run_task(task, mode) for task in selected_tasks]
    return {
        "mode": mode,
        "task_count": len(run_dirs),
        "run_directories": [relative_to_root(path) for path in run_dirs],
    }


def run_task(task: dict[str, Any], mode: str) -> Path:
    if mode not in {"baseline", "evidence_chain"}:
        raise ValueError(f"unsupported mode: {mode}")

    task_id = task["task_id"]
    run_dir = reset_directory(RUNS_DIR / task_id / mode)
    context = build_run_context(task, mode, run_dir)
    policy = evaluate_policy(task, mode, context)
    status = determine_status(task, mode, policy)

    intent_payload = build_intent(task, mode, context)
    action_payload = build_action(task, mode, context, policy)
    result_payload = build_result(task, mode, context, policy, status)
    subject_digests = {
        "intent.json": sha256_digest(intent_payload),
        "action.json": sha256_digest(action_payload),
        "result.json": sha256_digest(result_payload),
    }
    trace_payload = build_trace(task, mode, context, policy, status, subject_digests)
    subject_digests["trace.json"] = sha256_digest(trace_payload)
    receipt_payload = build_receipt(task, mode, context, policy, status, subject_digests)

    payloads = {
        "intent.json": intent_payload,
        "action.json": action_payload,
        "result.json": result_payload,
        "trace.json": trace_payload,
        "receipt.json": receipt_payload,
    }
    for filename, payload in payloads.items():
        write_json(run_dir / filename, payload)

    return run_dir


def build_run_context(task: dict[str, Any], mode: str, run_dir: Path) -> dict[str, str]:
    task_id = task["task_id"]
    run_id = f"{task_id}-{mode}"
    return {
        "run_id": run_id,
        "task_id": task_id,
        "mode": mode,
        "run_dir": relative_to_root(run_dir),
        "persona_ref": "pop://personas/paper-eval-agent",
        "policy_checkpoint_ref": f"governor://paper-eval/checkpoints/{run_id}",
        "trace_ref": f"trace://paper-eval/{run_id}",
        "receipt_ref": f"aro://paper-eval/receipts/{run_id}",
    }


def evaluate_policy(task: dict[str, Any], mode: str, context: dict[str, str]) -> dict[str, Any]:
    budget_policy = task["budget_policy"]
    approval_policy = task["approval_policy"]
    input_payload = task["input_payload"]

    estimated_cost = float(input_payload.get("estimated_cost_usd", 0.0))
    estimated_tokens = int(input_payload.get("estimated_tokens", 0))
    usd_limit = budget_policy.get("usd_limit")
    token_limit = budget_policy.get("token_limit")
    cost_within_limit = usd_limit is None or estimated_cost <= float(usd_limit)
    tokens_within_limit = token_limit is None or estimated_tokens <= int(token_limit)
    approval_satisfied = (not approval_policy.get("requires_approval")) or bool(approval_policy.get("approval_token"))

    if mode == "baseline":
        status = "unchecked"
        reasons = ["baseline mode exports a trace-only bundle without a persisted governance checkpoint"]
    elif not cost_within_limit or not tokens_within_limit:
        status = "blocked_budget"
        reasons = ["budget policy would be exceeded"]
    elif not approval_satisfied:
        status = "blocked_approval"
        reasons = ["approval token is required but missing"]
    else:
        status = "approved"
        reasons = ["budget and approval checks passed"]

    return {
        "checked": mode == "evidence_chain",
        "checkpoint_id": context["policy_checkpoint_ref"],
        "status": status,
        "budget_within_limit": cost_within_limit and tokens_within_limit,
        "approval_satisfied": approval_satisfied,
        "estimated_cost_usd": estimated_cost,
        "estimated_tokens": estimated_tokens,
        "reasons": reasons,
        "budget_policy": budget_policy,
        "approval_policy": approval_policy,
    }


def determine_status(task: dict[str, Any], mode: str, policy: dict[str, Any]) -> str:
    if mode == "evidence_chain" and policy["status"] in {"blocked_budget", "blocked_approval"}:
        return policy["status"]
    if task["tamper_case"] and mode == "evidence_chain":
        return "tamper_detected"
    return "completed"


def build_intent(task: dict[str, Any], mode: str, context: dict[str, str]) -> dict[str, Any]:
    captured = mode == "evidence_chain"
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "file_type": "intent",
        "task_id": context["task_id"],
        "mode": context["mode"],
        "run_id": context["run_id"],
        "intent_captured": captured,
        "intent": None,
        "authorization_scope": {
            "budget_policy_ref": task["budget_policy"]["policy_id"],
            "approval_policy_ref": task["approval_policy"]["approval_scope"],
            "expected_exports": EXPORTED_FILES,
        },
        "notes": [],
    }
    if captured:
        payload["intent"] = {
            "category": task["category"],
            "title": task["title"],
            "goal": task["goal"],
            "actor_ref": context["persona_ref"],
            "target_ref": f"runtime://paper-eval/tasks/{context['task_id']}",
            "input_payload_snapshot": task["input_payload"],
            "expected_artifacts": task["expected_artifacts"],
        }
        payload["notes"].append("Explicit intent object persisted before execution.")
    else:
        payload["notes"].append("Baseline mode does not persist an explicit intent object.")
    return payload


def build_action(task: dict[str, Any], mode: str, context: dict[str, str], policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "file_type": "action",
        "task_id": context["task_id"],
        "mode": context["mode"],
        "run_id": context["run_id"],
        "requested_action": {
            "name": task["input_payload"]["operation"],
            "summary": task["title"],
            "tool_ref": f"runtime://paper-eval/{task['input_payload']['requested_tool']}",
            "parameters": task["input_payload"],
            "side_effect_class": task["input_payload"]["side_effect_class"],
        },
        "authorization_state": policy["status"],
        "policy": {
            "checked": policy["checked"],
            "checkpoint_id": policy["checkpoint_id"],
            "budget_policy": policy["budget_policy"],
            "approval_policy": policy["approval_policy"],
            "decision": {
                "status": policy["status"],
                "budget_within_limit": policy["budget_within_limit"],
                "approval_satisfied": policy["approval_satisfied"],
                "estimated_cost_usd": policy["estimated_cost_usd"],
                "estimated_tokens": policy["estimated_tokens"],
                "reasons": policy["reasons"],
            },
        },
    }


def build_result(
    task: dict[str, Any],
    mode: str,
    context: dict[str, str],
    policy: dict[str, Any],
    status: str,
) -> dict[str, Any]:
    summary = {
        "completed": f"Completed deterministic local run for {task['title']}.",
        "blocked_budget": f"Blocked by budget policy before execution for {task['title']}.",
        "blocked_approval": f"Blocked by approval policy before execution for {task['title']}.",
        "tamper_detected": f"Detected a tamper condition while verifying {task['title']}.",
    }[status]

    return {
        "schema_version": SCHEMA_VERSION,
        "file_type": "result",
        "task_id": context["task_id"],
        "mode": context["mode"],
        "run_id": context["run_id"],
        "status": status,
        "goal_satisfied": status == "completed",
        "outputs": {
            "summary": summary,
            "simulated_response": build_simulated_response(task, status),
            "artifact_directory": context["run_dir"],
            "expected_artifacts": EXPORTED_FILES,
        },
        "policy_outcome_ref": "action.json#/policy/decision",
        "execution_trace_ref": "trace.json",
        "evidence_refs": EXPORTED_FILES,
        "notes": policy["reasons"],
    }


def build_simulated_response(task: dict[str, Any], status: str) -> dict[str, Any]:
    input_payload = task["input_payload"]
    payload = {
        "category": task["category"],
        "operation": input_payload["operation"],
        "requested_tool": input_payload["requested_tool"],
        "target": input_payload.get("target"),
        "status": status,
    }
    if "expected_answer" in input_payload:
        payload["answer"] = input_payload["expected_answer"]
    if "arguments" in input_payload:
        payload["arguments"] = input_payload["arguments"]
    if "estimated_cost_usd" in input_payload:
        payload["estimated_cost_usd"] = input_payload["estimated_cost_usd"]
    if "estimated_tokens" in input_payload:
        payload["estimated_tokens"] = input_payload["estimated_tokens"]
    return payload


def build_trace(
    task: dict[str, Any],
    mode: str,
    context: dict[str, str],
    policy: dict[str, Any],
    status: str,
    subject_digests: dict[str, str],
) -> dict[str, Any]:
    performed = status in {"completed", "tamper_detected"} and not (
        mode == "evidence_chain" and policy["status"] in {"blocked_budget", "blocked_approval"}
    )
    integrity = build_integrity(task, mode, status, policy, subject_digests, context["run_id"])

    steps = [
        {"step": "task_loaded", "at": stable_timestamp(context["task_id"], mode, 0), "detail": task["title"]},
        {
            "step": "policy_evaluated",
            "at": stable_timestamp(context["task_id"], mode, 1),
            "detail": policy["status"],
        },
        {
            "step": "action_processed",
            "at": stable_timestamp(context["task_id"], mode, 2),
            "detail": task["input_payload"]["operation"],
        },
    ]
    if performed:
        steps.append(
            {
                "step": "execution_performed",
                "at": stable_timestamp(context["task_id"], mode, 3),
                "detail": task["input_payload"]["requested_tool"],
            }
        )
    else:
        steps.append(
            {
                "step": "execution_skipped",
                "at": stable_timestamp(context["task_id"], mode, 3),
                "detail": policy["status"],
            }
        )
    steps.append(
        {
            "step": "evidence_written",
            "at": stable_timestamp(context["task_id"], mode, 4),
            "detail": "receipt.json" if mode == "evidence_chain" else "trace-only placeholders",
        }
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "file_type": "trace",
        "task_id": context["task_id"],
        "mode": context["mode"],
        "run_id": context["run_id"],
        "trace_style": "trace_only" if mode == "baseline" else "evidence_chain",
        "executed_steps": steps,
        "execution": {
            "attempted": True,
            "performed": performed,
            "tool_ref": f"runtime://paper-eval/{task['input_payload']['requested_tool']}",
            "deterministic_seed": context["run_id"],
            "started_at": stable_timestamp(context["task_id"], mode, 0),
            "finished_at": stable_timestamp(context["task_id"], mode, 5),
        },
        "integrity": integrity,
        "evidence_produced": [
            "action.json",
            "result.json",
            "trace.json",
        ]
        if mode == "baseline"
        else EXPORTED_FILES,
    }


def build_integrity(
    task: dict[str, Any],
    mode: str,
    status: str,
    policy: dict[str, Any],
    subject_digests: dict[str, str],
    run_id: str,
) -> dict[str, Any]:
    if mode == "baseline":
        return {
            "checked": False,
            "method": "none",
            "verification_status": "not_performed",
            "subject_digests": {},
            "expected_digests": {},
            "checkpoints": [],
            "notes": ["Baseline mode does not emit execution-integrity evidence."],
        }

    expected_digests = dict(subject_digests)
    tamper_case = task["tamper_case"]
    if tamper_case:
        target_name = f"{tamper_case['tamper_target']}.json"
        expected_digests[target_name] = mutate_digest(subject_digests[target_name])

    checkpoints = build_checkpoints(run_id, list(subject_digests.values()))
    if policy["status"] in {"blocked_budget", "blocked_approval"}:
        verification_status = "skipped_by_policy"
    elif tamper_case:
        verification_status = "tamper_detected"
    else:
        verification_status = "verified"

    return {
        "checked": True,
        "method": "sha256-checkpoint-chain",
        "verification_status": verification_status,
        "subject_digests": subject_digests,
        "expected_digests": expected_digests,
        "checkpoints": checkpoints,
        "notes": [] if not tamper_case else [tamper_case["description"]],
    }


def build_checkpoints(run_id: str, digests: list[str]) -> list[str]:
    checkpoints: list[str] = []
    accumulator = run_id.encode("utf-8")
    for digest in digests:
        accumulator = accumulator + digest.encode("utf-8")
        checkpoints.append(sha256_digest({"checkpoint_input": accumulator.hex()}))
    return checkpoints


def build_receipt(
    task: dict[str, Any],
    mode: str,
    context: dict[str, str],
    policy: dict[str, Any],
    status: str,
    subject_digests: dict[str, str],
) -> dict[str, Any]:
    exported = mode == "evidence_chain"
    artifacts = []
    if exported:
        for name in ("intent.json", "action.json", "result.json", "trace.json"):
            artifacts.append(
                {
                    "path": name,
                    "role": name.removesuffix(".json"),
                    "sha256": subject_digests[name],
                }
            )

    verification_status = "not_performed"
    if exported:
        if policy["status"] in {"blocked_budget", "blocked_approval"}:
            verification_status = "skipped_by_policy"
        elif task["tamper_case"]:
            verification_status = "tamper_detected"
        else:
            verification_status = "verified"

    return {
        "schema_version": SCHEMA_VERSION,
        "file_type": "receipt",
        "task_id": context["task_id"],
        "mode": context["mode"],
        "run_id": context["run_id"],
        "receipt_exported": exported,
        "audit_receipt": {
            "profile": "paper-eval-bounded-receipt-v1",
            "status": "exported" if exported else "not_exported",
            "scope": "bounded_run_bundle",
            "artifacts": artifacts,
            "questions_answered": {}
            if not exported
            else {
                "what_was_intended": "intent.json#/intent",
                "what_was_authorized": "action.json#/policy/decision",
                "what_was_executed": "trace.json#/execution",
                "what_evidence_was_produced": "receipt.json#/audit_receipt/artifacts",
            },
            "boundedness": {
                "exported_files_count": len(EXPORTED_FILES),
                "allowed_files": EXPORTED_FILES,
                "artifact_digest_count": len(artifacts),
            },
            "integrity_summary": {
                "policy_checked": policy["checked"],
                "execution_verified": verification_status == "verified",
                "verification_status": verification_status,
                "tamper_detected": status == "tamper_detected",
            },
            "notes": []
            if exported
            else ["Baseline mode leaves receipt export as an empty placeholder for file-shape parity."],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the deterministic paper evaluation task suite.")
    parser.add_argument("--mode", required=True, choices=["baseline", "evidence_chain"])
    parser.add_argument("--task-id", help="Optional single task id to run.")
    args = parser.parse_args()

    summary = run_suite(mode=args.mode, task_id=args.task_id)
    print(summary)


if __name__ == "__main__":
    main()
