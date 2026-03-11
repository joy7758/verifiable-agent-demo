# Verifiable Agent Execution

Minimal infrastructure for auditable AI agent systems.

This repository demonstrates a governance pipeline for AI agents built on five layers:

Persona -> Interaction -> Governance -> Execution Integrity -> Audit Evidence

Architecture:

POP (Persona Object Protocol)
Portable persona layer defining agent identity and permissions.

AIP (Agent Intent Protocol)
Semantic interaction objects for intent, action, and result exchange.

Governance Check
Policy checkpoint reference before execution.

Execution Runtime
Task execution using deterministic local mock logic or CrewAI.

ARO (Audit Record Object)
Evidence generator producing append-only audit records.

Output:

`interaction/*.json` and `evidence/*.json`
