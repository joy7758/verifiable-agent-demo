# Verifiable Agent Execution

Minimal infrastructure for auditable AI agent systems.

This repository demonstrates a governance pipeline for AI agents built on three layers:

Identity -> Execution -> Audit

Architecture:

POP (Persona Object Protocol)
Portable persona layer defining agent identity and permissions.

Agent Runtime
Task execution using CrewAI.

ARO (Audit Record Object)
Evidence generator producing append-only audit records.

Output:

`evidence/*.json`
