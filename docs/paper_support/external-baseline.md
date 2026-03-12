# External Baseline

The external baseline adds a deterministic `external_baseline` mode under `artifacts/runs/<task_id>/external_baseline/`.

Design choice:

- The baseline now runs a minimal live CrewAI task for each paper-eval task using the repository's local `venv/` and a deterministic mock LLM.
- It preserves framework-native concepts such as agent initialization, crew task construction, crew kickoff, and task completion.
- It still does not claim live end-to-end CrewAI governance, integrity, or bounded receipt support.

What is real vs shimmed:

- Real: every `external_baseline` run executes `Crew.kickoff()` through the installed CrewAI runtime in `venv/`.
- Normalized: the five exported JSON files are still written by the paper harness after the CrewAI run so that every evaluation condition shares the same output contract.
- Honest omission: no explicit intent object, no governance checkpoint, no integrity proof, and no bounded receipt are claimed for this mode.

Why it matters:

- It gives the paper a stronger "default framework observability surface" than the local trace-only baseline because the framework execution is real rather than purely shape-mimicked.
- It remains deterministic and cheap to reproduce.

Run command:

```bash
make eval-external-baseline
```

Environment note:

- This mode requires the repository's local `venv/bin/python`, because CrewAI is installed there rather than under the system `python3`.

Generated comparison outputs:

- `docs/paper_support/external-baseline-summary.md`
- `docs/paper_support/external-baseline-summary.csv`
- `artifacts/metrics/external-baseline-summary.json`
