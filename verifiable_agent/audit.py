"""Audit recording helpers for the minimal reference implementation surface."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Union

from .evidence import EvidenceBundle
from .trace import ExecutionTrace


@dataclass
class AuditRecorder:
    """This is a minimal early-stage reference implementation surface."""

    schema: str = "aro-demo-v0"
    record_type: str = "ARO-compatible"
    framework: str = "verifiable-agent"
    root_dir: Optional[Path] = None

    def build_record(
        self,
        *,
        task: str,
        result: str,
        persona: Mapping[str, Any],
        trace: ExecutionTrace,
        agent_id: str,
        timestamp: Optional[float] = None,
        evidence_path: Optional[str] = None,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        record: Dict[str, Any] = {
            "schema": self.schema,
            "task": task,
            "result": result,
            "persona": dict(persona),
            "timestamp": float(timestamp if timestamp is not None else time.time()),
            "agent_id": agent_id,
            "framework": self.framework,
            "execution": trace.to_dict(),
            "audit": {
                "record_type": self.record_type,
            },
            "metadata": dict(metadata or {}),
        }
        if evidence_path:
            record["audit"]["evidence_path"] = evidence_path
        return record

    def build_bundle(
        self,
        *,
        task: str,
        result: str,
        persona: Mapping[str, Any],
        trace: ExecutionTrace,
        agent_id: str,
        evidence_path: Optional[str] = None,
        timestamp: Optional[float] = None,
        metadata: Optional[Mapping[str, Any]] = None,
        summary: Optional[str] = None,
        artifacts: Optional[list[str]] = None,
        references: Optional[list[str]] = None,
    ) -> EvidenceBundle:
        record = self.build_record(
            task=task,
            result=result,
            persona=persona,
            trace=trace,
            agent_id=agent_id,
            timestamp=timestamp,
            evidence_path=evidence_path,
            metadata=metadata,
        )
        return EvidenceBundle(
            audit_record=record,
            trace=trace,
            summary=summary,
            artifacts=list(artifacts or ([] if evidence_path is None else [evidence_path])),
            references=list(references or []),
            metadata={"framework": self.framework},
        )

    def write(self, payload: Union[EvidenceBundle, Mapping[str, Any]], path: Union[str, Path]) -> Path:
        output_path = Path(path)
        if not output_path.is_absolute() and self.root_dir is not None:
            output_path = self.root_dir / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data = payload.to_dict() if isinstance(payload, EvidenceBundle) else dict(payload)
        output_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return output_path
