# Shortest Validation Loop

This document compresses the demo into the smallest review loop that still maps to real files in the repository. The current loop is a working draft and a bounded verification surface, not the whole stack.

## Step 1: apply persona context

The minimal path applies persona context by loading the local object in `integration/pop_adapter.py` before the action runs.

Practical entry point:

```bash
python3 -m demo.agent
```

Review surface after this step:

- `interaction/intent.json` under `actor_ref`

## Step 2: emit intent and action objects

The bounded action is first expressed as interaction objects in `demo/agent.py`. The wrapper script keeps the loop short:

```bash
bash scripts/run_demo.sh
```

The CrewAI path is also available:

```bash
bash scripts/setup_framework_venv.sh
.venv/bin/python crew/crew_demo.py
```

Review surface after this step:

- `interaction/intent.json`
- `interaction/action.json`

## Step 3: execute the bounded task

The runtime executes a deterministic local task after the interaction objects are emitted.

## Step 4: emit trace, result, and evidence

The demo writes its review artifacts into the repository:

- `interaction/result.json`
- `evidence/example_audit.json`
- `evidence/result.json`
- `evidence/crew_demo_audit.json`

The key review fields are `status`, `execution.trace`, `audit.evidence_path`, and `governance_decision_ref`.

## Step 5: export or inspect the artifact

The result object can be inspected without the rest of the runtime:

```bash
python3 -m json.tool interaction/result.json
```

The audit-facing record remains available:

```bash
python3 -m json.tool evidence/example_audit.json
```

For the CrewAI path:

```bash
python3 -m json.tool evidence/crew_demo_audit.json
```

## Step 6: independently verify the result

Independent verification in this repository means checking the emitted record as a bounded verification surface.

The reviewer does not need to understand the whole system. They only need to check that:

- `actor_ref` shows the attached identity-bearing actor
- `intent` and `action` match the bounded task
- `status` and `evidence_refs` match the emitted outcome
- `execution.trace` shows the minimal ordered flow
- `audit.evidence_path` matches the file being reviewed

For a compact reviewer guide, see [independent-verification.md](independent-verification.md).
