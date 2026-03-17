#!/usr/bin/env python3
"""Generate and verify a minimal lifecycle governance walkthrough."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT_DIR / "artifacts" / "lifecycle_demo"
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

    transition_hash = _sha256(_protected_boundary(receipt))
    receipt["protected_hashes"] = {
        "transition_hash": transition_hash,
        "previous_receipt_hash": previous_receipt_hash,
    }
    return receipt


def verify(receipts: list[dict[str, Any]], lifecycle_object: dict[str, Any]) -> dict[str, Any]:
    issues: list[str] = []
    previous_hash: str | None = None

    for receipt in receipts:
        transition = receipt["transition_type"]
        expected = ALLOWED_TRANSITIONS.get(transition)
        if expected is None:
            issues.append(f"unknown transition_type: {transition}")
            continue

        allowed_priors, expected_next = expected
        if receipt["prior_state"] not in allowed_priors:
            issues.append(
                f"{transition}: expected prior_state in {allowed_priors!r}, got {receipt['prior_state']!r}"
            )
        if receipt["next_state"] != expected_next:
            issues.append(
                f"{transition}: expected next_state {expected_next!r}, got {receipt['next_state']!r}"
            )

        actual_transition_hash = receipt["protected_hashes"]["transition_hash"]
        expected_transition_hash = _sha256(_protected_boundary(receipt))
        if actual_transition_hash != expected_transition_hash:
            issues.append(f"{transition}: transition_hash mismatch")

        actual_previous_hash = receipt["protected_hashes"]["previous_receipt_hash"]
        if actual_previous_hash != previous_hash:
            issues.append(
                f"{transition}: previous_receipt_hash mismatch, expected {previous_hash!r}, got {actual_previous_hash!r}"
            )
        previous_hash = actual_transition_hash

    if lifecycle_object["receipt_chain_head"] != receipts[-1]["receipt_id"]:
        issues.append("lifecycle object receipt_chain_head does not match final receipt_id")
    if lifecycle_object["current_state"] != receipts[-1]["next_state"]:
        issues.append("lifecycle object current_state does not match final receipt next_state")

    return {
        "status": "ok" if not issues else "fail",
        "verified_receipt_count": len(receipts),
        "verified_transitions": [receipt["transition_type"] for receipt in receipts],
        "final_state": lifecycle_object["current_state"],
        "merge_mode": "document_sample_only",
        "issues": issues,
    }


def build_demo() -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    lineage_id = "lineage-root-001"
    agent_instance_id = "agent-alpha"
    related_instance_id = "agent-alpha-child"
    signer = "urn:signer:token-governor:lifecycle"

    init_receipt = build_receipt(
        receipt_id="urn:lifecycle-receipt:init-agent-alpha",
        transition_type="init",
        subject_instance_id=agent_instance_id,
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
        subject_instance_id=agent_instance_id,
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
        subject_instance_id=agent_instance_id,
        related_instance_id=related_instance_id,
        lineage_id=lineage_id,
        prior_state="ACTIVE",
        next_state="ACTIVE",
        issued_at="2026-03-17T02:00:00Z",
        evidence_ref="urn:evidence:bundle:fork-agent-alpha",
        governance_decision_ref="urn:governance-decision:fork-approve-001",
        signer=signer,
        previous_receipt_hash=activate_receipt["protected_hashes"]["transition_hash"],
    )
    terminate_receipt = build_receipt(
        receipt_id="urn:lifecycle-receipt:terminate-agent-alpha",
        transition_type="terminate",
        subject_instance_id=agent_instance_id,
        lineage_id=lineage_id,
        prior_state="ACTIVE",
        next_state="TERMINATED",
        issued_at="2026-03-17T03:10:00Z",
        evidence_ref="urn:evidence:bundle:terminate-agent-alpha",
        governance_decision_ref="urn:governance-decision:terminate-approve-001",
        signer=signer,
        previous_receipt_hash=fork_receipt["protected_hashes"]["transition_hash"],
        transition_reason="Root branch was explicitly ended after delegating work to a forked branch.",
    )

    lifecycle_object = {
        "schema_version": "0.1.0",
        "object_type": "lifecycle_object",
        "lifecycle_object_id": "urn:lifecycle-object:agent-alpha",
        "agent_instance_id": agent_instance_id,
        "lineage_id": lineage_id,
        "persona_ref": "urn:pop:persona:research-assistant:v1",
        "current_state": "TERMINATED",
        "state_since": terminate_receipt["issued_at"],
        "governance_profile_ref": "urn:governance-profile:token-governor:default:v1",
        "receipt_chain_head": terminate_receipt["receipt_id"],
        "evidence_refs": [
            init_receipt["evidence_ref"],
            activate_receipt["evidence_ref"],
            fork_receipt["evidence_ref"],
            terminate_receipt["evidence_ref"],
        ],
        "created_at": init_receipt["issued_at"],
    }

    receipts = [init_receipt, activate_receipt, fork_receipt, terminate_receipt]
    verification = verify(receipts, lifecycle_object)
    return lifecycle_object, receipts, verification


def main() -> int:
    lifecycle_object, receipts, verification = build_demo()

    _write_json(OUTPUT_DIR / "lifecycle_object.json", lifecycle_object)
    for receipt in receipts:
        filename = f"{receipt['transition_type']}.receipt.json"
        _write_json(RECEIPTS_DIR / filename, receipt)
    _write_json(OUTPUT_DIR / "verify.json", verification)

    print(f"Wrote lifecycle object to {OUTPUT_DIR / 'lifecycle_object.json'}")
    print(f"Wrote {len(receipts)} receipts to {RECEIPTS_DIR}")
    print(f"Wrote verifier output to {OUTPUT_DIR / 'verify.json'}")
    print(
        f"Verification status: {verification['status']} "
        f"({verification['verified_receipt_count']} receipts checked)"
    )
    return 0 if verification["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
