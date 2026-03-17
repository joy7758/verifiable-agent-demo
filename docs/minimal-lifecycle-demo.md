# Minimal Lifecycle Demo

This demo shows policy-controlled lifecycle transitions for autonomous agents.

The goal is not to build a large lifecycle system. The goal is to show a small,
reviewable lifecycle loop that stays aligned with the Lifecycle Object and
Lifecycle Receipt semantics defined in the sibling protocol repositories.

## What this demo runs

The script emits:

- one parent `lifecycle_object`
- one child `lifecycle_object`
- five lifecycle receipts: `init`, `activate`, `fork`, `merge`, `terminate`
- one machine-readable verifier summary
- one human-readable verifier summary

## Run steps

From the repository root:

```bash
python3 scripts/minimal_lifecycle_demo.py
```

## Artifact paths

The script writes to `artifacts/lifecycle_demo/`:

- `artifacts/lifecycle_demo/objects/parent.lifecycle_object.json`
- `artifacts/lifecycle_demo/objects/child.lifecycle_object.json`
- `artifacts/lifecycle_demo/receipts/init.receipt.json`
- `artifacts/lifecycle_demo/receipts/activate.receipt.json`
- `artifacts/lifecycle_demo/receipts/fork.receipt.json`
- `artifacts/lifecycle_demo/receipts/merge.receipt.json`
- `artifacts/lifecycle_demo/receipts/terminate.receipt.json`
- `artifacts/lifecycle_demo/verify.json`
- `artifacts/lifecycle_demo/verify.txt`

## Expected output

Expected console output is close to:

```text
Wrote lifecycle objects to artifacts/lifecycle_demo/objects
Wrote 5 receipts to artifacts/lifecycle_demo/receipts
Wrote verifier outputs to artifacts/lifecycle_demo/verify.json and artifacts/lifecycle_demo/verify.txt
Verification status: ok (5 receipts checked)
```

The verifier summary should report:

- `status: "ok"`
- `verified_transitions: ["init", "activate", "fork", "merge", "terminate"]`
- `parent_final_state: "ACTIVE"`
- `child_final_state: "TERMINATED"`
- `merge_mode: "runnable_transition"`
- `checks.merged_branch_closed: "ok"`

## What the verifier checks

The verifier in this demo is intentionally small. It checks:

- the transition sequence matches the minimal lifecycle rules across parent and child
- each receipt hash recomputes against the protected transition fields
- each receipt links to the prior receipt hash for the right subject
- parent and child share lineage continuity across the fork
- the child branch merges into an existing parent target
- a merged branch only closes with `terminate`, not by returning to `ACTIVE`
- both final `lifecycle_object` files agree with the last accepted receipts

This is enough for a reviewable lifecycle walkthrough without turning the demo
repository into another full protocol implementation.

The runnable loop in this round is:

- born
- active
- fork
- merge
- terminate-after-merge
- verify
