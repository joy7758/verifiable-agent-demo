"""Minimal CrewAI adapter.

This is a minimal adapter for the reference implementation surface.
It is not a complete production-grade CrewAI integration.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from verifiable_agent import AuditRecorder, EvidenceBundle, ExecutionTrace


def build_crewai_trace(task_description: str) -> ExecutionTrace:
    """Create a compact trace shape aligned with the current CrewAI demo."""

    trace = ExecutionTrace(metadata={"framework": "CrewAI"})
    trace.add_step("persona loaded")
    trace.add_step(
        "CrewAI agent executed task",
        data={"task_description": task_description},
    )
    trace.add_step("audit evidence generated")
    return trace


def record_crewai_run(
    *,
    task_description: str,
    result_text: str,
    persona: Mapping[str, Any],
    agent_id: str = "crew-demo-agent-001",
    evidence_path: Optional[str] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> EvidenceBundle:
    """Bridge a bounded CrewAI-style run into the minimal audit surface.

    The function accepts plain data so the module stays importable even when
    CrewAI is not installed in the current environment.
    """

    trace = build_crewai_trace(task_description)
    recorder = AuditRecorder(framework="CrewAI")
    return recorder.build_bundle(
        task=task_description,
        result=result_text,
        persona=persona,
        trace=trace,
        agent_id=agent_id,
        evidence_path=evidence_path,
        metadata=metadata,
        summary="Minimal CrewAI adapter output for the reference implementation surface.",
        artifacts=[] if evidence_path is None else [evidence_path],
    )
