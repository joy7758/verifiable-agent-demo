def build_audit_record(task, result, persona, timestamp, agent_id):
    return {
        "schema": "aro-demo-v0",
        "task": task,
        "result": result,
        "persona": persona,
        "timestamp": timestamp,
        "agent_id": agent_id,
        "execution": {
            "status": "completed",
            "trace": [
                "persona loaded",
                "agent action executed",
                "audit evidence generated",
            ],
        },
        "audit": {
            "record_type": "ARO-compatible",
            "evidence_path": "evidence/example_audit.json",
        },
    }

