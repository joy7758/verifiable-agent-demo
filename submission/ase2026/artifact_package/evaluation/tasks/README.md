# Paper Task Suite

This directory stores the stable machine-readable task suite used by the paper evaluation harness.

The suite contains 16 deterministic local tasks grouped into five categories:

- `read_only_query` checks whether a run captures intent and evidence even when the task is non-mutating.
- `tool_call` checks whether the bundle records concrete tool authorization and execution details.
- `budget_constrained` checks whether governance captures budget limits and budget-block outcomes.
- `approval_required` checks whether human-approval gates are explicit and reviewable.
- `tamper_scenario` checks whether the evidence-chain path reacts to integrity failures.

Each task file is JSON and follows `schemas/paper_eval/task.schema.json`.
