"""Deterministic baseline and evidence-chain runners for the paper task suite."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .common import EXPORTED_FILES, ROOT_DIR, RUNS_DIR, SCHEMA_VERSION, mutate_digest, relative_to_root, reset_directory, sha256_digest, stable_timestamp, write_json
from .modes import get_mode_profile, list_modes
from .suite import find_task, load_tasks, validate_task_suite


def run_suite(mode: str, task_id: str | None = None) -> dict[str, Any]:
    profile = get_mode_profile(mode)
    tasks = load_tasks()
    validation = validate_task_suite(tasks)
    if not validation["valid"]:
        raise ValueError(f"task suite is invalid: {validation['errors']}")

    selected_tasks = [find_task(task_id, tasks)] if task_id else tasks
    run_dirs = [run_task(task, profile.name) for task in selected_tasks]
    return {
        "mode": profile.name,
        "task_count": len(run_dirs),
        "run_directories": [relative_to_root(path) for path in run_dirs],
    }


def run_task(task: dict[str, Any], mode: str) -> Path:
    profile = get_mode_profile(mode)
    task_id = task["task_id"]
    run_dir = reset_directory(RUNS_DIR / task_id / mode)
    context = build_run_context(task, profile.name, run_dir)
    policy = evaluate_policy(task, profile.name, context)
    status = determine_status(task, profile.name, policy)

    intent_payload = build_intent(task, profile.name, context)
    action_payload = build_action(task, profile.name, context, policy)
    result_payload = build_result(task, profile.name, context, policy, status)
    subject_digests = {
        "intent.json": sha256_digest(intent_payload),
        "action.json": sha256_digest(action_payload),
        "result.json": sha256_digest(result_payload),
    }
    trace_payload = build_trace(task, profile.name, context, policy, status, dict(subject_digests))
    receipt_subject_digests = dict(subject_digests)
    receipt_subject_digests["trace.json"] = sha256_digest(trace_payload)
    receipt_payload = build_receipt(task, profile.name, context, policy, status, receipt_subject_digests)

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


def build_run_context(task: dict[str, Any], mode: str, run_dir: Path) -> dict[str, Any]:
    task_id = task["task_id"]
    run_id = f"{task_id}-{mode}"
    profile = get_mode_profile(mode)
    context: dict[str, Any] = {
        "run_id": run_id,
        "task_id": task_id,
        "mode": mode,
        "run_dir": relative_to_root(run_dir),
        "persona_ref": "pop://personas/paper-eval-agent",
        "policy_checkpoint_ref": f"governor://paper-eval/checkpoints/{run_id}",
        "trace_ref": f"trace://paper-eval/{run_id}",
        "receipt_ref": f"aro://paper-eval/receipts/{run_id}",
        "framework_label": profile.framework_label,
    }
    if mode == "external_baseline":
        context["native_runtime"] = run_live_crewai_baseline(task)
    return context


def run_live_crewai_baseline(task: dict[str, Any]) -> dict[str, Any]:
    helper = ROOT_DIR / "scripts" / "crewai_live_baseline.py"
    venv_python = ROOT_DIR / "venv" / "bin" / "python"
    if not helper.exists():
        raise FileNotFoundError(f"missing CrewAI baseline helper: {helper}")
    if not venv_python.exists():
        raise FileNotFoundError(f"missing CrewAI runtime python: {venv_python}")

    completed = subprocess.run(
        [str(venv_python), str(helper)],
        input=json.dumps(task, sort_keys=True, ensure_ascii=False),
        text=True,
        capture_output=True,
        check=True,
        cwd=ROOT_DIR,
    )
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"CrewAI baseline helper returned invalid JSON: {completed.stdout}") from exc


def evaluate_policy(task: dict[str, Any], mode: str, context: dict[str, Any]) -> dict[str, Any]:
    profile = get_mode_profile(mode)
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

    if not profile.policy_checked:
        if mode == "external_baseline":
            status = "framework_default"
            reasons = ["Minimal live CrewAI execution logs do not persist governance checkpoints or budget decisions."]
        elif mode == "no_governance":
            status = "not_recorded"
            reasons = ["Governance layer is ablated in this mode, so policy is neither persisted nor enforced."]
        else:
            status = "unchecked"
            reasons = ["Baseline mode exports a trace-only bundle without a persisted governance checkpoint."]
    elif not cost_within_limit or not tokens_within_limit:
        status = "blocked_budget"
        reasons = ["Budget policy would be exceeded."]
    elif not approval_satisfied:
        status = "blocked_approval"
        reasons = ["Approval token is required but missing."]
    else:
        status = "approved"
        reasons = ["Budget and approval checks passed."]

    return {
        "checked": profile.policy_checked,
        "enforced": profile.policy_enforced,
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
    profile = get_mode_profile(mode)
    if profile.policy_enforced and policy["status"] in {"blocked_budget", "blocked_approval"}:
        return policy["status"]
    if task["tamper_case"] and profile.integrity_checked:
        return "tamper_detected"
    return "completed"


def build_intent(task: dict[str, Any], mode: str, context: dict[str, Any]) -> dict[str, Any]:
    profile = get_mode_profile(mode)
    captured = profile.intent_captured
    native_runtime = context.get("native_runtime", {})
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
        "notes": list(profile.notes),
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
    elif profile.carries_raw_task_snapshot:
        payload["intent"] = {
            "framework_task_prompt": native_runtime.get("task_description", task["title"]),
            "agent_role": native_runtime.get("agent_role", "research agent"),
            "input_payload_snapshot": task["input_payload"],
            "source": native_runtime.get("framework", profile.framework_label),
            "native_surface": native_runtime.get("native_surface", {}),
        }
        payload["notes"].append("Framework-native task configuration was captured from a live CrewAI run, but not as an explicit intent object.")
    else:
        payload["notes"].append("This mode does not persist an explicit intent object.")
    return payload


def build_action(task: dict[str, Any], mode: str, context: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    profile = get_mode_profile(mode)
    native_runtime = context.get("native_runtime", {})
    authorization_state = policy["status"]
    if not profile.policy_checked:
        authorization_state = {
            "baseline": "unchecked",
            "external_baseline": "framework_executed",
            "no_governance": "untracked",
        }.get(mode, policy["status"])

    policy_bundle: dict[str, Any] = {
        "checked": policy["checked"],
        "checkpoint_id": policy["checkpoint_id"] if profile.policy_visible else "not_recorded",
        "budget_policy": policy["budget_policy"] if profile.policy_visible else {"status": "not_recorded"},
        "approval_policy": policy["approval_policy"] if profile.policy_visible else {"status": "not_recorded"},
        "decision": {
            "status": policy["status"],
            "budget_within_limit": policy["budget_within_limit"],
            "approval_satisfied": policy["approval_satisfied"],
            "estimated_cost_usd": policy["estimated_cost_usd"],
            "estimated_tokens": policy["estimated_tokens"],
            "reasons": policy["reasons"],
        },
    }
    if not profile.policy_visible:
        policy_bundle["decision"] = {
            "status": policy["status"],
            "reasons": policy["reasons"],
        }

    requested_action = {
        "name": task["input_payload"]["operation"],
        "summary": task["title"],
        "tool_ref": f"runtime://paper-eval/{task['input_payload']['requested_tool']}",
        "parameters": task["input_payload"],
        "side_effect_class": task["input_payload"]["side_effect_class"],
    }
    if native_runtime:
        requested_action["framework_runtime"] = native_runtime.get("framework", profile.framework_label)

    return {
        "schema_version": SCHEMA_VERSION,
        "file_type": "action",
        "task_id": context["task_id"],
        "mode": context["mode"],
        "run_id": context["run_id"],
        "requested_action": requested_action,
        "authorization_state": authorization_state,
        "policy": policy_bundle,
    }


def build_result(
    task: dict[str, Any],
    mode: str,
    context: dict[str, Any],
    policy: dict[str, Any],
    status: str,
) -> dict[str, Any]:
    profile = get_mode_profile(mode)
    native_runtime = context.get("native_runtime", {})
    summary = {
        "completed": f"Completed deterministic local run for {task['title']}.",
        "blocked_budget": f"Blocked by budget policy before execution for {task['title']}.",
        "blocked_approval": f"Blocked by approval policy before execution for {task['title']}.",
        "tamper_detected": f"Detected a tamper condition while verifying {task['title']}.",
    }[status]

    outputs = {
        "summary": summary,
        "simulated_response": build_simulated_response(task, status),
        "artifact_directory": context["run_dir"],
        "expected_artifacts": EXPORTED_FILES,
        "runtime_surface": profile.framework_label,
    }
    if native_runtime:
        outputs["framework_result"] = native_runtime.get("result_text")

    return {
        "schema_version": SCHEMA_VERSION,
        "file_type": "result",
        "task_id": context["task_id"],
        "mode": context["mode"],
        "run_id": context["run_id"],
        "status": status,
        "goal_satisfied": status == "completed",
        "outputs": outputs,
        "policy_outcome_ref": "action.json#/policy/decision",
        "execution_trace_ref": "trace.json",
        "evidence_refs": EXPORTED_FILES,
        "notes": policy["reasons"] + list(profile.notes),
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
    context: dict[str, Any],
    policy: dict[str, Any],
    status: str,
    subject_digests: dict[str, str],
) -> dict[str, Any]:
    profile = get_mode_profile(mode)
    native_runtime = context.get("native_runtime", {})
    performed = status in {"completed", "tamper_detected"} and not (
        profile.policy_enforced and policy["status"] in {"blocked_budget", "blocked_approval"}
    )
    integrity = build_integrity(task, mode, status, policy, subject_digests, context["run_id"])

    if mode == "external_baseline":
        steps = build_external_baseline_steps(task, mode, context, status)
    else:
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
            "detail": "receipt.json" if profile.receipt_exported else f"{profile.trace_style} placeholders",
        }
    )

    execution_payload = {
        "attempted": True,
        "performed": performed,
        "tool_ref": f"runtime://paper-eval/{task['input_payload']['requested_tool']}",
        "deterministic_seed": context["run_id"],
        "started_at": stable_timestamp(context["task_id"], mode, 0),
        "finished_at": stable_timestamp(context["task_id"], mode, 5),
        "framework": native_runtime.get("framework", profile.framework_label),
    }
    if native_runtime:
        execution_payload["framework_live_run"] = bool(native_runtime.get("live_framework"))
        execution_payload["framework_result"] = native_runtime.get("result_text")

    return {
        "schema_version": SCHEMA_VERSION,
        "file_type": "trace",
        "task_id": context["task_id"],
        "mode": context["mode"],
        "run_id": context["run_id"],
        "trace_style": profile.trace_style,
        "executed_steps": steps,
        "execution": execution_payload,
        "integrity": integrity,
        "evidence_produced": EXPORTED_FILES if profile.receipt_exported else ["action.json", "result.json", "trace.json"],
    }


def build_integrity(
    task: dict[str, Any],
    mode: str,
    status: str,
    policy: dict[str, Any],
    subject_digests: dict[str, str],
    run_id: str,
) -> dict[str, Any]:
    profile = get_mode_profile(mode)
    if not profile.integrity_checked:
        return {
            "checked": False,
            "method": "none",
            "verification_status": "not_performed",
            "subject_digests": {},
            "expected_digests": {},
            "checkpoints": [],
            "notes": ["This mode does not emit execution-integrity evidence."],
        }

    current_subject_digests = dict(subject_digests)
    expected_digests = dict(current_subject_digests)
    tamper_case = task["tamper_case"]
    if tamper_case:
        target_name = f"{tamper_case['tamper_target']}.json"
        expected_digests[target_name] = mutate_digest(current_subject_digests[target_name])

    checkpoints = build_checkpoints(run_id, list(current_subject_digests.values()))
    if profile.policy_enforced and policy["status"] in {"blocked_budget", "blocked_approval"}:
        verification_status = "skipped_by_policy"
    elif tamper_case:
        verification_status = "tamper_detected"
    else:
        verification_status = "verified"

    return {
        "checked": True,
        "method": "sha256-checkpoint-chain",
        "verification_status": verification_status,
        "subject_digests": current_subject_digests,
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
    context: dict[str, Any],
    policy: dict[str, Any],
    status: str,
    subject_digests: dict[str, str],
) -> dict[str, Any]:
    profile = get_mode_profile(mode)
    exported = profile.receipt_exported
    artifacts = []
    question_map = build_receipt_question_map(mode, exported)
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
        if profile.policy_enforced and policy["status"] in {"blocked_budget", "blocked_approval"}:
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
            "profile": "paper-eval-bounded-receipt-v1" if exported else f"{profile.framework_label}-placeholder",
            "status": "exported" if exported else "not_exported",
            "scope": "bounded_run_bundle",
            "artifacts": artifacts,
            "questions_answered": question_map,
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
            else list(profile.notes) + ["This mode leaves receipt export as an empty placeholder for file-shape parity."],
        },
    }


def build_external_baseline_steps(
    task: dict[str, Any], mode: str, context: dict[str, Any], status: str
) -> list[dict[str, str]]:
    native_runtime = context.get("native_runtime", {})
    events = native_runtime.get("events")
    if not events:
        events = [
            {"step": "crewai_agent_initialized", "detail": "paper evaluation agent"},
            {"step": "crewai_task_built", "detail": task["title"]},
            {"step": "crewai_kickoff_started", "detail": task["input_payload"]["operation"]},
            {"step": "crewai_kickoff_finished", "detail": status},
        ]
    steps = []
    for index, event in enumerate(events):
        steps.append(
            {
                "step": event["step"],
                "at": stable_timestamp(context["task_id"], mode, index),
                "detail": event["detail"],
            }
        )
    return steps


def build_receipt_question_map(mode: str, exported: bool) -> dict[str, str]:
    if not exported:
        return {}

    question_map = {
        "what_was_intended": "intent.json#/intent",
        "what_was_authorized": "action.json#/policy/decision",
        "what_was_executed": "trace.json#/execution",
        "what_evidence_was_produced": "receipt.json#/audit_receipt/artifacts",
    }
    if mode == "no_intent":
        question_map.pop("what_was_intended")
    if mode == "no_governance":
        question_map.pop("what_was_authorized")
    return question_map


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the deterministic paper evaluation task suite.")
    parser.add_argument("--mode", required=True, choices=list_modes())
    parser.add_argument("--task-id", help="Optional single task id to run.")
    args = parser.parse_args()

    summary = run_suite(mode=args.mode, task_id=args.task_id)
    print(summary)


if __name__ == "__main__":
    main()
