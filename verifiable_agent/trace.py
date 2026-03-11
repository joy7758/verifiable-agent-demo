"""Execution trace helpers for the minimal reference implementation surface."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class TraceStep:
    """A lightweight trace event that can still collapse to the demo trace format."""

    message: str
    detail: Optional[str] = None
    timestamp: Optional[float] = None
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"message": self.message}
        if self.detail:
            payload["detail"] = self.detail
        if self.timestamp is not None:
            payload["timestamp"] = self.timestamp
        if self.data:
            payload["data"] = dict(self.data)
        return payload


@dataclass
class ExecutionTrace:
    """This is a minimal early-stage reference implementation surface."""

    status: str = "completed"
    metadata: Dict[str, Any] = field(default_factory=dict)
    steps: List[TraceStep] = field(default_factory=list)

    def add_step(
        self,
        message: str,
        *,
        detail: Optional[str] = None,
        timestamp: Optional[float] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> TraceStep:
        step = TraceStep(
            message=message,
            detail=detail,
            timestamp=timestamp,
            data=dict(data or {}),
        )
        self.steps.append(step)
        return step

    def add_event(
        self,
        message: str,
        *,
        detail: Optional[str] = None,
        timestamp: Optional[float] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> TraceStep:
        return self.add_step(
            message,
            detail=detail,
            timestamp=timestamp,
            data=data,
        )

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "status": self.status,
            "trace": [step.message for step in self.steps],
        }
        if self.metadata:
            payload["metadata"] = dict(self.metadata)

        rich_events = [
            step.to_dict()
            for step in self.steps
            if step.detail is not None or step.timestamp is not None or step.data
        ]
        if rich_events:
            payload["events"] = rich_events

        return payload
