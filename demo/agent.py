import json
import time
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT_DIR / "evidence" / "example_audit.json"


def run_agent(task):
    result = {
        "task": task,
        "result": "task completed",
        "timestamp": time.time(),
        "agent_id": "demo-agent-001",
    }

    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    return result


if __name__ == "__main__":
    print(json.dumps(run_agent("test task"), indent=2))
