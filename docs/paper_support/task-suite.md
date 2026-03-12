# Task Suite

The paper evaluation harness adds a deterministic 16-task suite under `evaluation/tasks/`.

Category rationale:

- `read_only_query` isolates the question of whether explicit intent and bounded evidence are still emitted when the task is low-risk.
- `tool_call` forces the harness to record a concrete requested action, tool reference, and parameters.
- `budget_constrained` aligns lightly with Token Governor ideas by making cost or token limits first-class policy objects.
- `approval_required` checks whether privileged operations remain blocked until an explicit approval token is present.
- `tamper_scenario` aligns lightly with execution-integrity work by requiring a digest mismatch to become visible in the evidence-chain path.

Why this supports the paper claims:

- The suite is machine-readable and deterministic, so the comparison is reproducible.
- Every task emits the same five-file export shape, which keeps reviewer expectations stable.
- The tasks include both positive controls and negative controls: budget overflow, missing approval, and tamper conditions.
- Reference repositories were used only to align terms such as intent object, budget window, checkpoint chain, and receipt, not as hard runtime dependencies.

Validation command:

```bash
python3 scripts/validate_task_suite.py
```
