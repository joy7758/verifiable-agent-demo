# Exported Bundle Contract

Each exported run bundle contains exactly five JSON files:

- `intent.json`
- `action.json`
- `result.json`
- `trace.json`
- `receipt.json`

The contract is shared across the local baseline, the full evidence chain, the live-framework baselines, the same-framework wrapped paths, and the four ablations.

Review logic:

- recomputes bundle identity consistency across all five files
- recomputes integrity digests and receipt artifact digests
- distinguishes reviewable success, policy-blocked, tamper-detected, and partial outcomes
- rejects falsified bundles when cross-file contradictions or digest mismatches appear

Included sample bundles cover:

- local baseline versus full evidence chain
- minimal live CrewAI and LangChain baselines and their wrapped evidence-chain counterparts
- four single-stage ablations
- one policy-blocked bundle
- one tamper-detected bundle
- representative falsification cases for payload tampering, replay mismatch, and policy-bypass claims
