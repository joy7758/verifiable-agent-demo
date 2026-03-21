from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = REPO_ROOT.parent
OUTPUT_DIR = Path(
    os.getenv(
        "ENTERPRISE_SANDBOX_OUTPUT_DIR",
        str(REPO_ROOT / "artifacts" / "enterprise_sandbox_demo"),
    )
)
SCENARIO = "整理客户拜访记录 → 生成周报 → 发起审批"

for repo_name in ("agent-evidence", "aro-audit"):
    candidate = WORKSPACE_ROOT / repo_name
    if candidate.exists() and str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from agent_evidence import EvidenceRecorder, LocalEvidenceStore

try:
    from agent_evidence.sep import export_sep_bundle, verify_sep_bundle
except ImportError:  # pragma: no cover - compatibility for post-sep agent-evidence
    @dataclass
    class _CompatSepEvent:
        event_id: str
        event_type: str
        event_hash: str
        previous_event_hash: str | None
        chain_hash: str

    @dataclass
    class _CompatSepBundle:
        events: list[_CompatSepEvent]

    def export_sep_bundle(
        envelopes: list[Any],
        output_path: Path,
        *,
        kernel_bundle_path: str,
    ) -> _CompatSepBundle:
        events = [
            _CompatSepEvent(
                event_id=envelope.event.event_id,
                event_type=envelope.event.event_type,
                event_hash=envelope.hashes.event_hash,
                previous_event_hash=envelope.hashes.previous_event_hash,
                chain_hash=envelope.hashes.chain_hash,
            )
            for envelope in envelopes
        ]
        payload = {
            "schema_version": "compat-sep-v1",
            "kernel_bundle_path": kernel_bundle_path,
            "event_count": len(events),
            "events": [
                {
                    "event_id": event.event_id,
                    "event_type": event.event_type,
                    "event_hash": event.event_hash,
                    "previous_event_hash": event.previous_event_hash,
                    "chain_hash": event.chain_hash,
                }
                for event in events
            ],
        }
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return _CompatSepBundle(events=events)

    def verify_sep_bundle(path: Path) -> dict[str, Any]:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            events = list(payload["events"])
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            return {"verified": False, "mode": "compat-sep-v1", "reason": "invalid_bundle"}

        previous_hash = None
        for index, event in enumerate(events):
            if not isinstance(event, dict):
                return {
                    "verified": False,
                    "mode": "compat-sep-v1",
                    "reason": f"invalid_event_{index}",
                }
            if not event.get("event_hash") or not event.get("chain_hash"):
                return {
                    "verified": False,
                    "mode": "compat-sep-v1",
                    "reason": f"missing_hashes_{index}",
                }
            if event.get("previous_event_hash") != previous_hash:
                return {
                    "verified": False,
                    "mode": "compat-sep-v1",
                    "reason": f"broken_previous_hash_{index}",
                }
            previous_hash = event["event_hash"]

        return {
            "verified": True,
            "mode": "compat-sep-v1",
            "event_count": len(events),
        }

try:
    from validator import validate_enterprise_sandbox_receipt_data
except ImportError:  # pragma: no cover - local workspace dependency
    validate_enterprise_sandbox_receipt_data = None


