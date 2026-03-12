# Export Format

Each run exports exactly five JSON files under `artifacts/runs/<task_id>/<mode>/`:

- `intent.json`
- `action.json`
- `result.json`
- `trace.json`
- `receipt.json`

Modes:

- `baseline` is a trace-only approximation. The file set is present for deterministic comparison, but `intent_captured`, `policy.checked`, and `receipt_exported` remain false.
- `external_baseline` is a minimal live CrewAI logging baseline. It preserves a real framework execution surface plus a raw task snapshot for replayability, but it does not claim explicit intent, governance, integrity, or receipt support.
- `external_evidence_chain` uses the same live CrewAI runtime path as `external_baseline`, but wraps it with explicit intent capture, governance persistence, integrity validation, and bounded receipt export.
- `langchain_baseline` is a minimal live LangChain callback/logging baseline. It preserves a real LCEL execution surface plus a raw task snapshot for replayability, but it does not claim explicit intent, governance, integrity, or receipt support.
- `langchain_evidence_chain` uses the same live LangChain runtime path as `langchain_baseline`, but wraps it with explicit intent capture, governance persistence, integrity validation, and bounded receipt export.
- `no_intent`, `no_governance`, `no_integrity`, and `no_receipt` are ablations that keep the same five-file contract while explicitly neutralizing one capability.
- `evidence_chain` persists explicit intent, a governance decision, an execution-integrity result, and a bounded receipt.

Field contracts:

- `intent.json` answers what was intended and binds the task goal to a frozen input payload snapshot.
- `action.json` answers what was authorized and records the policy decision, budget policy, and approval policy.
- `result.json` answers what outcome occurred, including policy-blocked and tamper-detected cases.
- `trace.json` answers what was executed and whether integrity verification was performed, skipped, or failed. Its integrity section binds `intent.json`, `action.json`, and `result.json`.
- `receipt.json` answers what evidence was exported and which file digests bound the run bundle. Its artifact list carries the digest for `trace.json`, which avoids a self-referential digest inside the trace payload itself.

Schemas live under `schemas/paper_eval/`:

- `task.schema.json`
- `intent.schema.json`
- `action.schema.json`
- `result.schema.json`
- `trace.schema.json`
- `receipt.schema.json`

The implementation is intentionally thin: it uses local deterministic shims instead of direct runtime coupling to the reference repositories. The naming aligns lightly with AIP, Token Governor, FDO kernel checkpoints, and ARO receipts.

Review-oriented notes:

- The review script recomputes bundle identity consistency (`task_id`, `run_id`, `mode`) across all five files.
- The review script recomputes the integrity digests recorded in `trace.json` and the artifact digests recorded in `receipt.json`.
- A declared tamper condition is only accepted when the stored expected digests independently disagree with the current bundle contents.
