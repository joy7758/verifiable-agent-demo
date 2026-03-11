# Shortest Validation Loop

This document compresses the demo into the smallest review loop that still maps
to real files in the repository. The current loop is a working draft and a
bounded verification surface, not the whole stack.

## Step 1: apply persona or policy context

The minimal path applies persona context by loading the local object in
`integration/pop_adapter.py` before the action runs.

Practical entry point:

```bash
python3 -m demo.agent
```

Review surface after this step:

- `evidence/example_audit.json` under `persona`

## Step 2: run a bounded action

The bounded action is the deterministic task in `demo/agent.py`. The wrapper
script keeps the loop short:

```bash
bash scripts/run_demo.sh
```

The CrewAI path is also available:

```bash
venv/bin/python crew/crew_demo.py
```

## Step 3: emit trace / receipt / evidence

The demo writes its review artifact into the repository:

- `evidence/example_audit.json`
- `evidence/crew_demo_audit.json`

The key review fields are `task`, `result`, `execution.trace`, and
`audit.evidence_path`.

## Step 4: export or inspect the artifact

The artifact can be inspected without the rest of the runtime:

```bash
python3 -m json.tool evidence/example_audit.json
```

Or for the CrewAI path:

```bash
python3 -m json.tool evidence/crew_demo_audit.json
```

## Step 5: independently verify the result

Independent verification in this repository means checking the emitted record
as a bounded verification surface.

The reviewer does not need to understand the whole system. They only need to
check that:

- `persona` shows the attached identity object
- `task` and `result` match the bounded action
- `execution.trace` shows the minimal ordered flow
- `audit.evidence_path` matches the file being reviewed

For a compact reviewer guide, see [independent-verification.md](independent-verification.md).
