import json
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


def generate_audit(
    task,
    result,
    persona,
    timestamp,
    agent_id="demo-agent-001",
    framework="demo-agent",
    trace=None,
    evidence_path="evidence/example_audit.json",
    metadata=None,
):
    execution_trace = trace or [
        "persona loaded",
        "agent action executed",
        "audit evidence generated",
    ]

    return {
        "schema": "aro-demo-v0",
        "task": task,
        "result": result,
        "persona": persona,
        "timestamp": timestamp,
        "agent_id": agent_id,
        "framework": framework,
        "execution": {
            "status": "completed",
            "trace": execution_trace,
        },
        "audit": {
            "record_type": "ARO-compatible",
            "evidence_path": evidence_path,
        },
        "metadata": metadata or {},
    }


def build_audit_record(task, result, persona, timestamp, agent_id):
    return generate_audit(
        task=task,
        result=result,
        persona=persona,
        timestamp=timestamp,
        agent_id=agent_id,
    )


def write_audit_record(record, evidence_path):
    output_path = ROOT_DIR / evidence_path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return output_path
