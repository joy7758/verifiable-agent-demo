# Independent Verification

## Smallest review object

The smallest review object in this repository is `evidence/example_audit.json`.
It is the minimal audit artifact for the shortest validation loop.

## How to view it

Generate or refresh the artifact:

```bash
bash scripts/run_demo.sh
```

Inspect it:

```bash
python3 -m json.tool evidence/example_audit.json
```

## What a reviewer needs to check

A reviewer does not need to understand the whole runtime. The minimum fields
to inspect are:

- `persona`
- `task`
- `result`
- `execution.status`
- `execution.trace`
- `audit.evidence_path`

For the CrewAI path, `evidence/crew_demo_audit.json` adds `framework` and
`metadata` fields that can be reviewed the same way.

## Current verification boundary

The current verification boundary is a bounded verification surface over the
emitted audit record. A reviewer can check that the demo produced a stable,
exportable evidence artifact for a bounded action and that the record is
self-consistent with the local demo flow.

## What this still cannot prove

This repository does not yet prove full runtime isolation, cryptographic
sealing, external anchoring, or policy enforcement by default. It is a compact
demo for reviewable evidence output, not the whole stack.
