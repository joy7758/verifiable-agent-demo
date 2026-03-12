# Top-Journal Mode Comparison

Generated from actual artifacts across baseline, external baseline, four ablations, and the full evidence chain.

| mode | total_tasks | intent_captured_true | policy_checked_true | execution_verified_true | receipt_exported_true | avg_explicitness | avg_replayability | avg_tamper_sensitivity | avg_audit_boundedness | avg_integration_surface |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 16 | 0 | 0 | 0 | 0 | 1.0 | 3.0 | 0.0 | 2.0 | 1.0 |
| external_baseline | 16 | 0 | 0 | 0 | 0 | 1.0 | 4.0 | 0.0 | 2.0 | 1.0 |
| no_intent | 16 | 0 | 16 | 11 | 0 | 3.0 | 4.0 | 4.81 | 4.0 | 4.0 |
| no_governance | 16 | 16 | 0 | 14 | 0 | 2.0 | 5.0 | 5.0 | 4.0 | 4.0 |
| no_integrity | 16 | 16 | 16 | 0 | 16 | 5.0 | 5.0 | 0.0 | 5.0 | 4.0 |
| no_receipt | 16 | 16 | 16 | 11 | 0 | 4.0 | 4.0 | 4.81 | 2.0 | 4.0 |
| evidence_chain | 16 | 16 | 16 | 11 | 16 | 5.0 | 5.0 | 4.81 | 5.0 | 5.0 |

Heuristic definitions are documented in `docs/paper_support/ablation-study.md`.
