# Agent Governance Pipeline

```mermaid
flowchart TD

A[Persona Object<br>POP] --> B[Intent Object<br>AIP]

B --> C[Governance Check<br>Token Governor Context]

C --> D[Execution Trace]

D --> E[Audit Evidence<br>ARO Record]

E --> F[Evidence JSON Output]

style A fill:#e3f2fd
style B fill:#e8f5e9
style C fill:#fff3e0
style D fill:#fce4ec
style E fill:#ede7f6
style F fill:#f3e5f5
```

Minimal governance pipeline for AI agents.

Layers:

Identity -> Persona Object (POP)
Interaction -> Intent Object (AIP)
Governance -> Pre-execution checkpoint
Execution -> Execution trace capture
Audit -> ARO-style evidence record
