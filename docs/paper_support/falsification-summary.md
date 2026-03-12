# Falsification Summary

Negative-control bundles derived from review-passing evidence-chain runs. Each scenario preserves or corrupts specific bundle properties to test whether the independent review contract can reject malformed evidence.

Source bundles by status:

- `pass`: 11 source `evidence_chain` runs.
- `policy_blocked`: 3 source `evidence_chain` runs.

| scenario | source_status | total_bundles | detected_bundles | detection_rate | intent_captured_true | policy_checked_true | execution_verified_true | receipt_exported_true |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| missing_intent | pass | 11 | 11 | 1.0 | 0 | 11 | 11 | 11 |
| missing_policy | pass | 11 | 11 | 1.0 | 11 | 0 | 11 | 11 |
| forged_receipt | pass | 11 | 11 | 1.0 | 11 | 11 | 11 | 0 |
| payload_tamper | pass | 11 | 11 | 1.0 | 11 | 11 | 0 | 0 |
| false_tamper_claim | pass | 11 | 11 | 1.0 | 11 | 11 | 0 | 11 |
| cross_run_replay_mismatch | pass | 11 | 11 | 1.0 | 11 | 11 | 0 | 11 |
| cross_bundle_receipt_swap | pass | 11 | 11 | 1.0 | 11 | 11 | 11 | 0 |
| policy_bypass_claim | policy_blocked | 3 | 3 | 1.0 | 3 | 3 | 3 | 3 |

Scenario definitions are documented in `docs/paper_support/falsification-workflow.md`.
