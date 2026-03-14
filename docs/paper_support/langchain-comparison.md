# LangChain Same-Framework Comparison

This workflow compares two conditions built on the same live LangChain LCEL runtime path:

- `langchain_baseline`: minimal live LangChain execution with default observability-like callback export only
- `langchain_evidence_chain`: the same live LangChain execution path wrapped by explicit intent capture, governance persistence, integrity validation, and bounded receipt export

Why this comparison exists:

- It provides a second framework-level paired comparison beyond CrewAI.
- It isolates the effect of the evidence layer while keeping the LangChain runtime fixed.
- It reduces the risk that the paper's external comparison depends on a single framework ecosystem.

Run it with:

```bash
make eval-langchain-pair
```

Generated outputs:

- `docs/paper_support/langchain-pair-summary.md`
- `docs/paper_support/langchain-pair-summary.csv`
- `artifacts/metrics/langchain-pair-summary.json`

Implementation notes:

- The live path uses a minimal LCEL pipeline: `ChatPromptTemplate | SimpleChatModel | StrOutputParser`.
- The chat model is deterministic and local; it does not call an external API.
- The baseline persists callback-shaped framework events but does not claim explicit intent, governance, integrity, or bounded receipt support.
- The wrapped condition exports the same live LangChain execution path through the full evidence-preserving contract.

Environment note:

- Create the local framework environment first with `bash scripts/setup_framework_venv.sh`.
- This mode requires `langchain` in the repository `.venv/`. The checked-in artifacts were generated with `langchain 1.2.12` in the same local environment that carries `crewai 1.10.1` for the CrewAI pair.

Limits:

- This is a minimal live integration rather than a production LangChain deployment.
- The comparison remains evidence-shape oriented rather than semantic-quality oriented.
