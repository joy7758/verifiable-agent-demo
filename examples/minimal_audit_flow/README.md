# Minimal Audit Flow

This example shows the smallest reference-implementation path in this
repository:

- simulate a bounded agent action
- capture an execution trace with the new `verifiable_agent` surface
- generate an audit record
- write exportable evidence artifacts into this example's own output directory

## How to run

From the repository root:

```bash
python3 examples/minimal_audit_flow/run.py
```

## What it generates

Running the example creates:

- `examples/minimal_audit_flow/output/audit-record.json`
- `examples/minimal_audit_flow/output/evidence-bundle.json`

The output directory is created on demand by the script.

## Relationship to the existing demo

The existing `demo/` and `crew/` paths are kept as-is. This example is the
minimal reference-implementation path layered on top of the current repository,
not a replacement for the original demo entry points.
