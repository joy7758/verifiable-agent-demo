# Demo Artifacts

This demo emits bounded artifacts intended for inspection, explanation, and audit-oriented review.

Each artifact represents one layer or one handoff in the broader architecture.

## Interaction artifacts

- `interaction/intent.json` - declared task intent before execution
- `interaction/action.json` - concrete runtime action proposal
- `interaction/result.json` - interaction outcome object

## Evidence artifacts

- `evidence/example_audit.json` - deterministic tracked sample audit record
- `evidence/result.json` - exported result object for audit-side handoff
- `evidence/crew_demo_audit.json` - CrewAI-specific audit record
- `evidence/sample-manifest.json` - checksum manifest for the tracked sample bundle

Live local runs write fresh artifacts under `artifacts/demo_output/`.

## Enterprise sandbox artifact chain

The fixed enterprise sandbox scenario writes a single reviewer-facing directory:

- `artifacts/enterprise_sandbox_demo/intent.json`
- `artifacts/enterprise_sandbox_demo/policy.json`
- `artifacts/enterprise_sandbox_demo/trace.jsonl`
- `artifacts/enterprise_sandbox_demo/sep.bundle.json`
- `artifacts/enterprise_sandbox_demo/replay_verdict.json`
- `artifacts/enterprise_sandbox_demo/audit_receipt.json`

The demo is illustrative rather than exhaustive.
