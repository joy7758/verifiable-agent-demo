# External Baseline vs Evidence Chain

Generated from actual artifacts comparing the CrewAI-like native logging baseline against the full evidence chain.

| mode | total_tasks | intent_captured_true | policy_checked_true | execution_verified_true | receipt_exported_true | avg_explicitness | avg_replayability | avg_tamper_sensitivity | avg_audit_boundedness | avg_integration_surface |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| external_baseline | 16 | 0 | 0 | 0 | 0 | 1.0 | 4.0 | 0.0 | 2.0 | 1.0 |
| evidence_chain | 16 | 16 | 16 | 11 | 16 | 5.0 | 5.0 | 4.81 | 5.0 | 5.0 |

Heuristic definitions are documented in `docs/paper_support/external-baseline.md`.
