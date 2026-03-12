# Review Workflow

The review script inspects a generated run directory and emits a machine-readable verdict.

Default JSON mode:

```bash
python3 scripts/review_bundle.py --run-dir artifacts/runs/task-001/evidence_chain
```

Optional human-readable mode:

```bash
python3 scripts/review_bundle.py --run-dir artifacts/runs/task-001/evidence_chain --human
```

The review answers these four questions explicitly:

- was intent captured?
- was policy checked?
- was execution verified?
- was receipt exported?

Decision rules are deterministic and combine field checks with independent bundle corroboration:

- `intent_captured` requires `intent.json.intent_captured == true` and a non-null `intent` object.
- `policy_checked` requires `action.json.policy.checked == true` and a persisted decision object.
- `execution_verified` requires `trace.json.integrity.checked == true`, `verification_status == "verified"`, consistent bundle identity fields, and integrity digests that recompute against the current bundle.
- `receipt_exported` requires `receipt.json.receipt_exported == true`, the bounded four-artifact digest list, and receipt digests that recompute against the current bundle.

Expected outcomes:

- Baseline runs should typically review as `partial`.
- External baseline runs should typically review as `partial`.
- Ablation runs should typically review as `partial`, except where a policy block or tamper detection remains explicit.
- Evidence-chain runs should review as `pass`, `policy_blocked`, or `tamper_detected`.
- Falsified bundles should review as `partial`, unless the bundle independently corroborates a true policy block or tamper condition.

Make target:

```bash
make review-sample
```

Negative-control workflow:

```bash
make falsification-checks
```
