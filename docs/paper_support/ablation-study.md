# Ablation Study

The ablation study adds four modes derived from the full `evidence_chain`:

- `no_intent`: removes the explicit intent object.
- `no_governance`: removes policy persistence and policy enforcement.
- `no_integrity`: removes digest and checkpoint verification.
- `no_receipt`: removes bounded receipt export.

Architectural purpose:

- `no_intent` tests whether replayable execution evidence is still understandable without a front-loaded intent claim.
- `no_governance` tests whether budget and approval semantics remain reviewable when policy is removed.
- `no_integrity` tests whether tamper sensitivity survives without verification.
- `no_receipt` tests whether audit boundedness survives without a receipt layer.

Scoring:

- The study uses the same deterministic rule-based metrics already defined for the harness:
  `explicitness`, `replayability`, `tamper_sensitivity`, `audit_boundedness`, and `integration_surface`.
- Heuristic details remain documented in `docs/paper_support/comparison-workflow.md`.

Top-level comparison table:

- `baseline`
- `external_baseline`
- `no_intent`
- `no_governance`
- `no_integrity`
- `no_receipt`
- `evidence_chain`

Run command:

```bash
make eval-ablation
```

Generated outputs:

- `docs/paper_support/ablation-summary.md`
- `docs/paper_support/ablation-summary.csv`
- `artifacts/metrics/ablation-summary.json`
