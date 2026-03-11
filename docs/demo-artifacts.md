# Demo Artifacts

This demo emits bounded artifacts intended for inspection, explanation, and audit-oriented review.

Each artifact represents one layer or one handoff in the broader architecture.

## Interaction artifacts

- `interaction/intent.json` - declared task intent before execution
- `interaction/action.json` - concrete runtime action proposal
- `interaction/result.json` - interaction outcome object

## Evidence artifacts

- `evidence/example_audit.json` - minimal local ARO-compatible audit record
- `evidence/result.json` - exported result object for audit-side handoff
- `evidence/crew_demo_audit.json` - CrewAI-specific audit record

The demo is illustrative rather than exhaustive.
