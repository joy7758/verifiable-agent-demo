#!/usr/bin/env python3
"""Generate and verify a minimal lifecycle governance walkthrough."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "artifacts" / "lifecycle_demo"
OBJECTS_DIR = OUTPUT_DIR / "objects"
RECEIPTS_DIR = OUTPUT_DIR / "receipts"

ALLOWED_TRANSITIONS: dict[str, tuple[tuple[str | None, ...], str]] = {
    "init": ((None,), "BORN"),
    "activate": (("BORN",), "ACTIVE"),
    "suspend": (("ACTIVE",), "SUSPENDED"),
    "resume": (("SUSPENDED",), "ACTIVE"),
    "fork": (("ACTIVE",), "ACTIVE"),
    "merge": (("ACTIVE", "SUSPENDED"), "MERGED"),
    "terminate": (("BORN", "ACTIVE", "SUSPENDED", "MERGED"), "TERMINATED"),
}


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_json(value)).hexdigest()


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _protected_boundary(receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "receipt_id": receipt["receipt_id"],
        "transition_type": receipt["transition_type"],
        "subject_instance_id": receipt["subject_instance_id"],
        "related_instance_id": receipt.get("related_instance_id"),
        "lineage_id": receipt["lineage_id"],
        "prior_state": receipt["prior_state"],
        "next_state": receipt["next_state"],
        "issued_at": receipt["issued_at"],
        "evidence_ref": receipt["evidence_ref"],
        "governance_decision_ref": receipt["governance_decision_ref"],
        "transition_reason": receipt.get("transition_reason"),
        "signer": receipt["signer"],
        "previous_receipt_hash": receipt.get("protected_hashes", {}).get("previous_receipt_hash"),
    }


def build_receipt(
    *,
    receipt_id: str,
    transition_type: str,
    subject_instance_id: str,
    lineage_id: str,
    prior_state: str | None,
    next_state: str,
    issued_at: str,
    evidence_ref: str,
    governance_decision_ref: str,
    signer: str,
    previous_receipt_hash: str | None,
    related_instance_id: str | None = None,
    transition_reason: str | None = None,
) -> dict[str, Any]:
    receipt: dict[str, Any] = {
        "schema_version": "0.1.0",
        "object_type": "lifecycle_receipt",
        "receipt_id": receipt_id,
        "transition_type": transition_type,
        "subject_instance_id": subject_instance_id,
        "lineage_id": lineage_id,
        "prior_state": prior_state,
        "next_state": next_state,
        "issued_at": issued_at,
        "evidence_ref": evidence_ref,
        "governance_decision_ref": governance_decision_ref,
        "signer": signer,
    }
    if related_instance_id is not None:
        receipt["related_instance_id"] = related_instance_id
    if transition_reason is not None:
        receipt["transition_reason"] = transition_reason

    receipt["protected_hashes"] = {
        "transition_hash": "",
        "previous_receipt_hash": previous_receipt_hash,
    }
    receipt["protected_hashes"]["transition_hash"] = _sha256(_protected_boundary(receipt))
    return receipt


def build_lifecycle_object(
    *,
    lifecycle_object_id: str,
    agent_instance_id: str,
    lineage_id: str,
    current_state: str,
    state_since: str,
    receipt_chain_head: str,
    evidence_refs: list[str],
    created_at: str,
) -> dict[str, Any]:
    return {
        "schema_version": "0.1.0",
        "object_type": "lifecycle_object",
        "lifecycle_object_id": lifecycle_object_id,
        "agent_instance_id": agent_instance_id,
        "lineage_id": lineage_id,
        "persona_ref": "urn:pop:persona:research-assistant:v1",
        "current_state": current_state,
        "state_since": state_since,
        "governance_profile_ref": "urn:governance-profile:token-governor:default:v1",
        "receipt_chain_head": receipt_chain_head,
        "evidence_refs": evidence_refs,
        "created_at": created_at,
    }


def verify(
    *,
    parent_object: dict[str, Any],
    child_object: dict[str, Any],
    receipts: list[dict[str, Any]],
) -> dict[str, Any]:
    issues: list[str] = []
    objects = {
        parent_object["agent_instance_id"]: parent_object,
        child_object["agent_instance_id"]: child_object,
    }
    subject_states: dict[str, str] = {}
    subject_last_hash: dict[str, str] = {}
    subject_last_timestamp: dict[str, datetime] = {}
    last_receipt_by_subject: dict[str, dict[str, Any]] = {}
    merge_receipt: dict[str, Any] | None = None

    for receipt in receipts:
        subject_id = receipt["subject_instance_id"]
        transition = receipt["transition_type"]
        expected = ALLOWED_TRANSITIONS.get(transition)
        if expected is None:
            issues.append(f"unknown transition_type: {transition}")
            continue

        allowed_priors, expected_next = expected
        current_state = subject_states.get(subject_id)
        if current_state == "TERMINATED":
            issues.append(f"{subject_id}: TERMINATED branch cannot accept {transition}")
            continue
        if current_state == "MERGED" and transition != "terminate":
            issues.append(f"{subject_id}: MERGED branch cannot continue with {transition}")
            continue

        actual_transition_hash = receipt["protected_hashes"]["transition_hash"]
        expected_transition_hash = _sha256(_protected_boundary(receipt))
        if actual_transition_hash != expected_transition_hash:
            issues.append(f"{transition}: transition_hash mismatch for {subject_id}")
            continue

        previous_hash = receipt["protected_hashes"]["previous_receipt_hash"]
        expected_previous_hash = subject_last_hash.get(subject_id)
        if transition == "init":
            if previous_hash is not None:
                issues.append("init: previous_receipt_hash must be null")
                continue
        elif expected_previous_hash is not None and previous_hash != expected_previous_hash:
            issues.append(
                f"{transition}: previous_receipt_hash mismatch for {subject_id}, "
                f"expected {expected_previous_hash!r}, got {previous_hash!r}"
            )
            continue

        prior_state = receipt["prior_state"]
        next_state = receipt["next_state"]
        if prior_state not in allowed_priors:
            issues.append(
                f"{transition}: expected prior_state in {allowed_priors!r}, got {prior_state!r}"
            )
            continue
        if current_state is not None and prior_state != current_state:
            issues.append(
                f"{transition}: state continuity mismatch for {subject_id}, "
                f"expected {current_state!r}, got {prior_state!r}"
            )
            continue
        if next_state != expected_next:
            issues.append(
                f"{transition}: expected next_state {expected_next!r}, got {next_state!r}"
            )
            continue

        issued_at = _parse_timestamp(receipt["issued_at"])
        last_issued_at = subject_last_timestamp.get(subject_id)
        if last_issued_at is not None and issued_at < last_issued_at:
            issues.append(f"{transition}: timestamp regression for {subject_id}")
            continue

        if transition == "fork":
            child_id = receipt.get("related_instance_id")
            if child_id != child_object["agent_instance_id"]:
                issues.append("fork: related_instance_id does not match the child lifecycle object")
                continue
            if child_object["lineage_id"] != receipt["lineage_id"]:
                issues.append("fork: child lineage_id does not match parent lineage_id")
                continue
            subject_states[child_id] = "ACTIVE"
            subject_last_hash[child_id] = actual_transition_hash
            subject_last_timestamp[child_id] = issued_at

        if transition == "merge":
            merge_target = receipt.get("related_instance_id")
            if merge_target != parent_object["agent_instance_id"]:
                issues.append("merge: related_instance_id does not point to the parent lifecycle object")
                continue
            if parent_object["lineage_id"] != receipt["lineage_id"]:
                issues.append("merge: parent lineage_id does not match the merged branch lineage_id")
                continue
            merge_receipt = receipt

        subject_states[subject_id] = next_state
        subject_last_hash[subject_id] = actual_transition_hash
        subject_last_timestamp[subject_id] = issued_at
        last_receipt_by_subject[subject_id] = receipt

    parent_last = last_receipt_by_subject.get(parent_object["agent_instance_id"])
    child_last = last_receipt_by_subject.get(child_object["agent_instance_id"])
    if parent_last is None or child_last is None:
        issues.append("verifier did not observe both parent and child receipt chains")
    else:
        if parent_object["receipt_chain_head"] != parent_last["receipt_id"]:
            issues.append("parent lifecycle object receipt_chain_head does not match the last parent receipt")
        if parent_object["current_state"] != parent_last["next_state"]:
            issues.append("parent lifecycle object current_state does not match the last parent receipt")
        if child_object["receipt_chain_head"] != child_last["receipt_id"]:
            issues.append("child lifecycle object receipt_chain_head does not match the last child receipt")
        if child_object["current_state"] != child_last["next_state"]:
            issues.append("child lifecycle object current_state does not match the last child receipt")

    child_receipts = [receipt for receipt in receipts if receipt["subject_instance_id"] == child_object["agent_instance_id"]]
    merged_branch_closed = True
    merge_seen = False
    for receipt in child_receipts:
        if receipt["transition_type"] == "merge":
            merge_seen = True
            continue
        if merge_seen and receipt["transition_type"] != "terminate":
            merged_branch_closed = False

    checks = {
        "lineage_continuity": "ok"
        if parent_object["lineage_id"] == child_object["lineage_id"]
        else "fail",
        "merge_target_exists": "ok" if merge_receipt is not None else "fail",
        "merged_branch_closed": "ok" if merged_branch_closed and child_object["current_state"] == "TERMINATED" else "fail",
        "parent_state_matches_object": "ok"
        if parent_last and parent_object["current_state"] == parent_last["next_state"]
        else "fail",
        "child_state_matches_object": "ok"
        if child_last and child_object["current_state"] == child_last["next_state"]
        else "fail",
    }

    if any(value != "ok" for value in checks.values()) and not issues:
        issues.append("one or more lifecycle verifier checks did not reach ok status")

    return {
        "status": "ok" if not issues else "fail",
        "verified_receipt_count": len(receipts),
        "verified_transitions": [receipt["transition_type"] for receipt in receipts],
        "parent_final_state": parent_object["current_state"],
        "child_final_state": child_object["current_state"],
        "merge_mode": "runnable_transition",
        "checks": checks,
        "issues": issues,
    }


def build_verifier_text(summary: dict[str, Any]) -> str:
    lines = [
        f"Verification status: {summary['status']}",
        f"Verified transitions: {', '.join(summary['verified_transitions'])}",
        f"Parent final state: {summary['parent_final_state']}",
        f"Child final state: {summary['child_final_state']}",
        f"Lineage continuity: {summary['checks']['lineage_continuity']}",
        f"Merge target exists: {summary['checks']['merge_target_exists']}",
        f"Merged branch closed: {summary['checks']['merged_branch_closed']}",
        f"Parent object consistency: {summary['checks']['parent_state_matches_object']}",
        f"Child object consistency: {summary['checks']['child_state_matches_object']}",
    ]
    if summary["issues"]:
        lines.append("Issues:")
        lines.extend(f"- {issue}" for issue in summary["issues"])
    else:
        lines.append("Issues: none")
    return "\n".join(lines) + "\n"


def build_demo() -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    lineage_id = "lineage-root-001"
    parent_instance_id = "agent-alpha"
    child_instance_id = "agent-alpha-child"
    signer = "urn:signer:token-governor:lifecycle"

    init_receipt = build_receipt(
        receipt_id="urn:lifecycle-receipt:init-agent-alpha",
        transition_type="init",
        subject_instance_id=parent_instance_id,
        lineage_id=lineage_id,
        prior_state=None,
        next_state="BORN",
        issued_at="2026-03-17T00:00:00Z",
        evidence_ref="urn:evidence:bundle:init-agent-alpha",
        governance_decision_ref="urn:governance-decision:init-approve-001",
        signer=signer,
        previous_receipt_hash=None,
    )
    activate_receipt = build_receipt(
        receipt_id="urn:lifecycle-receipt:activate-agent-alpha",
        transition_type="activate",
        subject_instance_id=parent_instance_id,
        lineage_id=lineage_id,
        prior_state="BORN",
        next_state="ACTIVE",
        issued_at="2026-03-17T00:05:00Z",
        evidence_ref="urn:evidence:bundle:activate-agent-alpha",
        governance_decision_ref="urn:governance-decision:activate-approve-001",
        signer=signer,
        previous_receipt_hash=init_receipt["protected_hashes"]["transition_hash"],
    )
    fork_receipt = build_receipt(
        receipt_id="urn:lifecycle-receipt:fork-agent-alpha",
        transition_type="fork",
        subject_instance_id=parent_instance_id,
        related_instance_id=child_instance_id,
        lineage_id=lineage_id,
        prior_state="ACTIVE",
        next_state="ACTIVE",
        issued_at="2026-03-17T02:00:00Z",
        evidence_ref="urn:evidence:bundle:fork-agent-alpha",
        governance_decision_ref="urn:governance-decision:fork-approve-001",
        signer=signer,
        previous_receipt_hash=activate_receipt["protected_hashes"]["transition_hash"],
    )
    merge_receipt = build_receipt(
        receipt_id="urn:lifecycle-receipt:merge-agent-alpha-child",
        transition_type="merge",
        subject_instance_id=child_instance_id,
        related_instance_id=parent_instance_id,
        lineage_id=lineage_id,
        prior_state="ACTIVE",
        next_state="MERGED",
        issued_at="2026-03-17T03:00:00Z",
        evidence_ref="urn:evidence:bundle:merge-agent-alpha-child",
        governance_decision_ref="urn:governance-decision:merge-approve-001",
        signer=signer,
        previous_receipt_hash=fork_receipt["protected_hashes"]["transition_hash"],
    )
    terminate_receipt = build_receipt(
        receipt_id="urn:lifecycle-receipt:terminate-agent-alpha-child",
        transition_type="terminate",
        subject_instance_id=child_instance_id,
        lineage_id=lineage_id,
        prior_state="MERGED",
        next_state="TERMINATED",
        issued_at="2026-03-17T03:10:00Z",
        evidence_ref="urn:evidence:bundle:terminate-agent-alpha-child",
        governance_decision_ref="urn:governance-decision:terminate-approve-001",
        signer=signer,
        previous_receipt_hash=merge_receipt["protected_hashes"]["transition_hash"],
        transition_reason="Merged child branch is now closed and cannot continue independently.",
    )

    parent_object = build_lifecycle_object(
        lifecycle_object_id="urn:lifecycle-object:agent-alpha",
        agent_instance_id=parent_instance_id,
        lineage_id=lineage_id,
        current_state="ACTIVE",
        state_since=fork_receipt["issued_at"],
        receipt_chain_head=fork_receipt["receipt_id"],
        evidence_refs=[
            init_receipt["evidence_ref"],
            activate_receipt["evidence_ref"],
            fork_receipt["evidence_ref"],
        ],
        created_at=init_receipt["issued_at"],
    )
    child_object = build_lifecycle_object(
        lifecycle_object_id="urn:lifecycle-object:agent-alpha-child",
        agent_instance_id=child_instance_id,
        lineage_id=lineage_id,
        current_state="TERMINATED",
        state_since=terminate_receipt["issued_at"],
        receipt_chain_head=terminate_receipt["receipt_id"],
        evidence_refs=[
            fork_receipt["evidence_ref"],
            merge_receipt["evidence_ref"],
            terminate_receipt["evidence_ref"],
        ],
        created_at=fork_receipt["issued_at"],
    )

    receipts = [init_receipt, activate_receipt, fork_receipt, merge_receipt, terminate_receipt]
    verification = verify(parent_object=parent_object, child_object=child_object, receipts=receipts)
    return parent_object, child_object, receipts, verification


def main() -> int:
    parent_object, child_object, receipts, verification = build_demo()

    _write_json(OBJECTS_DIR / "parent.lifecycle_object.json", parent_object)
    _write_json(OBJECTS_DIR / "child.lifecycle_object.json", child_object)
    for receipt in receipts:
        filename = f"{receipt['transition_type']}.receipt.json"
        _write_json(RECEIPTS_DIR / filename, receipt)
    _write_json(OUTPUT_DIR / "verify.json", verification)
    _write_text(OUTPUT_DIR / "verify.txt", build_verifier_text(verification))

    print(f"Wrote lifecycle objects to {OBJECTS_DIR}")
    print(f"Wrote {len(receipts)} receipts to {RECEIPTS_DIR}")
    print(
        "Wrote verifier outputs to "
        f"{OUTPUT_DIR / 'verify.json'} and {OUTPUT_DIR / 'verify.txt'}"
    )
    print(
        f"Verification status: {verification['status']} "
        f"({verification['verified_receipt_count']} receipts checked)"
    )
    return 0 if verification["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
