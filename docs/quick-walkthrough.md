# Quick Walkthrough

This demo is meant to be readable in a few minutes. The artifacts below already
exist in the repository and show the four core steps.

## 1. Persona attached

The demo loads a small persona object before execution starts.
Artifact file: [`../evidence/example_audit.json`](../evidence/example_audit.json)
The `persona` block shows the attached identity object and permissions.

## 2. Runtime action

The agent executes a deterministic task and returns a simple result.
Artifact file: [`../evidence/crew_demo_audit.json`](../evidence/crew_demo_audit.json)
The `task`, `result`, and `framework` fields show the runtime action that completed.

## 3. Execution trace

The run emits a compact ordered trace of what happened.
Artifact file: [`../evidence/example_audit.json`](../evidence/example_audit.json)
The `execution.trace` field records persona loading, agent action, and evidence generation.

## 4. Evidence output

The trace and metadata are written as an ARO-compatible audit record.
Artifact file: [`../evidence/crew_demo_audit.json`](../evidence/crew_demo_audit.json)
The `audit` block and `metadata` fields show the exportable evidence output.
