# Falsification Summary

Negative-control bundles derived from review-passing evidence-chain runs. Each scenario preserves or corrupts specific bundle properties to test whether the independent review contract can reject malformed evidence.

Source bundles: 11 review-passing `evidence_chain` runs.

| scenario | total_bundles | detected_bundles | detection_rate | intent_captured_true | policy_checked_true | execution_verified_true | receipt_exported_true |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| missing_intent | 11 | 11 | 1.0 | 0 | 11 | 11 | 11 |
| missing_policy | 11 | 11 | 1.0 | 11 | 0 | 11 | 11 |
| forged_receipt | 11 | 11 | 1.0 | 11 | 11 | 11 | 0 |
| payload_tamper | 11 | 11 | 1.0 | 11 | 11 | 0 | 0 |
| false_tamper_claim | 11 | 11 | 1.0 | 11 | 11 | 0 | 11 |

Scenario definitions are documented in `docs/paper_support/falsification-workflow.md`.
