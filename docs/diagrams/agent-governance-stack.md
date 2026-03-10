# Agent Governance Pipeline

```mermaid
flowchart TD

A[Persona Object<br>POP] --> B[Agent Runtime<br>CrewAI]

B --> C[Execution Trace]

C --> D[Audit Evidence<br>ARO Record]

D --> E[Evidence JSON Output]

style A fill:#e3f2fd
style B fill:#e8f5e9
style C fill:#fff3e0
style D fill:#fce4ec
style E fill:#ede7f6
```

Minimal governance pipeline for AI agents.

Layers:

Identity -> Persona Object (POP)
Execution -> Agent Runtime (CrewAI)
Trace -> Execution trace capture
Audit -> ARO-style evidence record
