from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from integration.aro_adapter import generate_audit, write_audit_record
from integration.intent_adapter import (
    build_action,
    build_intent,
    build_result,
    write_json_artifact,
)
from integration.pop_adapter import load_persona


DEFAULT_TASK = "test task"
DEFAULT_CORRELATION_ID = "demo-run-001"
REPO_SAMPLE_TIMESTAMP = 1773261564.422378
LIVE_OUTPUT_ROOT = "artifacts/demo_output"


def _join_ref(output_root: Path, relative_path: str) -> str:
    relative = Path(relative_path)
    if output_root in {Path(""), Path(".")}:
        return relative.as_posix()
    return (output_root / relative).as_posix()


def run_agent(
    task: str,
    *,
    output_root: str = LIVE_OUTPUT_ROOT,
    correlation_id: str = DEFAULT_CORRELATION_ID,
    timestamp: float | None = None,
) -> dict[str, object]:
    persona = load_persona()
    timestamp_value = time.time() if timestamp is None else timestamp
    output_base = Path(output_root)
    result_text = "task completed"

    intent_path = _join_ref(output_base, "interaction/intent.json")
    action_path = _join_ref(output_base, "interaction/action.json")
    interaction_result_path = _join_ref(output_base, "interaction/result.json")
    evidence_audit_path = _join_ref(output_base, "evidence/example_audit.json")
    evidence_result_path = _join_ref(output_base, "evidence/result.json")

    intent_object = build_intent(task, persona, correlation_id)
    action_object = build_action(task, persona, correlation_id)

    write_json_artifact(intent_object, intent_path)
    write_json_artifact(action_object, action_path)

    audit_record = generate_audit(
        task=task,
        result=result_text,
        persona=persona,
        timestamp=timestamp_value,
        agent_id="demo-agent-001",
        evidence_path=evidence_audit_path,
        metadata={
            "intent_ref": intent_path,
            "action_ref": action_path,
            "governance_checkpoint_ref": "governor://checkpoints/demo-local-001",
            "correlation_id": correlation_id,
        },
    )

    write_audit_record(audit_record, evidence_audit_path)
    result_object = build_result(
        persona,
        correlation_id,
        output_refs=[f"artifact://demo/task-result/{correlation_id}"],
        evidence_refs=[
            evidence_audit_path,
            evidence_result_path,
        ],
    )
    write_json_artifact(result_object, interaction_result_path)
    write_json_artifact(result_object, evidence_result_path)

    return {
        "intent": intent_object,
        "action": action_object,
        "result": result_object,
        "audit_record": audit_record,
        "paths": {
            "intent": intent_path,
            "action": action_path,
            "interaction_result": interaction_result_path,
            "audit": evidence_audit_path,
            "evidence_result": evidence_result_path,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the minimal verifiable-agent demo.")
    parser.add_argument("--task", default=DEFAULT_TASK)
    parser.add_argument("--output-root", default=LIVE_OUTPUT_ROOT)
    parser.add_argument("--correlation-id", default=DEFAULT_CORRELATION_ID)
    parser.add_argument("--timestamp", type=float, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(
        json.dumps(
            run_agent(
                args.task,
                output_root=args.output_root,
                correlation_id=args.correlation_id,
                timestamp=args.timestamp,
            ),
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
