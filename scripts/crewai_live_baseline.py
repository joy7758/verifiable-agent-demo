#!/usr/bin/env python3
"""Run a minimal live CrewAI task and emit normalized metadata as JSON."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("CREWAI_TESTING", "true")
os.environ.setdefault("CREWAI_TRACING_ENABLED", "false")

from crewai import Agent, Crew, Task
from crewai.events.listeners.tracing.utils import set_suppress_tracing_messages
from crewai.llms.base_llm import BaseLLM


class DeterministicPaperEvalLLM(BaseLLM):
    def __init__(self, expected_output: str):
        super().__init__(model="mock-crewai-paper-eval", provider="custom")
        self.expected_output = expected_output

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
            "Thought: I can complete this task with a deterministic local CrewAI response.\n"
            f"Final Answer: {self.expected_output}"
        )


def build_expected_output(task: dict[str, Any]) -> str:
    input_payload = task.get("input_payload", {})
    if "expected_answer" in input_payload:
        return str(input_payload["expected_answer"])
    if task.get("tamper_case"):
        return "tamper scenario observed"
    if task.get("category") == "approval_required":
        return "approval-dependent action completed"
    if task.get("category") == "budget_constrained":
        return "budget-sensitive action completed"
    return f"{task['title']} completed"


def build_description(task: dict[str, Any]) -> str:
    payload = json.dumps(task["input_payload"], sort_keys=True, ensure_ascii=False)
    return (
        f"Task title: {task['title']}\n"
        f"Goal: {task['goal']}\n"
        f"Category: {task['category']}\n"
        f"Input payload: {payload}\n"
        "Return the expected concise outcome only."
    )


def run_task(task: dict[str, Any]) -> dict[str, Any]:
    expected_output = build_expected_output(task)
    description = build_description(task)
    llm = DeterministicPaperEvalLLM(expected_output)
    set_suppress_tracing_messages(True)

    agent = Agent(
        role="paper evaluation agent",
        goal="execute a deterministic local task through CrewAI",
        backstory="Minimal live CrewAI baseline for the execution-evidence paper.",
        llm=llm,
        verbose=False,
    )
    crew_task = Task(
        description=description,
        expected_output=expected_output,
        agent=agent,
    )
    crew = Crew(
        agents=[agent],
        tasks=[crew_task],
        verbose=False,
        tracing=False,
    )
    result = crew.kickoff()
    result_text = getattr(result, "raw", str(result)).strip()

    return {
        "framework": "CrewAI",
        "live_framework": True,
        "agent_role": agent.role,
        "agent_goal": agent.goal,
        "task_description": description,
        "expected_output": expected_output,
        "result_text": result_text,
        "llm_model": llm.model,
        "events": [
            {"step": "crewai_agent_initialized", "detail": agent.role},
            {"step": "crewai_task_built", "detail": task["title"]},
            {"step": "crewai_kickoff_started", "detail": task["input_payload"]["operation"]},
            {"step": "crewai_kickoff_finished", "detail": result_text},
        ],
        "native_surface": {
            "framework": "CrewAI",
            "task_prompt": description,
            "expected_output": expected_output,
            "tool_usage_declared": task["input_payload"]["requested_tool"],
            "mock_local_llm": True,
        },
    }


def main() -> int:
    task = json.load(sys.stdin)
    output = run_task(task)
    print(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
