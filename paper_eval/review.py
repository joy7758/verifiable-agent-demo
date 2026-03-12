"""Third-party review helpers for exported run bundles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import EXPORTED_FILES, load_json


def review_run_directory(run_dir: str | Path) -> dict[str, Any]:
    path = Path(run_dir).resolve()
    missing_files = [name for name in EXPORTED_FILES if not (path / name).exists()]
    review: dict[str, Any] = {
        "run_dir": str(path),
        "task_id": path.parent.name if path.parent != path else "unknown",
        "mode": path.name,
        "intent_captured": False,
        "policy_checked": False,
        "execution_verified": False,
        "receipt_exported": False,
        "overall_status": "invalid_bundle",
        "missing_or_failed_checks": [],
        "summary": "",
    }
    if missing_files:
        review["missing_or_failed_checks"] = [f"missing file: {name}" for name in missing_files]
        review["summary"] = "Run bundle is incomplete."
        return review

    try:
        intent = load_json(path / "intent.json")
        action = load_json(path / "action.json")
        result = load_json(path / "result.json")
        trace = load_json(path / "trace.json")
        receipt = load_json(path / "receipt.json")
    except Exception as exc:  # pragma: no cover - surfaced directly to the CLI
        review["missing_or_failed_checks"] = [f"failed to parse bundle: {exc}"]
        review["summary"] = "Run bundle could not be parsed."
        return review

    review["task_id"] = intent.get("task_id") or result.get("task_id") or review["task_id"]
    review["mode"] = intent.get("mode") or review["mode"]
    review["intent_captured"] = bool(intent.get("intent_captured")) and isinstance(intent.get("intent"), dict)
    review["policy_checked"] = bool(action.get("policy", {}).get("checked")) and isinstance(
        action.get("policy", {}).get("decision"), dict
    )
    integrity = trace.get("integrity", {})
    verification_status = integrity.get("verification_status")
    review["execution_verified"] = bool(integrity.get("checked")) and verification_status == "verified"
    review["receipt_exported"] = bool(receipt.get("receipt_exported")) and bool(
        receipt.get("audit_receipt", {}).get("artifacts")
    )

    failed_checks: list[str] = []
    if not review["intent_captured"]:
        failed_checks.append("intent not explicitly captured")
    if not review["policy_checked"]:
        failed_checks.append("policy not explicitly checked")
    if not review["execution_verified"]:
        failed_checks.append(f"execution verification status: {verification_status or 'unknown'}")
    if not review["receipt_exported"]:
        failed_checks.append("receipt not exported with artifact digests")

    result_status = result.get("status")
    if result_status == "tamper_detected":
        overall_status = "tamper_detected"
    elif result_status in {"blocked_budget", "blocked_approval"} and review["intent_captured"] and review["policy_checked"]:
        overall_status = "policy_blocked"
    elif not failed_checks:
        overall_status = "pass"
    else:
        overall_status = "partial"

    review["overall_status"] = overall_status
    review["missing_or_failed_checks"] = failed_checks
    review["summary"] = build_summary(review, result_status)
    return review


def build_summary(review: dict[str, Any], result_status: str | None) -> str:
    if review["overall_status"] == "pass":
        return "Intent, policy, execution verification, and receipt export are all present."
    if review["overall_status"] == "policy_blocked":
        return f"Run was intentionally blocked by policy with status {result_status}."
    if review["overall_status"] == "tamper_detected":
        return "Integrity verification detected a tamper condition."
    if review["overall_status"] == "invalid_bundle":
        return "Bundle is invalid and could not be fully reviewed."
    return "Bundle is reviewable but one or more evidence-chain checks are missing or failed."
