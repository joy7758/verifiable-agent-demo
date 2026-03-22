# Demo Receipt Validation Report

This patch closes the remaining enterprise sandbox receipt gap.

Canonical validator:

- `from aro_audit.receipt_validation import validate_receipt`
- `python -m aro_audit.receipt_validation artifacts/enterprise_sandbox_demo/audit_receipt.json`

Demo-side contract:

- `receipt_valid`: `true` or `false`
- `receipt_validation_profile`: currently `minimal`
- `receipt_validation_reason`: reviewer-facing summary string

Fixtures:

- `tests/fixtures/enterprise_sandbox_receipt.valid.json`
- `tests/fixtures/enterprise_sandbox_receipt.invalid.json`

Checks added:

- valid fixture returns `receipt_valid = true`
- invalid fixture returns `receipt_valid = false`
- summary output no longer uses `null` as a success placeholder
