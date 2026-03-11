"""Evidence bundle helpers for the minimal reference implementation surface."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .trace import ExecutionTrace


@dataclass
class EvidenceBundle:
    """This is a minimal early-stage reference implementation surface."""

    audit_record: Dict[str, Any]
    trace: Optional[ExecutionTrace] = None
    summary: Optional[str] = None
    artifacts: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"audit_record": dict(self.audit_record)}
        if self.trace is not None:
            payload["trace"] = self.trace.to_dict()
        if self.summary:
            payload["summary"] = self.summary
        if self.artifacts:
            payload["artifacts"] = list(self.artifacts)
        if self.references:
            payload["references"] = list(self.references)
        if self.metadata:
            payload["metadata"] = dict(self.metadata)
        return payload
