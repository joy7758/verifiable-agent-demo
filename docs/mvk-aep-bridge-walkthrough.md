# MVK -> Agent Evidence Bridge Walkthrough

## What this connects

```text
verifiable-agent-demo = guided walkthrough
fdo-kernel-mvk = execution integrity proof
agent-evidence = evidence packaging and reviewer handoff
```

This repository stays focused on the shortest guided demo path. It does not
vendor or import the execution-integrity kernel or the evidence packaging
toolkit.

## Handoff path

```text
MVK execution
-> audit_bundle.json
-> AEP-compatible bundle
-> offline verification
-> signed export / review pack workflows
```

## Run with sibling repositories

```bash
git clone https://github.com/joy7758/fdo-kernel-mvk ../fdo-kernel-mvk
git clone https://github.com/joy7758/agent-evidence ../agent-evidence

make mvk-aep-bridge-dry-run
make mvk-aep-bridge-demo
```

`make mvk-aep-bridge-demo` defaults to `../fdo-kernel-mvk`. Override it with
`MVK_REPO=/path/to/fdo-kernel-mvk` when the checkout is elsewhere.

## Manual path

```bash
cd ../fdo-kernel-mvk
make demo
make verify-demo
make export-aep
make verify-aep

agent-evidence verify-bundle --bundle-dir mvk-aep-bundle
```

## Expected outputs

- `../fdo-kernel-mvk/audit_bundle.json`
- `../fdo-kernel-mvk/mvk-aep-bundle/manifest.json`
- `../fdo-kernel-mvk/mvk-aep-bundle/records.jsonl`
- `../fdo-kernel-mvk/mvk-aep-bundle/mvk-aep-receipt.json`

## Boundary and non-claims

- The MVK bridge bundle is local and unsigned.
- Signed export, signature verification, and Review Pack remain in
  `agent-evidence`.
- This is not legal non-repudiation.
- This is not compliance certification.
- This is not official FDO standard adoption.
