"""Mode profiles for the paper evaluation harness."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModeProfile:
    name: str
    label: str
    trace_style: str
    framework_label: str
    intent_captured: bool
    policy_checked: bool
    policy_enforced: bool
    policy_visible: bool
    integrity_checked: bool
    receipt_exported: bool
    carries_raw_task_snapshot: bool
    notes: tuple[str, ...]


MODE_PROFILES: dict[str, ModeProfile] = {
    "baseline": ModeProfile(
        name="baseline",
        label="Local trace-only baseline",
        trace_style="trace_only",
        framework_label="paper-local-baseline",
        intent_captured=False,
        policy_checked=False,
        policy_enforced=False,
        policy_visible=True,
        integrity_checked=False,
        receipt_exported=False,
        carries_raw_task_snapshot=False,
        notes=("Trace-only local control path without persisted intent, governance, integrity, or receipt.",),
    ),
    "external_baseline": ModeProfile(
        name="external_baseline",
        label="CrewAI-like native logging baseline",
        trace_style="crewai_native_log",
        framework_label="crewai-like-native-surface",
        intent_captured=False,
        policy_checked=False,
        policy_enforced=False,
        policy_visible=False,
        integrity_checked=False,
        receipt_exported=False,
        carries_raw_task_snapshot=True,
        notes=(
            "Thin deterministic adapter that preserves a CrewAI-like task/agent/logging evidence shape.",
            "This is not a deep live CrewAI integration; it is a local compatibility shim aligned to the existing CrewAI demo.",
        ),
    ),
    "no_intent": ModeProfile(
        name="no_intent",
        label="Ablation without explicit intent",
        trace_style="evidence_chain_no_intent",
        framework_label="paper-local-ablation",
        intent_captured=False,
        policy_checked=True,
        policy_enforced=True,
        policy_visible=True,
        integrity_checked=True,
        receipt_exported=True,
        carries_raw_task_snapshot=False,
        notes=("Ablation mode removes the explicit intent object while preserving other evidence-chain layers.",),
    ),
    "no_governance": ModeProfile(
        name="no_governance",
        label="Ablation without governance",
        trace_style="evidence_chain_no_governance",
        framework_label="paper-local-ablation",
        intent_captured=True,
        policy_checked=False,
        policy_enforced=False,
        policy_visible=False,
        integrity_checked=True,
        receipt_exported=True,
        carries_raw_task_snapshot=False,
        notes=("Ablation mode removes policy persistence and enforcement while leaving other layers in place.",),
    ),
    "no_integrity": ModeProfile(
        name="no_integrity",
        label="Ablation without execution integrity",
        trace_style="evidence_chain_no_integrity",
        framework_label="paper-local-ablation",
        intent_captured=True,
        policy_checked=True,
        policy_enforced=True,
        policy_visible=True,
        integrity_checked=False,
        receipt_exported=True,
        carries_raw_task_snapshot=False,
        notes=("Ablation mode removes digest/checkpoint verification while preserving intent, governance, and receipt.",),
    ),
    "no_receipt": ModeProfile(
        name="no_receipt",
        label="Ablation without audit receipt",
        trace_style="evidence_chain_no_receipt",
        framework_label="paper-local-ablation",
        intent_captured=True,
        policy_checked=True,
        policy_enforced=True,
        policy_visible=True,
        integrity_checked=True,
        receipt_exported=False,
        carries_raw_task_snapshot=False,
        notes=("Ablation mode keeps execution evidence but suppresses the bounded audit receipt export.",),
    ),
    "evidence_chain": ModeProfile(
        name="evidence_chain",
        label="Full evidence chain",
        trace_style="evidence_chain",
        framework_label="paper-local-evidence-chain",
        intent_captured=True,
        policy_checked=True,
        policy_enforced=True,
        policy_visible=True,
        integrity_checked=True,
        receipt_exported=True,
        carries_raw_task_snapshot=False,
        notes=("Full intent, governance, integrity, and receipt chain.",),
    ),
}

DEFAULT_COMPARISON_MODES = ["baseline", "evidence_chain"]
EXTERNAL_COMPARISON_MODES = ["external_baseline", "evidence_chain"]
TOP_JOURNAL_MODES = [
    "baseline",
    "external_baseline",
    "no_intent",
    "no_governance",
    "no_integrity",
    "no_receipt",
    "evidence_chain",
]


def get_mode_profile(mode: str) -> ModeProfile:
    try:
        return MODE_PROFILES[mode]
    except KeyError as exc:  # pragma: no cover - defensive
        raise ValueError(f"unsupported mode: {mode}") from exc


def list_modes() -> list[str]:
    return list(MODE_PROFILES)
