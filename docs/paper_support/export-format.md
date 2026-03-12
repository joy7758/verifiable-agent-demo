# Export Format

Each run exports exactly five JSON files under `artifacts/runs/<task_id>/<mode>/`:

- `intent.json`
- `action.json`
- `result.json`
- `trace.json`
- `receipt.json`

Modes:

- `baseline` is a trace-only approximation. The file set is present for deterministic comparison, but `intent_captured`, `policy.checked`, and `receipt_exported` remain false.
- `external_baseline` is a CrewAI-like native logging baseline. It may preserve a raw task snapshot for replayability, but it does not claim explicit intent, governance, integrity, or receipt support.
- `no_intent`, `no_governance`, `no_integrity`, and `no_receipt` are ablations that keep the same five-file contract while explicitly neutralizing one capability.
- `evidence_chain` persists explicit intent, a governance decision, an execution-integrity result, and a bounded receipt.

Field contracts:

- `intent.json` answers what was intended and binds the task goal to a frozen input payload snapshot.
- `action.json` answers what was authorized and records the policy decision, budget policy, and approval policy.
- `result.json` answers what outcome occurred, including policy-blocked and tamper-detected cases.
- `trace.json` answers what was executed and whether integrity verification was performed, skipped, or failed.
- `receipt.json` answers what evidence was exported and which file digests bound the run bundle.

Schemas live under `schemas/paper_eval/`:

- `task.schema.json`
- `intent.schema.json`
- `action.schema.json`
- `result.schema.json`
- `trace.schema.json`
- `receipt.schema.json`

The implementation is intentionally thin: it uses local deterministic shims instead of direct runtime coupling to the reference repositories. The naming aligns lightly with AIP, Token Governor, FDO kernel checkpoints, and ARO receipts.
