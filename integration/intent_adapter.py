import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "0.1.0-draft"


def actor_ref_from_persona(persona):
    return f"pop://personas/{persona['id']}"


def build_intent(task, persona, correlation_id, constraints=None):
    return {
        "schema_version": SCHEMA_VERSION,
        "object_type": "agent_intent",
        "intent": {
            "operation": "execute_demo_task",
            "summary": task,
        },
        "actor_ref": actor_ref_from_persona(persona),
        "constraints": constraints or {
            "max_steps": 1,
            "network_access": "disabled",
            "deterministic_local_mock": True,
        },
        "target_ref": "runtime://local-demo/task-runner",
        "expected_result": {"summary": "task completed"},
        "policy_context_ref": "governor://checkpoints/demo-local-001",
        "correlation_id": correlation_id,
    }


def build_action(task, persona, correlation_id, parameters=None):
    return {
        "schema_version": SCHEMA_VERSION,
        "object_type": "agent_action",
        "action": {
            "name": "execute_local_demo_task",
            "summary": f"Run the deterministic demo task: {task}",
        },
        "actor_ref": actor_ref_from_persona(persona),
        "execution_mode": "direct",
        "tool_ref": "runtime://local-demo/mock-task-runner",
        "parameters": parameters or {"task": task},
        "side_effect_class": "read_only",
        "policy_checkpoint_ref": "governor://checkpoints/demo-local-001",
        "correlation_id": correlation_id,
    }


def build_result(persona, correlation_id, status="completed", error=None, output_refs=None, evidence_refs=None):
    payload = {
        "schema_version": SCHEMA_VERSION,
        "object_type": "agent_result",
        "status": status,
        "actor_ref": actor_ref_from_persona(persona),
        "correlation_id": correlation_id,
        "output_refs": output_refs or [f"artifact://demo/task-result/{correlation_id}"],
        "evidence_refs": evidence_refs or ["evidence/example_audit.json"],
        "execution_trace_ref": f"trace://demo/{correlation_id}",
        "governance_decision_ref": "governor://checkpoints/demo-local-001",
    }
    if error is not None:
        payload["error"] = error
    return payload


def write_json_artifact(payload, relative_path):
    output_path = ROOT_DIR / relative_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return output_path
