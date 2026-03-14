# Quick Walkthrough

This demo is meant to be readable in a few minutes. The artifacts below are deterministic tracked samples in the repository and show the five-layer flow.

## 1. Persona attached

The demo loads a small persona object before execution starts.
Artifact file: [`../interaction/intent.json`](../interaction/intent.json)
The `actor_ref` and task context show which persona-bearing actor is about to act.

## 2. Intent declared

The demo emits a machine-readable intent object before execution.
Artifact file: [`../interaction/intent.json`](../interaction/intent.json)
The `intent`, `constraints`, and `correlation_id` fields show what is being requested.

## 3. Action and governance checkpoint

The runtime emits a concrete action object with a governance checkpoint reference.
Artifact file: [`../interaction/action.json`](../interaction/action.json)
The `action`, `execution_mode`, and `policy_checkpoint_ref` fields show the proposed runtime action.

## 4. Result emitted

After execution, the demo emits a result object.
Artifact file: [`../interaction/result.json`](../interaction/result.json)
The `status`, `output_refs`, and `evidence_refs` fields show the interaction outcome.

## 5. Evidence output

The trace and metadata are written as an ARO-compatible audit record.
Artifact file: [`../evidence/example_audit.json`](../evidence/example_audit.json)
The `execution.trace`, `audit`, and `metadata` fields show the exportable evidence output.
