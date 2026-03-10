# Verifiable Agent Demo

A minimal demonstration of verifiable AI agent execution.

This repository demonstrates verifiable execution for AI agents.

This project shows how an AI agent action can produce a verifiable audit record.

Architecture layers:

Identity -> Persona Object (POP)
Execution -> Agent runtime
Audit -> ARO evidence record
Governance -> Token Governor

Demo architecture:

Persona (POP)
-> Agent execution
-> Audit evidence (ARO compatible)

Demo flow:

1. Agent receives task
2. Agent executes action
3. Execution trace recorded
4. Evidence bundle generated

Output example:

`evidence/example_audit.json`

## Framework Integration

This demo can run with CrewAI.

CrewAI currently requires Python `<3.14`, so this repository uses a local `venv`
with Python 3.13 for the integration example.

Setup:

```bash
python3.13 -m venv venv
venv/bin/pip install crewai
```

Example:

```bash
venv/bin/python crew/crew_demo.py
```

The CrewAI example uses a deterministic local mock LLM so the governance
pipeline can run without external API keys.
