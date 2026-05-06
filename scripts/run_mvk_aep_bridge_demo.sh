#!/usr/bin/env bash
set -euo pipefail

MVK_REPO="${MVK_REPO:-../fdo-kernel-mvk}"
AGENT_EVIDENCE_CLI="${AGENT_EVIDENCE_CLI:-agent-evidence}"
MVK_AEP_BUNDLE_DIR="${MVK_AEP_BUNDLE_DIR:-$MVK_REPO/mvk-aep-bundle}"

usage() {
  cat <<'USAGE'
Usage: scripts/run_mvk_aep_bridge_demo.sh [--dry-run]

Environment overrides:
  MVK_REPO=/path/to/fdo-kernel-mvk
  AGENT_EVIDENCE_CLI=agent-evidence
  MVK_AEP_BUNDLE_DIR=/path/to/mvk-aep-bundle
USAGE
}

print_plan() {
  cat <<PLAN
Would run:
  make -C "$MVK_REPO" demo
  make -C "$MVK_REPO" verify-demo
  make -C "$MVK_REPO" export-aep
  make -C "$MVK_REPO" verify-aep
  $AGENT_EVIDENCE_CLI verify-bundle --bundle-dir "$MVK_AEP_BUNDLE_DIR"
PLAN
}

dry_run=false

while (($#)); do
  case "$1" in
    --dry-run)
      dry_run=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$dry_run" == true ]]; then
  print_plan
  exit 0
fi

if [[ ! -d "$MVK_REPO" ]]; then
  echo "MVK repository not found: $MVK_REPO" >&2
  echo "Set MVK_REPO=/path/to/fdo-kernel-mvk or clone it as a sibling repository." >&2
  exit 1
fi

make -C "$MVK_REPO" demo
make -C "$MVK_REPO" verify-demo
make -C "$MVK_REPO" export-aep
make -C "$MVK_REPO" verify-aep

if command -v "$AGENT_EVIDENCE_CLI" >/dev/null 2>&1; then
  "$AGENT_EVIDENCE_CLI" verify-bundle --bundle-dir "$MVK_AEP_BUNDLE_DIR"
else
  cat <<NOTE
NOTE: MVK-side export and verification passed.
NOTE: agent-evidence CLI was not found as "$AGENT_EVIDENCE_CLI".
NOTE: Install agent-evidence and run:
  $AGENT_EVIDENCE_CLI verify-bundle --bundle-dir "$MVK_AEP_BUNDLE_DIR"
NOTE
fi

cat <<SUMMARY
MVK AEP bridge demo complete.
  audit bundle:  $MVK_REPO/audit_bundle.json
  AEP manifest:  $MVK_AEP_BUNDLE_DIR/manifest.json
  records.jsonl:  $MVK_AEP_BUNDLE_DIR/records.jsonl
  receipt:       $MVK_AEP_BUNDLE_DIR/mvk-aep-receipt.json
SUMMARY
