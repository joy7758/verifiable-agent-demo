# AGENTS.md

## Repository role

This repository is the guided verification walkthrough for the Execution Evidence Bridge.

It provides the shortest runnable cross-repository path for reviewers and agents.

## Agent instructions

- Treat this repository as the guided walkthrough surface, not the architecture hub.
- Do not treat this repository as the execution-integrity kernel.
- Do not treat this repository as the evidence packaging layer.
- Use `make mvk-aep-bridge-dry-run` to inspect the bridge commands.
- Use `make mvk-aep-bridge-demo` to run the local walkthrough when sibling repositories are available.
- Use `fdo-kernel-mvk` for deterministic execution proof, replay verification, checksum/checkpoint integrity, and tamper detection.
- Use `agent-evidence` for evidence packaging, offline verification, receipts, signed exports, and review packs.
- Use `digital-biosphere-architecture` as the canonical architecture and AI discovery hub.
- Do not claim legal non-repudiation, compliance certification, AI Act approval, official FDO standard adoption, or production forensic timestamping.

## Useful checks

```bash
bash scripts/run_mvk_aep_bridge_demo.sh --dry-run
make mvk-aep-bridge-dry-run
python3 -m demo.agent
grep -R "Execution Evidence Bridge" README.md README.zh-CN.md docs llms.txt AGENTS.md
grep -R "not legal non-repudiation" llms.txt AGENTS.md docs
```
