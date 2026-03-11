# Audit Record Schema

## Purpose

This document describes the early-stage minimal audit record schema used by the
current reference implementation surface. The schema is derived from the
repository's existing evidence artifacts and keeps only the smallest stable
fields needed for a bounded review flow.

## Required fields

- `schema`
- `task`
- `result`
- `persona`
- `timestamp`
- `agent_id`
- `framework`
- `execution`
- `audit`

## Optional fields

- `audit.evidence_path`
- `metadata`

## Minimal example payload

```json
{
  "schema": "aro-demo-v0",
  "task": "test task",
  "result": "task completed",
  "persona": {
    "id": "demo-persona",
    "role": "research-agent",
    "permissions": ["write_evidence"]
  },
  "timestamp": 1773172609.1262112,
  "agent_id": "demo-agent-001",
  "framework": "demo-agent",
  "execution": {
    "status": "completed",
    "trace": [
      "persona loaded",
      "agent action executed",
      "audit evidence generated"
    ]
  },
  "audit": {
    "record_type": "ARO-compatible",
    "evidence_path": "evidence/example_audit.json"
  },
  "metadata": {}
}
```

## Notes / compatibility scope

- This is an early-stage minimal schema.
- It is intended to support the current reference implementation in this
  repository, including the existing demo artifacts.
- It is not a final standard, not a complete evidence model, and not a promise
  of production-grade interoperability.
