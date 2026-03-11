from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from verifiable_agent import AuditRecorder, ExecutionTrace


def main() -> None:
    output_dir = ROOT_DIR / "examples" / "minimal_audit_flow" / "output"
    audit_path = output_dir / "audit-record.json"
    bundle_path = output_dir / "evidence-bundle.json"

    persona = {
        "id": "demo-persona",
        "role": "research-agent",
        "permissions": ["write_evidence"],
    }
    trace = ExecutionTrace(metadata={"framework": "minimal-local"})
    trace.add_step("persona loaded", timestamp=time.time())
    trace.add_step(
        "agent action executed",
        detail="simulated bounded action",
        timestamp=time.time(),
        data={"task": "test task"},
    )
    trace.add_step("audit evidence generated", timestamp=time.time())

    recorder = AuditRecorder(framework="minimal-reference-example", root_dir=ROOT_DIR)
    bundle = recorder.build_bundle(
        task="test task",
        result="task completed",
        persona=persona,
        trace=trace,
        agent_id="minimal-example-agent-001",
        evidence_path="examples/minimal_audit_flow/output/audit-record.json",
        metadata={"source": "examples/minimal_audit_flow/run.py"},
        summary="Minimal local audit flow using the additive reference implementation shell.",
        references=[
            "schemas/audit-record.schema.json",
            "schemas/execution-trace.schema.json",
        ],
    )

    recorder.write(bundle.audit_record, audit_path)
    recorder.write(bundle, bundle_path)

    print(json.dumps(bundle.to_dict(), indent=2))


if __name__ == "__main__":
    main()
