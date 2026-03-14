#!/usr/bin/env python3
"""Regenerate and verify the tracked deterministic demo sample bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from demo.agent import DEFAULT_TASK, REPO_SAMPLE_TIMESTAMP, run_agent


MANIFEST_PATH = ROOT_DIR / "evidence" / "sample-manifest.json"
SAMPLE_FILES = [
    "interaction/intent.json",
    "interaction/action.json",
    "interaction/result.json",
    "evidence/example_audit.json",
    "evidence/result.json",
]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def build_manifest() -> dict[str, object]:
    return {
        "schema": "verifiable-agent-demo-sample-manifest-v1",
        "sample_kind": "repo_tracked_generated_bundle",
        "sample_task": DEFAULT_TASK,
        "sample_timestamp": REPO_SAMPLE_TIMESTAMP,
        "generated_by": "scripts/refresh_demo_samples.py",
        "artifacts": {
            relative_path: {
                "sha256": _sha256(ROOT_DIR / relative_path),
            }
            for relative_path in SAMPLE_FILES
        },
    }


def refresh() -> None:
    run_agent(
        DEFAULT_TASK,
        output_root=".",
        timestamp=REPO_SAMPLE_TIMESTAMP,
    )
    MANIFEST_PATH.write_text(
        json.dumps(build_manifest(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def verify() -> int:
    if not MANIFEST_PATH.exists():
        print(f"missing manifest: {MANIFEST_PATH}")
        return 1

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    expected = manifest.get("artifacts", {})
    if not isinstance(expected, dict):
        print("invalid manifest: artifacts must be an object")
        return 1

    mismatches: list[str] = []
    for relative_path, details in expected.items():
        artifact_path = ROOT_DIR / relative_path
        if not artifact_path.exists():
            mismatches.append(f"missing {relative_path}")
            continue
        actual_hash = _sha256(artifact_path)
        expected_hash = ""
        if isinstance(details, dict):
            expected_hash = str(details.get("sha256", ""))
        if actual_hash != expected_hash:
            mismatches.append(
                f"{relative_path}: expected {expected_hash}, got {actual_hash}"
            )

    if mismatches:
        print("sample verification failed:")
        for item in mismatches:
            print(f"- {item}")
        return 1

    print("sample verification passed")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify the tracked sample bundle against the manifest",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.verify:
        return verify()

    refresh()
    return verify()


if __name__ == "__main__":
    raise SystemExit(main())
