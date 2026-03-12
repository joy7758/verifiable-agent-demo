# Falsification Workflow

The falsification workflow derives negative-control bundles from review-passing `evidence_chain` runs and re-runs the same third-party review logic against those derived bundles.

Outputs:

- `artifacts/reviews/falsification/<task_id>/<scenario>/`
- `docs/paper_support/falsification-summary.md`
- `docs/paper_support/falsification-summary.csv`
- `artifacts/metrics/falsification-summary.json`

Run it with:

```bash
make falsification-checks
```

Or call the CLI directly:

```bash
python3 scripts/run_falsification_checks.py
```

Current scenarios:

- `missing_intent`: removes the explicit intent object while keeping the rest of the bundle internally rebound.
- `missing_policy`: removes the persisted governance decision while keeping integrity and receipt bindings intact.
- `forged_receipt`: alters one receipt digest after export so that the receipt no longer matches the bundle it claims to summarize.
- `payload_tamper`: changes the exported result payload after the trace and receipt digests have already been bound.
- `false_tamper_claim`: declares a tamper outcome without an independently corroborating digest mismatch.
- `cross_run_replay_mismatch`: swaps in a trace from a different review-passing run while rebinding the receipt to the current bundle.
- `cross_bundle_receipt_swap`: swaps in a receipt from a different review-passing bundle without updating its artifact digests.
- `policy_bypass_claim`: rewrites a policy-blocked bundle to claim successful completion while leaving the blocked policy decision in place.

Design intent:

- Most scenarios derive from the `evidence_chain` runs that the review script already marks as `pass`; `policy_bypass_claim` derives from the reviewable `policy_blocked` runs.
- Single-surface removals (`missing_intent`, `missing_policy`) are rebound so that the bundle stays internally consistent except for the targeted capability.
- Tamper-oriented and replay-oriented scenarios (`forged_receipt`, `payload_tamper`, `false_tamper_claim`, `cross_run_replay_mismatch`, `cross_bundle_receipt_swap`) are designed to show that the review script does more than check field presence.
- Policy-result contradiction is tested by `policy_bypass_claim`, which now depends on cross-file coherence checks rather than on digest mismatch alone.

Interpretation rules:

- A successful falsification check means the derived bundle is no longer reviewed as `pass`.
- Selective failures are expected:
  - `missing_intent` should clear `intent_captured` while preserving policy, execution, and receipt checks.
  - `missing_policy` should clear `policy_checked` while preserving the other positive checks.
  - `forged_receipt` should clear only `receipt_exported`.
  - `payload_tamper` should break execution verification and receipt verification together.
  - `false_tamper_claim` should be rejected as `partial`, not accepted as a true tamper detection.
  - `cross_run_replay_mismatch` should clear execution verification while leaving the receipt correctly bound to the mutated bundle.
  - `cross_bundle_receipt_swap` should clear only `receipt_exported`.
  - `policy_bypass_claim` should be rejected because the claimed completed result contradicts the persisted blocked policy decision.

Limits:

- The workflow derives from deterministic local artifacts rather than from an external adversarial actor.
- It validates the independent review contract and digest binding logic, not semantic task correctness.
