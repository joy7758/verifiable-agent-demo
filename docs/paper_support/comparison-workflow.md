# Comparison Workflow

The comparison step consumes actual generated artifacts and emits:

- `docs/paper_support/comparison-summary.md`
- `docs/paper_support/comparison-summary.csv`
- `artifacts/metrics/comparison-summary.json`

Run it with:

```bash
make compare
```

Scoring rules are deterministic and rule-based. Each metric is scored on a 0-5 integer scale per run, then averaged per mode.

Metric definitions:

- `explicitness`: one point each for explicit intent capture, explicit policy check, explicit authorization state, explicit result summary, and a receipt that maps the four reviewer questions to concrete fields.
- `replayability`: one point each for frozen input payload, requested action parameters, deterministic seed, at least four ordered trace steps, and a receipt with at least four artifact digests.
- `tamper_sensitivity`: one point each for integrity checking enabled, subject digests present, expected digests present, explicit verification status, and the correct terminal status (`verified` for non-tamper tasks or `tamper_detected` for tamper tasks).
- `audit_boundedness`: one point each for receipt export enabled, exactly five declared bundle files, a stable allowed-file list, four artifact digests, and four reviewer-question mappings.
- `integration_surface`: one point each for intent capture, requested action, policy check, integrity check, and receipt export.

The comparison is intentionally honest about limits:

- It measures deterministic local shims, not live integration against the reference repositories.
- The scores are evidence-shape metrics, not semantic-quality metrics.
- Budget and approval outcomes are simulated from task metadata rather than external systems.
