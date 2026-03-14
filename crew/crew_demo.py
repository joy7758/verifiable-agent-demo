from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("CREWAI_TESTING", "true")
os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")

from crewai import Agent, Crew, Task
from crewai.events.listeners.tracing.utils import set_suppress_tracing_messages
from crewai.llms.base_llm import BaseLLM

from integration.aro_adapter import generate_audit, write_audit_record
from integration.intent_adapter import (
    build_action,
    build_intent,
    build_result,
    write_json_artifact,
)
from integration.pop_adapter import load_persona


DEFAULT_OUTPUT_ROOT = "artifacts/demo_output/crewai"


def _join_ref(output_root: Path, relative_path: str) -> str:
    relative = Path(relative_path)
    if output_root in {Path(""), Path(".")}:
        return relative.as_posix()
    return (output_root / relative).as_posix()


class MockCrewAILLM(BaseLLM):
    def __init__(self):
        super().__init__(model="mock-crewai-local", provider="custom")

    def call(
        self,
        messages,
        tools=None,
        callbacks=None,
        available_functions=None,
        from_task=None,
        from_agent=None,
        response_model=None,
    ):
        self._token_usage["successful_requests"] += 1
        return (
            "Thought: I can complete this task with a deterministic local response.\n"
            "Final Answer: task completed"
        )


def run_crewai_demo(
    *,
    output_root: str = DEFAULT_OUTPUT_ROOT,
    timestamp: float | None = None,
) -> tuple[str, dict[str, object]]:
    persona = load_persona()
    correlation_id = "crew-demo-001"
    llm = MockCrewAILLM()
    output_base = Path(output_root)
    set_suppress_tracing_messages(True)

    intent_path = _join_ref(output_base, "interaction/intent.json")
    action_path = _join_ref(output_base, "interaction/action.json")
    interaction_result_path = _join_ref(output_base, "interaction/result.json")
    evidence_audit_path = _join_ref(output_base, "evidence/crew_demo_audit.json")
    evidence_result_path = _join_ref(output_base, "evidence/result.json")

    agent = Agent(
        role="research agent",
        goal="execute task with verifiable audit",
        backstory="demo agent for governance layer",
        llm=llm,
        verbose=False,
    )

    task = Task(
        description="analyze a simple task",
        expected_output="task completed",
        agent=agent,
    )

    intent_object = build_intent(task.description, persona, correlation_id)
    action_object = build_action(
        task.description,
        persona,
        correlation_id,
        parameters={
            "task": task.description,
            "expected_output": task.expected_output,
            "framework": "CrewAI",
        },
    )
    write_json_artifact(intent_object, intent_path)
    write_json_artifact(action_object, action_path)

    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=False,
        tracing=False,
    )

    result = crew.kickoff()
    result_text = getattr(result, "raw", str(result))

    audit = generate_audit(
        task=task.description,
        result=result_text,
        persona=persona,
        timestamp=time.time() if timestamp is None else timestamp,
        agent_id="crew-demo-agent-001",
        framework="CrewAI",
        trace=[
            "persona loaded",
            "CrewAI agent executed task",
            "audit evidence generated",
        ],
        evidence_path=evidence_audit_path,
        metadata={
            "llm_model": llm.model,
            "task_description": task.description,
            "expected_output": task.expected_output,
            "intent_ref": intent_path,
            "action_ref": action_path,
            "governance_checkpoint_ref": "governor://checkpoints/demo-local-001",
            "correlation_id": correlation_id,
        },
    )
    write_audit_record(audit, evidence_audit_path)

    result_object = build_result(
        persona,
        correlation_id,
        output_refs=["artifact://demo/task-result/crew-demo-001"],
        evidence_refs=[
            evidence_audit_path,
            evidence_result_path,
        ],
    )
    write_json_artifact(result_object, interaction_result_path)
    write_json_artifact(result_object, evidence_result_path)

    return result_text, {
        "intent": intent_object,
        "action": action_object,
        "result": result_object,
        "audit": audit,
        "paths": {
            "intent": intent_path,
            "action": action_path,
            "interaction_result": interaction_result_path,
            "audit": evidence_audit_path,
            "evidence_result": evidence_result_path,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the deterministic CrewAI demo.")
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--timestamp", type=float, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result_text, audit = run_crewai_demo(
        output_root=args.output_root,
        timestamp=args.timestamp,
    )
    print(result_text)
    print(json.dumps(audit, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
