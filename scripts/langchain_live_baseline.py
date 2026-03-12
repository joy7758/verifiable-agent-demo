#!/usr/bin/env python3
"""Run a minimal live LangChain pipeline and emit normalized metadata as JSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.language_models.chat_models import SimpleChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


class DeterministicLangChainChatModel(SimpleChatModel):
    response_text: str
    model_name: str = "mock-langchain-paper-eval"

    @property
    def _llm_type(self) -> str:
        return "deterministic-paper-eval"

    @property
    def _identifying_params(self) -> dict[str, Any]:
        return {"model_name": self.model_name}

    def _call(self, messages, stop=None, run_manager=None, **kwargs) -> str:
        return self.response_text


class RecordingCallbackHandler(BaseCallbackHandler):
    def __init__(self) -> None:
        self.events: list[dict[str, str]] = []

    def on_chain_start(self, serialized, inputs, **kwargs) -> None:
        name = serialized.get("name") if isinstance(serialized, dict) else None
        if name == "ChatPromptTemplate":
            self.events.append({"step": "langchain_prompt_template_started", "detail": "ChatPromptTemplate"})
        elif name:
            self.events.append({"step": "langchain_chain_started", "detail": str(name)})

    def on_chain_end(self, outputs, **kwargs) -> None:
        detail = str(outputs)
        self.events.append({"step": "langchain_chain_finished", "detail": detail[:160]})

    def on_chat_model_start(self, serialized, messages, **kwargs) -> None:
        name = serialized.get("name") if isinstance(serialized, dict) else "chat_model"
        self.events.append({"step": "langchain_chat_model_started", "detail": f"{name}:{len(messages)}"})

    def on_llm_end(self, response, **kwargs) -> None:
        try:
            text = response.generations[0][0].text
        except Exception:  # pragma: no cover - defensive
            text = str(response)
        self.events.append({"step": "langchain_llm_finished", "detail": text[:160]})


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


def build_human_prompt(task: dict[str, Any]) -> str:
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
    human_prompt = build_human_prompt(task)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a deterministic local LangChain baseline for paper evaluation."),
            ("human", "{task_prompt}"),
        ]
    )
    model = DeterministicLangChainChatModel(response_text=expected_output)
    chain = prompt | model | StrOutputParser()

    callback = RecordingCallbackHandler()
    result_text = chain.invoke(
        {"task_prompt": human_prompt},
        config={"callbacks": [callback], "run_name": "paper-langchain-baseline"},
    )

    events = [{"step": "langchain_invoke_started", "detail": task["input_payload"]["operation"]}]
    events.extend(callback.events)
    events.append({"step": "langchain_invoke_finished", "detail": result_text})

    return {
        "framework": "LangChain",
        "live_framework": True,
        "agent_role": "langchain runnable chain",
        "agent_goal": "execute a deterministic local task through LangChain",
        "task_description": human_prompt,
        "expected_output": expected_output,
        "result_text": result_text,
        "llm_model": model.model_name,
        "events": events,
        "native_surface": {
            "framework": "LangChain",
            "pipeline": "ChatPromptTemplate|SimpleChatModel|StrOutputParser",
            "task_prompt": human_prompt,
            "expected_output": expected_output,
            "tool_usage_declared": task["input_payload"]["requested_tool"],
            "mock_local_llm": True,
            "callbacks_recorded": True,
        },
    }


def main() -> int:
    task = json.load(sys.stdin)
    output = run_task(task)
    print(json.dumps(output, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
