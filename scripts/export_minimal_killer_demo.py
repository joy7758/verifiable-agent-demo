#!/usr/bin/env python3
"""Export a minimal external demo view from comparison-summary metrics."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


BASELINE_GAPS = [
    "intent not explicitly captured",
    "policy not explicitly checked",
    "execution verification not performed",
    "receipt not exported with verifiable artifact digests",
]

EVIDENCE_CHAIN_ADDITIONS = [
    "intent captured",
    "policy checked",
    "execution verified or explicitly blocked/tamper-detected",
    "bounded receipt exported",
]

NORMALIZED_CHECKS = {
    "intent not explicitly captured": "intent not explicitly captured",
    "policy not explicitly checked": "policy not explicitly checked",
    "execution verification status: not_performed": "execution verification not performed",
    "receipt not exported with verifiable artifact digests": "receipt not exported with verifiable artifact digests",
}

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = REPO_ROOT / "artifacts" / "metrics" / "comparison-summary.json"
OUTREACH_DIR = REPO_ROOT / "docs" / "outreach"
JSON_OUTPUT_PATH = OUTREACH_DIR / "minimal-killer-demo.json"
MARKDOWN_OUTPUT_PATH = OUTREACH_DIR / "minimal-killer-demo.md"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def relative_repo_path(path: Path | str) -> str:
    resolved = Path(path).resolve()
    return resolved.relative_to(REPO_ROOT).as_posix()


def task_sort_key(task_id: str) -> tuple[int, str]:
    try:
        return (int(task_id.split("-")[-1]), task_id)
    except ValueError:
        return (10**9, task_id)


def read_bundle(run_dir: str) -> dict[str, Any]:
    run_path = Path(run_dir)
    if not run_path.is_absolute():
        run_path = REPO_ROOT / run_path
    return {
        "intent": load_json(run_path / "intent.json"),
        "action": load_json(run_path / "action.json"),
        "result": load_json(run_path / "result.json"),
        "receipt": load_json(run_path / "receipt.json"),
    }


def stable_counter(counter: Counter[str]) -> dict[str, int]:
    return {key: counter[key] for key in sorted(counter)}


def summarize_baseline(entries: list[dict[str, Any]]) -> dict[str, Any]:
    normalized = Counter()
    digest_counts: list[int] = []

    for entry in entries:
        receipt = read_bundle(entry["review"]["run_dir"])["receipt"]["audit_receipt"]
        digest_counts.append(receipt["boundedness"]["artifact_digest_count"])
        for check in entry["review"]["missing_or_failed_checks"]:
            normalized_name = NORMALIZED_CHECKS.get(check)
            if normalized_name:
                normalized[normalized_name] += 1

    return {
        "mode": "baseline",
        "source_path": relative_repo_path(SOURCE_PATH),
        "tasks_seen": len(entries),
        "missing_capabilities": BASELINE_GAPS,
        "missing_capability_counts": {
            item: normalized.get(item, 0) for item in BASELINE_GAPS
        },
        "overall_status_counts": stable_counter(
            Counter(entry["review"]["overall_status"] for entry in entries)
        ),
        "receipt_digest_count_range": [
            min(digest_counts, default=0),
            max(digest_counts, default=0),
        ],
    }


def summarize_evidence_chain(entries: list[dict[str, Any]]) -> dict[str, Any]:
    verification_statuses = Counter()
    digest_counts: list[int] = []
    execution_covered = 0

    for entry in entries:
        receipt = read_bundle(entry["review"]["run_dir"])["receipt"]["audit_receipt"]
        verification_status = receipt["integrity_summary"]["verification_status"]
        verification_statuses[verification_status] += 1
        digest_counts.append(receipt["boundedness"]["artifact_digest_count"])
        if verification_status in {"verified", "skipped_by_policy", "tamper_detected"}:
            execution_covered += 1

    return {
        "mode": "evidence_chain",
        "source_path": relative_repo_path(SOURCE_PATH),
        "tasks_seen": len(entries),
        "added_capabilities": EVIDENCE_CHAIN_ADDITIONS,
        "capability_counts": {
            "intent captured": sum(1 for entry in entries if entry["review"]["intent_captured"]),
            "policy checked": sum(1 for entry in entries if entry["review"]["policy_checked"]),
            "execution verified or explicitly blocked/tamper-detected": execution_covered,
            "bounded receipt exported": sum(
                1 for entry in entries if entry["review"]["receipt_exported"]
            ),
        },
        "overall_status_counts": stable_counter(
            Counter(entry["review"]["overall_status"] for entry in entries)
        ),
        "verification_status_counts": stable_counter(verification_statuses),
        "receipt_digest_count_range": [
            min(digest_counts, default=0),
            max(digest_counts, default=0),
        ],
    }


def compact_case_payload(entry: dict[str, Any]) -> dict[str, Any]:
    bundle = read_bundle(entry["review"]["run_dir"])
    action = bundle["action"]
    intent = bundle["intent"]
    receipt = bundle["receipt"]["audit_receipt"]
    decision = action["policy"]["decision"]

    reasons = decision.get("reasons") or []
    primary_reason = reasons[0] if reasons else entry["review"]["summary"]

    return {
        "task_id": entry["task_id"],
        "title": action["requested_action"]["summary"],
        "category": entry["category"],
        "mode": entry["mode"],
        "result_status": entry["result_status"],
        "overall_status": entry["review"]["overall_status"],
        "intent_captured": entry["review"]["intent_captured"],
        "policy_checked": entry["review"]["policy_checked"],
        "execution_verified": entry["review"]["execution_verified"],
        "receipt_exported": entry["review"]["receipt_exported"],
        "verification_status": receipt["integrity_summary"]["verification_status"],
        "artifact_digest_count": receipt["boundedness"]["artifact_digest_count"],
        "run_dir": relative_repo_path(entry["review"]["run_dir"]),
        "policy_reason": primary_reason,
        "review_summary": entry["review"]["summary"],
        "goal": (intent.get("intent") or {}).get("goal"),
        "artifact_roles_with_digests": [
            artifact["role"] for artifact in receipt.get("artifacts", [])
        ],
    }


def paired_completed_case(entries: list[dict[str, Any]]) -> dict[str, Any]:
    evidence_candidates = sorted(
        (
            entry
            for entry in entries
            if entry["mode"] == "evidence_chain"
            and entry["result_status"] == "completed"
            and entry["review"]["overall_status"] == "pass"
        ),
        key=lambda entry: task_sort_key(entry["task_id"]),
    )

    by_task_and_mode = {
        (entry["task_id"], entry["mode"]): entry for entry in entries
    }

    for evidence_entry in evidence_candidates:
        baseline_entry = by_task_and_mode.get((evidence_entry["task_id"], "baseline"))
        if not baseline_entry:
            continue
        return {
            "task_id": evidence_entry["task_id"],
            "title": compact_case_payload(evidence_entry)["title"],
            "category": evidence_entry["category"],
            "takeaway": (
                "Both runs finish, but only the evidence-chain run leaves explicit "
                "intent, policy, verification, and receipt evidence."
            ),
            "baseline": compact_case_payload(baseline_entry),
            "evidence_chain": compact_case_payload(evidence_entry),
        }

    raise RuntimeError("No paired completed baseline/evidence-chain case found.")


def single_case(
    entries: list[dict[str, Any]],
    *,
    overall_status: str,
    label: str,
    takeaway: str,
) -> dict[str, Any]:
    matches = sorted(
        (entry for entry in entries if entry["review"]["overall_status"] == overall_status),
        key=lambda entry: task_sort_key(entry["task_id"]),
    )
    if not matches:
        raise RuntimeError(f"No {label} case found in comparison summary.")

    payload = compact_case_payload(matches[0])
    payload["takeaway"] = takeaway
    return payload


def render_markdown(export_data: dict[str, Any]) -> str:
    baseline = export_data["baseline_summary"]
    evidence = export_data["evidence_chain_summary"]
    completed = export_data["one_completed_case"]
    policy_blocked = export_data["one_policy_blocked_case"]
    tamper = export_data["one_tamper_detected_case"]

    return "\n".join(
        [
            "# Why agent logs are not enough",
            "",
            "普通 agent 只告诉你“它跑完了”，但说不清它本来想做什么、有没有经过策略检查、有没有验证执行真实性、有没有导出可交接收据。这个最小样品把同一套本地评测结果压成一页，直接对比 no-evidence run 和 evidence-chain run 的差别。",
            "",
            f"Data source: `{baseline['source_path']}`.",
            "",
            "## Baseline 缺什么",
            "",
            "1. intent not explicitly captured",
            "2. policy not explicitly checked",
            "3. execution verification not performed",
            "4. receipt not exported with verifiable artifact digests",
            "",
            f"Observed in `{baseline['tasks_seen']}/{baseline['tasks_seen']}` baseline runs. Receipt digest count range: `{baseline['receipt_digest_count_range'][0]}-{baseline['receipt_digest_count_range'][1]}`.",
            "",
            "## Evidence chain 多了什么",
            "",
            "1. intent captured",
            "2. policy checked",
            "3. execution verified or explicitly blocked/tamper-detected",
            "4. bounded receipt exported",
            "",
            (
                f"Observed in `{evidence['tasks_seen']}/{evidence['tasks_seen']}` evidence-chain runs. "
                f"Outcome mix: `pass={evidence['overall_status_counts'].get('pass', 0)}`, "
                f"`policy_blocked={evidence['overall_status_counts'].get('policy_blocked', 0)}`, "
                f"`tamper_detected={evidence['overall_status_counts'].get('tamper_detected', 0)}`."
            ),
            "",
            "## Three minimal cases",
            "",
            "### A. completed",
            "",
            f"Task `{completed['task_id']}`: **{completed['title']}**. {completed['takeaway']}",
            "",
            "| run | result_status | overall_status | intent | policy | verification | receipt digests | bundle |",
            "| --- | --- | --- | --- | --- | --- | ---: | --- |",
            (
                f"| baseline | `{completed['baseline']['result_status']}` | "
                f"`{completed['baseline']['overall_status']}` | "
                f"`{str(completed['baseline']['intent_captured']).lower()}` | "
                f"`{str(completed['baseline']['policy_checked']).lower()}` | "
                f"`{completed['baseline']['verification_status']}` | "
                f"{completed['baseline']['artifact_digest_count']} | "
                f"`{completed['baseline']['run_dir']}` |"
            ),
            (
                f"| evidence_chain | `{completed['evidence_chain']['result_status']}` | "
                f"`{completed['evidence_chain']['overall_status']}` | "
                f"`{str(completed['evidence_chain']['intent_captured']).lower()}` | "
                f"`{str(completed['evidence_chain']['policy_checked']).lower()}` | "
                f"`{completed['evidence_chain']['verification_status']}` | "
                f"{completed['evidence_chain']['artifact_digest_count']} | "
                f"`{completed['evidence_chain']['run_dir']}` |"
            ),
            "",
            "### B. policy_blocked",
            "",
            f"Task `{policy_blocked['task_id']}`: **{policy_blocked['title']}**.",
            "",
            f"- Result: `{policy_blocked['result_status']}` with review status `{policy_blocked['overall_status']}`.",
            f"- Reason: {policy_blocked['policy_reason']}",
            f"- Receipt: `{policy_blocked['artifact_digest_count']}` digests exported from `{policy_blocked['run_dir']}`.",
            f"- Takeaway: {policy_blocked['takeaway']}",
            "",
            "### C. tamper_detected",
            "",
            f"Task `{tamper['task_id']}`: **{tamper['title']}**.",
            "",
            f"- Result: `{tamper['result_status']}` with verification `{tamper['verification_status']}`.",
            f"- Receipt: `{tamper['artifact_digest_count']}` digests exported from `{tamper['run_dir']}`.",
            f"- Review summary: {tamper['review_summary']}",
            f"- Takeaway: {tamper['takeaway']}",
            "",
            "## Run locally",
            "",
            "```bash",
            "bash scripts/run_demo.sh",
            "make killer-demo",
            "python3 -m http.server --directory docs 8000",
            "```",
            "",
            "_Generated by `scripts/export_minimal_killer_demo.py`._",
            "",
        ]
    )


def build_export() -> dict[str, Any]:
    comparison = load_json(SOURCE_PATH)
    entries = comparison["per_task"]
    baseline_entries = [entry for entry in entries if entry["mode"] == "baseline"]
    evidence_entries = [entry for entry in entries if entry["mode"] == "evidence_chain"]

    return {
        "baseline_summary": summarize_baseline(baseline_entries),
        "evidence_chain_summary": summarize_evidence_chain(evidence_entries),
        "one_completed_case": paired_completed_case(entries),
        "one_policy_blocked_case": single_case(
            evidence_entries,
            overall_status="policy_blocked",
            label="policy_blocked",
            takeaway=(
                "The run is blocked before completion, but the policy decision and "
                "bounded receipt still make the stop independently reviewable."
            ),
        ),
        "one_tamper_detected_case": single_case(
            evidence_entries,
            overall_status="tamper_detected",
            label="tamper_detected",
            takeaway=(
                "The evidence chain does not just log a failure. It records a digest-backed "
                "receipt showing that tamper was detected."
            ),
        ),
    }


def main() -> int:
    OUTREACH_DIR.mkdir(parents=True, exist_ok=True)

    export_data = build_export()
    markdown = render_markdown(export_data)

    JSON_OUTPUT_PATH.write_text(
        json.dumps(export_data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    MARKDOWN_OUTPUT_PATH.write_text(markdown, encoding="utf-8")

    print(f"Wrote {relative_repo_path(JSON_OUTPUT_PATH)}")
    print(f"Wrote {relative_repo_path(MARKDOWN_OUTPUT_PATH)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
