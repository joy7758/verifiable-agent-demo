# Minimal Lifecycle Demo

This demo shows policy-controlled lifecycle transitions for autonomous agents.

The goal is not to build a large lifecycle system. The goal is to show a small,
reviewable lifecycle loop that stays aligned with the Lifecycle Object and
Lifecycle Receipt semantics defined in the sibling protocol repositories.

## What this demo runs

The script emits:

- one `lifecycle_object`
- four lifecycle receipts: `init`, `activate`, `fork`, `terminate`
- one verifier summary

`merge` is kept as a document sample in this round so the runnable path stays
small.

## Run steps

From the repository root:

```bash
python3 scripts/minimal_lifecycle_demo.py
```

## Artifact paths

The script writes to `artifacts/lifecycle_demo/`:

- `artifacts/lifecycle_demo/lifecycle_object.json`
- `artifacts/lifecycle_demo/receipts/init.receipt.json`
- `artifacts/lifecycle_demo/receipts/activate.receipt.json`
- `artifacts/lifecycle_demo/receipts/fork.receipt.json`
- `artifacts/lifecycle_demo/receipts/terminate.receipt.json`
- `artifacts/lifecycle_demo/verify.json`

## Expected output

Expected console output is close to:

```text
Wrote lifecycle object to artifacts/lifecycle_demo/lifecycle_object.json
Wrote 4 receipts to artifacts/lifecycle_demo/receipts
Wrote verifier output to artifacts/lifecycle_demo/verify.json
Verification status: ok (4 receipts checked)
```

The verifier summary should report:

- `status: "ok"`
- `verified_transitions: ["init", "activate", "fork", "terminate"]`
- `final_state: "TERMINATED"`
- `merge_mode: "document_sample_only"`

## What the verifier checks

The verifier in this demo is intentionally small. It checks:

- the transition sequence matches the minimal lifecycle rules
- each receipt hash recomputes against the protected transition fields
- each receipt links to the prior receipt hash
- the final `lifecycle_object` agrees with the last receipt

This is enough for a reviewable lifecycle walkthrough without turning the demo
repository into another full protocol implementation.

## Merge sample

If a merge were included, the receipt shape would stay the same and only change
the transition semantics:

```json
{
  "transition_type": "merge",
  "subject_instance_id": "agent-alpha-child",
  "related_instance_id": "agent-alpha",
  "prior_state": "ACTIVE",
  "next_state": "MERGED"
}
```

That sample stays document-only in this round so the runnable loop remains:

- born
- active
- fork
- terminate
- verify
