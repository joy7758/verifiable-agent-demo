# Same-Framework Comparison

This workflow compares two conditions built on the same live CrewAI runtime path:

- `external_baseline`: minimal live CrewAI execution with default observability-like export only
- `external_evidence_chain`: the same live CrewAI execution path wrapped by explicit intent capture, governance persistence, integrity validation, and bounded receipt export

Why this comparison exists:

- It reduces the risk that the paper's main result depends only on a local non-framework control path.
- It isolates the effect of the evidence layer while keeping the underlying framework runtime fixed.
- It gives the manuscript a paired comparison that is harder to dismiss as a straw baseline.

Run it with:

```bash
make eval-framework-pair
```

Generated outputs:

- `docs/paper_support/framework-pair-summary.md`
- `docs/paper_support/framework-pair-summary.csv`
- `artifacts/metrics/framework-pair-summary.json`

Interpretation:

- The two modes share the same deterministic local CrewAI helper and the same task suite.
- `external_baseline` preserves framework-native execution shape but does not claim explicit intent, governance, integrity, or bounded receipt support.
- `external_evidence_chain` adds the full evidence-preserving export contract around that same runtime path.

Limits:

- This is still a minimal live integration rather than a production CrewAI deployment.
- The comparison remains evidence-shape oriented rather than semantic-quality oriented.
