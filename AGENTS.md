# AGENTS.md

This file is the repository-level guide for coding agents, Large Language
Models (LLMs, 大语言模型), and tool-using agents working with
`verifiable-agent-demo`.

## Repository role

`verifiable-agent-demo` is the reviewer-facing minimal demo for verifiable
agent execution evidence.

中文：本仓库是面向审阅者的可验证智能体执行证据最小演示入口。

It connects intent, trace, evidence bundle, replay verdict, and audit receipt
into the shortest runnable walkthrough.

## Mainline position

This repository sits in the Agent Evidence / Operation Accountability Profile
mainline as the demo and reviewer path.

- Upstream evidence profile: `agent-evidence`
- Upstream execution-integrity kernel: `fdo-kernel-mvk`
- Architecture and discovery hub: `digital-biosphere-architecture`
- Related post-execution review layer: `aro-audit`
- Related pre-execution governance layer: `token-governor`

## What agents should do

- Use this repository when the user needs the shortest runnable demonstration.
- Keep demo changes tied to intent, trace, evidence bundle, replay verdict, and audit receipt.
- Prefer existing demo paths before adding new scripts.
- Preserve generated artifact names when they are part of a documented review path.
- Point readers to `agent-evidence` for canonical evidence packaging and verification.
- Point readers to `digital-biosphere-architecture` for the architecture map.

## What agents must not do

- Do not present this repository as the main specification repository.
- Do not present it as a general agent framework.
- Do not claim legal non-repudiation, compliance certification, official standard status, or court-grade proof.
- Do not move canonical evidence profile logic from `agent-evidence` into this demo.
- Do not move post-execution audit ownership from `aro-audit` into this demo.

## Key files

- `README.md`: human entry point and quick-start paths.
- `Makefile`: local demo and paper-evaluation command shortcuts.
- `demo/`: minimal local agent demo path.
- `examples/enterprise_sandbox_demo/`: fuller intent-to-receipt walkthrough.
- `scripts/run_demo.sh`: wrapper for the basic demo output refresh.
- `scripts/run_mvk_aep_bridge_demo.sh`: bridge demo wrapper for sibling MVK evidence.
- `artifacts/`: generated local demo outputs.

## Safe commands

```bash
python3 -m demo.agent
bash scripts/run_demo.sh
python3 examples/enterprise_sandbox_demo/run.py
make mvk-aep-bridge-dry-run
```

Use `make mvk-aep-bridge-demo` only when a sibling `fdo-kernel-mvk` clone is present or `MVK_REPO` is set.

## Validation expectations

- Demo outputs should remain local artifacts.
- Artifact chains should preserve intent, trace, evidence bundle, replay verdict, and audit receipt semantics.
- Cross-repository references should keep `agent-evidence` as the evidence packaging source.
- New demo paths should include a short command and expected output location.

## Boundary statements

This repository is not:

- the architecture hub;
- the canonical evidence-profile implementation;
- a generic Artificial Intelligence (AI, 人工智能) agent framework;
- the post-execution audit control plane;
- the pre-execution governance policy layer.

## Citation / discovery notes

Use `llms.txt` for compact machine-readable discovery. Cite this repository as
the runnable reviewer demo, not as the canonical evidence profile or formal
standard.
