import json
import time
from pathlib import Path

from integration.aro_adapter import build_audit_record
from integration.pop_adapter import load_persona


ROOT_DIR = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT_DIR / "evidence" / "example_audit.json"


def run_agent(task):
    persona = load_persona()
    timestamp = time.time()
    result = "task completed"
    audit_record = build_audit_record(
        task=task,
        result=result,
        persona=persona,
        timestamp=timestamp,
        agent_id="demo-agent-001",
    )

    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(json.dumps(audit_record, indent=2) + "\n", encoding="utf-8")

    return audit_record


if __name__ == "__main__":
    print(json.dumps(run_agent("test task"), indent=2))
