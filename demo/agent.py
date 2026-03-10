import json
import time

from integration.aro_adapter import generate_audit, write_audit_record
from integration.pop_adapter import load_persona


def run_agent(task):
    persona = load_persona()
    timestamp = time.time()
    result = "task completed"
    audit_record = generate_audit(
        task=task,
        result=result,
        persona=persona,
        timestamp=timestamp,
        agent_id="demo-agent-001",
        evidence_path="evidence/example_audit.json",
    )

    write_audit_record(audit_record, "evidence/example_audit.json")

    return audit_record


if __name__ == "__main__":
    print(json.dumps(run_agent("test task"), indent=2))
