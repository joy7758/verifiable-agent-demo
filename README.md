# Verifiable Agent Demo

A minimal demonstration of verifiable AI agent execution.

This repository demonstrates verifiable execution for AI agents.

This project shows how an AI agent action can produce a verifiable audit record.

Architecture layers:

Identity -> Persona Object (POP)
Execution -> Agent runtime
Audit -> ARO evidence record
Governance -> Token Governor

Demo flow:

1. Agent receives task
2. Agent executes action
3. Execution trace recorded
4. Evidence bundle generated

Output example:

`evidence/example_audit.json`
