import json
import time

from integration.aro_adapter import generate_audit, write_audit_record
from integration.intent_adapter import (
    build_action,
    build_intent,
    build_result,
    write_json_artifact,
)
from integration.pop_adapter import load_persona


def run_agent(task):
    persona = load_persona()
    correlation_id = "demo-run-001"
    timestamp = time.time()
    result = "task completed"
    intent_object = build_intent(task, persona, correlation_id)
    action_object = build_action(task, persona, correlation_id)

    write_json_artifact(intent_object, "interaction/intent.json")
    write_json_artifact(action_object, "interaction/action.json")
    audit_record = generate_audit(
        task=task,
        result=result,
        persona=persona,
        timestamp=timestamp,
        agent_id="demo-agent-001",
        evidence_path="evidence/example_audit.json",
        metadata={
            "intent_ref": "interaction/intent.json",
            "action_ref": "interaction/action.json",
            "governance_checkpoint_ref": "governor://checkpoints/demo-local-001",
            "correlation_id": correlation_id,
        },
    )

    write_audit_record(audit_record, "evidence/example_audit.json")
    result_object = build_result(
        persona,
        correlation_id,
        output_refs=["artifact://demo/task-result/demo-run-001"],
        evidence_refs=[
            "evidence/example_audit.json",
            "evidence/result.json",
        ],
    )
    write_json_artifact(result_object, "interaction/result.json")
    write_json_artifact(result_object, "evidence/result.json")

    return {
        "intent": intent_object,
        "action": action_object,
        "result": result_object,
        "audit_record": audit_record,
    }


if __name__ == "__main__":
    print(json.dumps(run_agent("test task"), indent=2))
