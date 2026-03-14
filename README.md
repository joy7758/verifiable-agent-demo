# Verifiable Agent Demo

The minimal end-to-end demonstration for the Digital Biosphere Architecture stack.

This repository connects persona, interaction semantics, governance context, execution traceability, and audit evidence into one walkthrough. It is a demo and reference path rather than a general-purpose framework.

```mermaid
flowchart LR
    Persona["Persona (POP)"] --> Intent["Intent Object (AIP)"]
    Intent --> Governance["Governance Check"]
    Governance --> Trace["Execution Trace"]
    Trace --> Audit["Audit Evidence (ARO)"]
```

## What this demo proves

- a portable persona-oriented entry point can be projected into runtime
- explicit intent and action objects can be emitted before execution
- result objects can be emitted after execution
- execution steps can be recorded as inspectable evidence
- audit-facing artifacts can be exported as bounded outputs

## Architecture Path in this Demo

- Persona Layer -> POP-aligned persona context carried into the run
- Interaction Layer -> intent, action, and result objects emitted under `interaction/`
- Governance Layer -> referenced as the control checkpoint for runtime policy and budget constraints
- Execution Integrity Layer -> runtime execution trace and verifiable execution context
- Audit Evidence Layer -> ARO-style exported evidence artifacts

This repository does not claim a full Token Governor integration. It demonstrates a minimal aligned path across the broader stack, with explicit governance checkpoint references in the emitted interaction and result objects.

## How to read this demo

This demo is a guided path across layers. It is not the normative specification for each layer, and it points outward to the canonical repositories for those layers: [digital-biosphere-architecture](https://github.com/joy7758/digital-biosphere-architecture), [persona-object-protocol](https://github.com/joy7758/persona-object-protocol), [agent-intent-protocol](https://github.com/joy7758/agent-intent-protocol), [token-governor](https://github.com/joy7758/token-governor), and [aro-audit](https://github.com/joy7758/aro-audit).

## Expected Artifacts

- `interaction/intent.json`
- `interaction/action.json`
- `interaction/result.json`
- `evidence/example_audit.json`
- `evidence/result.json`
- `evidence/crew_demo_audit.json`

Current concrete examples in this repository include:

- `docs/quick-walkthrough.md`
- `docs/interaction-flow.md`
- `docs/shortest-validation-loop.md`

## Run the Demo

### Fastest local path

```bash
python3 -m demo.agent
```

### Scripted wrapper

```bash
bash scripts/run_demo.sh
```

### Existing CrewAI demo path

```bash
bash scripts/setup_framework_venv.sh
.venv/bin/python crew/crew_demo.py
```

Environment notes:

- Python 3 is sufficient for the minimal local path.
- The optional CrewAI and LangChain paths should run from a git-ignored local `.venv/` created by `scripts/setup_framework_venv.sh`.
- The pinned framework helper environment currently uses `crewai 1.10.1`, `langchain 1.2.12`, and `langchain-core 1.2.18`.
- CrewAI currently requires Python `<3.14`.
- Both demo paths use deterministic local mock data and do not require external API calls.

## Paper Evaluation Harness

This repository now includes a paper-ready evaluation harness for
`Execution Evidence Architecture for Agentic Software Systems: From Intent Objects to Verifiable Audit Receipts`.

Primary entry points:

- `make eval-baseline`
- `make eval-evidence`
- `make eval-external-baseline`
- `make eval-framework-pair`
- `make eval-langchain-pair`
- `make eval-ablation`
- `make falsification-checks`
- `make human-review-kit`
- `make review-sample`
- `make compare`
- `make paper-eval`
- `make top-journal-pack`

Supporting material:

- [Task Suite](docs/paper_support/task-suite.md)
- [Export Format](docs/paper_support/export-format.md)
- [Review Workflow](docs/paper_support/review-workflow.md)
- [Comparison Workflow](docs/paper_support/comparison-workflow.md)
- [External Baseline](docs/paper_support/external-baseline.md)
- [Same-Framework Comparison](docs/paper_support/same-framework-comparison.md)
- [LangChain Comparison](docs/paper_support/langchain-comparison.md)
- [Ablation Study](docs/paper_support/ablation-study.md)
- [Human Review Study](docs/paper_support/human-review-study.md)
- [Falsification Workflow](docs/paper_support/falsification-workflow.md)

Generated outputs:

- `artifacts/runs/<task_id>/<mode>/`
- `docs/paper_support/comparison-summary.md`
- `docs/paper_support/comparison-summary.csv`
- `artifacts/metrics/comparison-summary.json`
- `docs/paper_support/external-baseline-summary.md`
- `docs/paper_support/framework-pair-summary.md`
- `docs/paper_support/langchain-pair-summary.md`
- `docs/paper_support/ablation-summary.md`
- `docs/paper_support/falsification-summary.md`
- `artifacts/human_review/synthetic-review-summary.json`

## English LaTeX Manuscript Draft

The repository also includes a manuscript draft grounded in the current implemented harness and checked-in metrics:

- [paper/latex/README.md](paper/latex/README.md)
- `paper/latex/main.tex`
- `paper/latex/main.pdf` after local compilation

## Related Repositories

- [digital-biosphere-architecture](https://github.com/joy7758/digital-biosphere-architecture) - system overview and canonical architecture hub
- [persona-object-protocol](https://github.com/joy7758/persona-object-protocol) - portable persona object layer
- [agent-intent-protocol](https://github.com/joy7758/agent-intent-protocol) - semantic interaction layer
- [token-governor](https://github.com/joy7758/token-governor) - runtime governance and budget-policy control layer
- [aro-audit](https://github.com/joy7758/aro-audit) - audit evidence and conformance-oriented verification layer

## Minimal Reference Surface

- `interaction/` for explicit interaction objects
- `evidence/` for audit and result artifacts
- `demo/` and `crew/` for runnable entry points
- `integration/` for persona and intent adapters
- `docs/spec/` for schema notes and example payloads

## Further Reading

- [Quick Walkthrough](docs/quick-walkthrough.md)
- [Interaction Flow](docs/interaction-flow.md)
- [Shortest Validation Loop](docs/shortest-validation-loop.md)
- [Independent Verification](docs/independent-verification.md)
- [Architecture](docs/architecture.md)
- [Demo Artifacts](docs/demo-artifacts.md)
<!-- render-refresh: 20260311T205242Z -->
