# Verifiable Agent Architecture

This demo shows a minimal governance pipeline for AI agents.

Architecture:

Persona (POP)
-> Agent Runtime
-> Execution Trace
-> Audit Evidence (ARO)

Components:

POP
Portable persona layer for agent identity.

Agent Runtime
Task execution using CrewAI.

ARO
Audit evidence generator producing verifiable records.

Token Governor (optional)
Cost and resource governance layer.

Output:

`evidence/*.json`