def _write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _sha256_prefixed_bytes(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _sha256_prefixed_text(payload: str) -> str:
    return _sha256_prefixed_bytes(payload.encode("utf-8"))


def _build_intent() -> dict[str, Any]:
    return {
        "schema_version": "0.1.0-draft",
        "object_type": "agent_intent",
        "scenario": SCENARIO,
        "intent": {
            "operation": "customer_visit_weekly_report_approval",
            "summary": "整理客户拜访记录，生成周报，并发起审批。",
        },
        "constraints": {
            "network_access": "proxy_only",
            "approval_required": True,
            "snapshot_required": True,
        },
        "actor_ref": "pop://personas/enterprise-operator",
    }


def _build_policy() -> dict[str, Any]:
    return {
        "policy_id": "policy://enterprise-sandbox-demo",
        "scenario": SCENARIO,
        "permission_intersection": ["read", "write"],
        "policy_decision": {
            "decision": "allow_with_approval",
            "decision_reason": "report generation is allowed, final dispatch requires approval",
            "allowed_permissions": ["read", "write"],
        },
        "sandbox_context": {
            "sandbox_id": "sandbox-demo-001",
            "environment": "enterprise-agent-os",
            "control_plane": {"id": "agent-os", "version": "2026.03"},
        },
        "network_proxy_meta": {
            "proxy_id": "proxy-demo-001",
            "status": "proxyed",
            "endpoint": "https://proxy.enterprise.internal",
        },
        "snapshot_ref": {
            "snapshot_id": "snapshot-demo-001",
            "storage": "kernel_bundle.json",
        },
        "verifier_ref": "mvk://sep-replay",
    }


def _copy_kernel_bundle(output_dir: Path) -> Path:
    source = WORKSPACE_ROOT / "fdo-kernel-mvk" / "examples" / "output" / "audit_bundle.json"
    target = output_dir / "kernel_bundle.json"
    shutil.copyfile(source, target)
    return target


def _record_sep_trace(trace_path: Path, intent_path: Path, policy_path: Path) -> dict[str, Any]:
    if trace_path.exists():
        trace_path.unlink()
    store = LocalEvidenceStore(trace_path)
    recorder = EvidenceRecorder(store)
    common_metadata = {
        "actor_identity": {"actor": "employee:alice", "department": "sales"},
        "intent_ref": intent_path.name,
        "action_ref": policy_path.name,
        "permission_intersection": ["read", "write"],
        "policy_decision": {
            "decision": "allow_with_approval",
            "allowed_permissions": ["read", "write"],
            "decision_reason": "report generation is allowed, final dispatch requires approval",
        },
        "sandbox_context": {
            "sandbox_id": "sandbox-demo-001",
            "environment": "enterprise-agent-os",
            "control_plane": {"id": "agent-os", "version": "2026.03"},
        },
        "network_proxy_meta": {
            "proxy_id": "proxy-demo-001",
            "status": "proxyed",
            "endpoint": "https://proxy.enterprise.internal",
        },
        "snapshot_ref": "kernel_bundle.json",
        "verifier_ref": "mvk://sep-replay",
        "signature_ref": "sig://enterprise-demo/001",
    }

    recorder.record(
        actor="token-governor",
        event_type="policy.decision",
        metadata=common_metadata,
        context={"source": "token_governor", "component": "governance"},
        outputs={"result_ref": "policy.json"},
    )
    recorder.record(
        actor="sandbox-runtime",
        event_type="sandbox.enter",
        metadata=common_metadata,
        context={"source": "mvk", "component": "sandbox"},
    )
    recorder.record(
        actor="sandbox-runtime",
        event_type="snapshot.create",
        metadata=common_metadata,
        context={"source": "mvk", "component": "snapshot"},
        outputs={"snapshot_ref": "kernel_bundle.json"},
    )
    recorder.record(
        actor="sandbox-runtime",
        event_type="network.request",
        metadata=common_metadata,
        context={"source": "runtime", "component": "network"},
        outputs={"result_ref": "policy.json"},
    )
    recorder.record(
        actor="sandbox-runtime",
        event_type="network.response",
        metadata=common_metadata,
        context={"source": "runtime", "component": "network"},
        outputs={"result_ref": "policy.json"},
    )
    recorder.record(
        actor="approver",
        event_type="approval.start",
        metadata=common_metadata,
        context={"source": "runtime", "component": "approval"},
    )
    recorder.record(
        actor="approver",
        event_type="approval.result",
        metadata=common_metadata,
        context={"source": "runtime", "component": "approval"},
        outputs={"result_ref": "audit_receipt.json"},
    )
    return {"record_count": len(store.list())}


def _mvk_replay(bundle_path: Path) -> dict[str, Any]:
    mvk_root = WORKSPACE_ROOT / "fdo-kernel-mvk"
    result = subprocess.run(
        [sys.executable, "-m", "kernel.verify", str(bundle_path)],
        capture_output=True,
        text=True,
        cwd=str(mvk_root),
        check=False,
    )
    stdout_lines = [line for line in result.stdout.splitlines() if line.strip()]
    verdict = stdout_lines[-1] if stdout_lines else "CONFORMANCE_FAIL"
    return {
        "verdict": verdict,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def _build_audit_receipt(
    *,
    sep_bundle: Any,
    kernel_bundle_path: Path,
    replay_verdict: dict[str, Any],
) -> dict[str, Any]:
    snapshot_hash = _sha256_prefixed_bytes(kernel_bundle_path.read_bytes())
    last_event = sep_bundle.events[-1] if sep_bundle.events else None
    event_chain = []
    for event in sep_bundle.events:
        event_chain.append(
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "event_hash": f"sha256:{event.event_hash}",
                "previous_event_hash": (
                    None if event.previous_event_hash is None else f"sha256:{event.previous_event_hash}"
                ),
                "chain_hash": f"sha256:{event.chain_hash}",
                "event_ref": "trace.jsonl",
            }
        )
    receipt = {
        "schema_version": "0.1.0",
        "object_type": "enterprise_sandbox_receipt",
        "receipt_id": "urn:enterprise-sandbox-receipt:demo-001",
        "actor_identity": "employee:alice",
        "intent_ref": "intent.json",
        "action_ref": "policy.json",
        "result_ref": "replay_verdict.json",
        "permission_intersection": ["read", "write"],
        "policy_decision": {
            "policy_id": "policy://enterprise-sandbox-demo",
            "decision": "allow_with_approval",
            "allowed_permissions": ["read", "write"],
            "decision_reason": "report generation is allowed, final dispatch requires approval",
        },
        "sandbox_context": {
            "sandbox_id": "sandbox-demo-001",
            "environment": "enterprise-agent-os",
            "control_plane": {"id": "agent-os", "version": "2026.03"},
        },
        "network_proxy_meta": {
            "proxy_id": "proxy-demo-001",
            "status": "proxyed",
            "endpoint": "https://proxy.enterprise.internal",
        },
        "snapshot_ref": {
            "snapshot_id": "snapshot-demo-001",
            "snapshot_hash": snapshot_hash,
            "previous_snapshot_hash": None,
            "storage": "kernel_bundle.json",
        },
        "event_chain": event_chain,
        "hashes": {
            "event_hash": None if last_event is None else f"sha256:{last_event.event_hash}",
            "previous_event_hash": (
                None
                if last_event is None or last_event.previous_event_hash is None
                else f"sha256:{last_event.previous_event_hash}"
            ),
            "chain_hash": None if last_event is None else f"sha256:{last_event.chain_hash}",
        },
        "verifier_ref": "mvk://sep-replay",
        "signature_ref": {
            "signature_id": "sig-demo-001",
            "signer": "enterprise-security",
            "signature": _sha256_prefixed_text(json.dumps(replay_verdict, sort_keys=True)),
        },
    }
    return receipt


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    intent_path = _write_json(OUTPUT_DIR / "intent.json", _build_intent())
    policy_path = _write_json(OUTPUT_DIR / "policy.json", _build_policy())
    kernel_bundle_path = _copy_kernel_bundle(OUTPUT_DIR)
    _record_sep_trace(OUTPUT_DIR / "trace.jsonl", intent_path, policy_path)

    store = LocalEvidenceStore(OUTPUT_DIR / "trace.jsonl")
    sep_bundle = export_sep_bundle(
        store.list(),
        OUTPUT_DIR / "sep.bundle.json",
        kernel_bundle_path="kernel_bundle.json",
    )
    sep_verify = verify_sep_bundle(OUTPUT_DIR / "sep.bundle.json")
    replay_verdict = _mvk_replay(kernel_bundle_path)
    replay_verdict["sep_verify"] = sep_verify
    _write_json(OUTPUT_DIR / "replay_verdict.json", replay_verdict)

    receipt = _build_audit_receipt(
        sep_bundle=sep_bundle,
        kernel_bundle_path=kernel_bundle_path,
        replay_verdict=replay_verdict,
    )
    receipt_ok = None
    if validate_enterprise_sandbox_receipt_data is not None:
        receipt_ok, receipt_errors = validate_enterprise_sandbox_receipt_data(receipt)
        if not receipt_ok:
            raise SystemExit(
                "enterprise sandbox receipt validation failed: "
                + "; ".join(receipt_errors)
            )
    _write_json(OUTPUT_DIR / "audit_receipt.json", receipt)

    print(
        json.dumps(
            {
                "scenario": SCENARIO,
                "output_dir": str(OUTPUT_DIR),
                "artifacts": [
                    "intent.json",
                    "policy.json",
                    "trace.jsonl",
                    "sep.bundle.json",
                    "replay_verdict.json",
                    "audit_receipt.json",
                ],
                "replay_verdict": replay_verdict.get("verdict"),
                "receipt_valid": receipt_ok,
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
