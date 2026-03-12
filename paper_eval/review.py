"""Third-party review helpers for exported run bundles."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import EXPORTED_FILES, load_json, sha256_digest


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

    consistency = inspect_bundle(intent, action, result, trace, receipt)
    review["task_id"] = _first_nonempty(
        intent.get("task_id"),
        action.get("task_id"),
        result.get("task_id"),
        trace.get("task_id"),
        receipt.get("task_id"),
        review["task_id"],
    )
    review["mode"] = _first_nonempty(
        intent.get("mode"),
        action.get("mode"),
        result.get("mode"),
        trace.get("mode"),
        receipt.get("mode"),
        review["mode"],
    )

    intent_object = intent.get("intent") or {}
    policy_bundle = action.get("policy", {})
    policy_decision = policy_bundle.get("decision") or {}
    integrity = trace.get("integrity", {})
    audit_receipt = receipt.get("audit_receipt") or {}
    verification_status = integrity.get("verification_status")

    review["intent_captured"] = bool(intent.get("intent_captured")) and isinstance(intent_object, dict) and bool(
        intent_object.get("goal")
    )
    review["policy_checked"] = bool(policy_bundle.get("checked")) and isinstance(policy_decision, dict) and bool(
        policy_decision.get("status")
    )
    review["execution_verified"] = (
        bool(integrity.get("checked"))
        and verification_status == "verified"
        and consistency["identity_consistent"]
        and consistency["subject_digests_valid"]
        and consistency["expected_state_valid"]
    )
    review["receipt_exported"] = (
        bool(receipt.get("receipt_exported"))
        and consistency["receipt_valid"]
        and len(audit_receipt.get("questions_answered") or {}) == 4
    )

    failed_checks: list[str] = []
    if not review["intent_captured"]:
        failed_checks.append("intent not explicitly captured")
    if not review["policy_checked"]:
        failed_checks.append("policy not explicitly checked")
    if not review["execution_verified"]:
        failed_checks.append(f"execution verification status: {verification_status or 'unknown'}")
    if not review["receipt_exported"]:
        failed_checks.append("receipt not exported with verifiable artifact digests")

    failed_checks.extend(consistency["identity_issues"])
    failed_checks.extend(consistency["subject_digest_issues"])
    failed_checks.extend(consistency["expected_digest_issues"])
    failed_checks.extend(consistency["receipt_issues"])
    failed_checks = dedupe_preserve_order(failed_checks)

    result_status = result.get("status")
    if (
        result_status == "tamper_detected"
        and review["intent_captured"]
        and review["policy_checked"]
        and review["receipt_exported"]
        and consistency["identity_consistent"]
        and consistency["subject_digests_valid"]
        and consistency["tamper_confirmed"]
    ):
        overall_status = "tamper_detected"
    elif (
        result_status in {"blocked_budget", "blocked_approval"}
        and review["intent_captured"]
        and review["policy_checked"]
        and review["receipt_exported"]
        and consistency["identity_consistent"]
        and consistency["subject_digests_valid"]
        and consistency["expected_state_valid"]
    ):
        overall_status = "policy_blocked"
    elif not failed_checks:
        overall_status = "pass"
    else:
        overall_status = "partial"

    review["overall_status"] = overall_status
    review["missing_or_failed_checks"] = failed_checks
    review["summary"] = build_summary(review, result_status)
    return review


def inspect_bundle(
    intent: dict[str, Any],
    action: dict[str, Any],
    result: dict[str, Any],
    trace: dict[str, Any],
    receipt: dict[str, Any],
) -> dict[str, Any]:
    payloads = {
        "intent.json": intent,
        "action.json": action,
        "result.json": result,
        "trace.json": trace,
        "receipt.json": receipt,
    }
    actual_digests = {name: sha256_digest(payload) for name, payload in payloads.items() if name != "receipt.json"}

    identity_issues = inspect_identity(payloads)
    subject_digest_issues, subject_digests_valid = inspect_subject_digests(trace.get("integrity") or {}, actual_digests)
    expected_digest_issues, expected_state_valid, tamper_confirmed = inspect_expected_digests(
        trace.get("integrity") or {}, actual_digests
    )
    receipt_issues, receipt_valid = inspect_receipt(receipt, actual_digests)

    return {
        "identity_consistent": not identity_issues,
        "identity_issues": identity_issues,
        "subject_digests_valid": subject_digests_valid,
        "subject_digest_issues": subject_digest_issues,
        "expected_state_valid": expected_state_valid,
        "expected_digest_issues": expected_digest_issues,
        "receipt_valid": receipt_valid,
        "receipt_issues": receipt_issues,
        "tamper_confirmed": tamper_confirmed,
    }


def inspect_identity(payloads: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    expected_types = {
        "intent.json": "intent",
        "action.json": "action",
        "result.json": "result",
        "trace.json": "trace",
        "receipt.json": "receipt",
    }
    for name, payload in payloads.items():
        if payload.get("file_type") != expected_types[name]:
            issues.append(f"{name} file_type mismatch")

    for key in ("task_id", "run_id", "mode"):
        observed = {name: payload.get(key) for name, payload in payloads.items()}
        values = {value for value in observed.values() if value}
        if len(values) > 1:
            issues.append(f"inconsistent {key} across bundle")
        elif not values:
            issues.append(f"missing {key} across bundle")
    return issues


def inspect_subject_digests(integrity: dict[str, Any], actual_digests: dict[str, str]) -> tuple[list[str], bool]:
    issues: list[str] = []
    if not integrity.get("checked"):
        return issues, False

    subject_digests = integrity.get("subject_digests") or {}
    for required in ("intent.json", "action.json", "result.json"):
        if required not in subject_digests:
            issues.append(f"missing integrity subject digest for {required}")
    unexpected = set(subject_digests) - set(actual_digests)
    for name in sorted(unexpected):
        issues.append(f"unexpected integrity subject digest entry: {name}")
    for name, digest in subject_digests.items():
        actual = actual_digests.get(name)
        if actual and digest != actual:
            issues.append(f"integrity subject digest mismatch for {name}")
    return issues, not issues


def inspect_expected_digests(integrity: dict[str, Any], actual_digests: dict[str, str]) -> tuple[list[str], bool, bool]:
    issues: list[str] = []
    if not integrity.get("checked"):
        return issues, False, False

    expected_digests = integrity.get("expected_digests") or {}
    verification_status = integrity.get("verification_status")
    mismatches = [
        name
        for name, digest in expected_digests.items()
        if name in actual_digests and digest != actual_digests[name]
    ]

    if verification_status in {"verified", "skipped_by_policy"}:
        for required in ("intent.json", "action.json", "result.json"):
            if required not in expected_digests:
                issues.append(f"missing integrity expected digest for {required}")
        if mismatches:
            issues.extend(f"integrity expected digest mismatch for {name}" for name in mismatches)
        return issues, not issues, False

    if verification_status == "tamper_detected":
        if not expected_digests:
            issues.append("declared tamper without expected digests")
        if not mismatches:
            issues.append("declared tamper without an independently observed digest mismatch")
        return issues, not issues, not issues

    issues.append(f"unrecognized execution verification status: {verification_status or 'unknown'}")
    return issues, False, False


def inspect_receipt(receipt: dict[str, Any], actual_digests: dict[str, str]) -> tuple[list[str], bool]:
    issues: list[str] = []
    if not receipt.get("receipt_exported"):
        return issues, False

    audit_receipt = receipt.get("audit_receipt") or {}
    artifacts = audit_receipt.get("artifacts") or []
    artifact_map = {artifact.get("path"): artifact.get("sha256") for artifact in artifacts}
    required_paths = {"intent.json", "action.json", "result.json", "trace.json"}

    if set(artifact_map) != required_paths:
        issues.append("receipt artifacts do not match the required bounded bundle")
    for path, digest in artifact_map.items():
        actual = actual_digests.get(path)
        if actual and digest != actual:
            issues.append(f"receipt artifact digest mismatch for {path}")

    boundedness = audit_receipt.get("boundedness") or {}
    if boundedness.get("exported_files_count") != len(EXPORTED_FILES):
        issues.append("receipt boundedness exported_files_count is inconsistent")
    if boundedness.get("allowed_files") != EXPORTED_FILES:
        issues.append("receipt boundedness allowed_files is inconsistent")
    if boundedness.get("artifact_digest_count") != len(required_paths):
        issues.append("receipt boundedness artifact_digest_count is inconsistent")
    if len(audit_receipt.get("questions_answered") or {}) != 4:
        issues.append("receipt does not answer all four review questions")
    return issues, not issues


def dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            output.append(item)
    return output


def _first_nonempty(*values: Any) -> Any:
    for value in values:
        if value not in (None, ""):
            return value
    return None


def build_summary(review: dict[str, Any], result_status: str | None) -> str:
    if review["overall_status"] == "pass":
        return "Intent, policy, execution verification, and receipt export are all present and independently corroborated."
    if review["overall_status"] == "policy_blocked":
        return f"Run was intentionally blocked by policy with status {result_status}, and the block remains independently reviewable."
    if review["overall_status"] == "tamper_detected":
        return "Integrity verification independently corroborated a tamper condition."
    if review["overall_status"] == "invalid_bundle":
        return "Bundle is invalid and could not be fully reviewed."
    return "Bundle is reviewable but one or more evidence-chain checks are missing, inconsistent, or unverifiable."
