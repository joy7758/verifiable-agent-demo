#!/usr/bin/env python3
"""Generate LaTeX table fragments from repository metric summaries."""

from __future__ import annotations

import json
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
LATEX_ROOT = SCRIPT_DIR.parent
REPO_ROOT = LATEX_ROOT.parent.parent
METRICS_DIR = REPO_ROOT / "artifacts" / "metrics"
TABLES_DIR = LATEX_ROOT / "tables"


def load_modes(name: str) -> dict[str, dict]:
    data = json.loads((METRICS_DIR / name).read_text())
    return {entry["mode"]: entry for entry in data["modes"]}


def write(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n")


def format_score(value: float) -> str:
    return f"{value:.2f}" if isinstance(value, float) and value % 1 else f"{value:.1f}"


def main_table() -> str:
    modes = load_modes("comparison-summary.json")
    order = ["baseline", "evidence_chain"]
    labels = {
        "baseline": "Baseline",
        "evidence_chain": "Evidence chain",
    }
    rows = []
    for mode in order:
      entry = modes[mode]
      rows.append(
          "    {label} & {intent}/{total} & {policy}/{total} & {verified}/{total} & {receipt}/{total} & {explicitness} & {replayability} & {tamper} & {audit} & {integration} \\\\".format(
              label=labels[mode],
              intent=entry["intent_captured_true"],
              policy=entry["policy_checked_true"],
              verified=entry["execution_verified_true"],
              receipt=entry["receipt_exported_true"],
              total=entry["total_tasks"],
              explicitness=format_score(entry["average_explicitness"]),
              replayability=format_score(entry["average_replayability"]),
              tamper=format_score(entry["average_tamper_sensitivity"]),
              audit=format_score(entry["average_audit_boundedness"]),
              integration=format_score(entry["average_integration_surface"]),
          )
      )

    return r"""
\begin{table}[t]
\centering
\caption{Trace-oriented baseline versus full evidence chain. Counts report positive bundle-review verdicts across the 16-task suite; scores are average rule-based metrics on a 0--5 scale. The evidence-chain condition includes 11 verified successful executions, 3 policy-blocked reviewable outcomes, and 2 tamper-detected reviewable outcomes.}
\label{tab:main-comparison}
\small
\resizebox{\linewidth}{!}{%
\begin{tabular}{lccccccccc}
\toprule
Mode & Intent & Policy & Exec.\ verified & Receipt & Explicitness & Replayability & Tamper & Audit & Stage exposure \\
\midrule
""" + "\n".join(rows) + r"""
\\
\bottomrule
\end{tabular}%
}
\end{table}
"""


def external_table() -> str:
    modes = load_modes("external-baseline-summary.json")
    order = ["external_baseline", "evidence_chain"]
    labels = {
        "external_baseline": "External baseline",
        "evidence_chain": "Evidence chain",
    }
    rows = []
    for mode in order:
      entry = modes[mode]
      rows.append(
          "    {label} & {intent}/{total} & {policy}/{total} & {verified}/{total} & {receipt}/{total} & {explicitness} & {replayability} & {tamper} & {audit} & {integration} \\\\".format(
              label=labels[mode],
              intent=entry["intent_captured_true"],
              policy=entry["policy_checked_true"],
              verified=entry["execution_verified_true"],
              receipt=entry["receipt_exported_true"],
              total=entry["total_tasks"],
              explicitness=format_score(entry["average_explicitness"]),
              replayability=format_score(entry["average_replayability"]),
              tamper=format_score(entry["average_tamper_sensitivity"]),
              audit=format_score(entry["average_audit_boundedness"]),
              integration=format_score(entry["average_integration_surface"]),
          )
      )

    return r"""
\begin{table}[t]
\centering
\caption{Framework-shaped external baseline versus the full evidence chain. The external baseline preserves a richer default execution surface than the local trace baseline, but does not add explicit evidence-chain semantics.}
\label{tab:external-comparison}
\small
\resizebox{\linewidth}{!}{%
\begin{tabular}{lccccccccc}
\toprule
Mode & Intent & Policy & Exec.\ verified & Receipt & Explicitness & Replayability & Tamper & Audit & Stage exposure \\
\midrule
""" + "\n".join(rows) + r"""
\\
\bottomrule
\end{tabular}%
}
\end{table}
"""


def framework_pair_table() -> str:
    crewai_modes = load_modes("framework-pair-summary.json")
    langchain_modes = load_modes("langchain-pair-summary.json")
    entries = [
        ("CrewAI", "CrewAI baseline", crewai_modes["external_baseline"]),
        ("CrewAI", "CrewAI + evidence chain", crewai_modes["external_evidence_chain"]),
        ("LangChain", "LangChain baseline", langchain_modes["langchain_baseline"]),
        ("LangChain", "LangChain + evidence chain", langchain_modes["langchain_evidence_chain"]),
    ]
    rows = []
    for framework, label, entry in entries:
        rows.append(
            "    {framework} & {label} & {intent}/{total} & {policy}/{total} & {verified}/{total} & {receipt}/{total} & {explicitness} & {replayability} & {tamper} & {audit} & {integration} \\\\".format(
                framework=framework,
                label=label,
                intent=entry["intent_captured_true"],
                policy=entry["policy_checked_true"],
                verified=entry["execution_verified_true"],
                receipt=entry["receipt_exported_true"],
                total=entry["total_tasks"],
                explicitness=format_score(entry["average_explicitness"]),
                replayability=format_score(entry["average_replayability"]),
                tamper=format_score(entry["average_tamper_sensitivity"]),
                audit=format_score(entry["average_audit_boundedness"]),
                integration=format_score(entry["average_integration_surface"]),
            )
        )

    return r"""
\begin{table}[t]
\centering
\caption{Same-framework paired comparisons under the live CrewAI and LangChain paths. In both frameworks the baseline preserves only the default framework-shaped observability surface, while the paired condition wraps that same runtime with the full evidence chain.}
\label{tab:framework-pair-comparison}
\small
\resizebox{\linewidth}{!}{%
\begin{tabular}{llccccccccc}
\toprule
Framework & Mode & Intent & Policy & Exec.\ verified & Receipt & Explicitness & Replayability & Tamper & Audit & Stage exposure \\
\midrule
""" + "\n".join(rows) + r"""
\\
\bottomrule
\end{tabular}%
}
\end{table}
"""


def ablation_table() -> str:
    modes = load_modes("ablation-summary.json")
    order = [
        "baseline",
        "external_baseline",
        "no_intent",
        "no_governance",
        "no_integrity",
        "no_receipt",
        "evidence_chain",
    ]
    labels = {
        "baseline": "Baseline",
        "external_baseline": "External baseline",
        "no_intent": "No intent",
        "no_governance": "No governance",
        "no_integrity": "No integrity",
        "no_receipt": "No receipt",
        "evidence_chain": "Evidence chain",
    }
    rows = []
    for mode in order:
      entry = modes[mode]
      rows.append(
          "    {label} & {explicitness} & {replayability} & {tamper} & {audit} & {integration} & {intent}/{total} & {policy}/{total} & {verified}/{total} & {receipt}/{total} \\\\".format(
              label=labels[mode],
              explicitness=format_score(entry["average_explicitness"]),
              replayability=format_score(entry["average_replayability"]),
              tamper=format_score(entry["average_tamper_sensitivity"]),
              audit=format_score(entry["average_audit_boundedness"]),
              integration=format_score(entry["average_integration_surface"]),
              intent=entry["intent_captured_true"],
              policy=entry["policy_checked_true"],
              verified=entry["execution_verified_true"],
              receipt=entry["receipt_exported_true"],
              total=entry["total_tasks"],
          )
      )

    return r"""
\begin{table}[t]
\centering
\caption{Seven-mode comparison across the baseline, external baseline, four ablations, and the full evidence chain. Scores are average 0--5 values; counts report positive review verdicts across 16 tasks.}
\label{tab:ablation-comparison}
\small
\resizebox{\linewidth}{!}{%
\begin{tabular}{lccccccccc}
\toprule
Mode & Explicitness & Replayability & Tamper & Audit & Stage exposure & Intent & Policy & Exec.\ verified & Receipt \\
\midrule
""" + "\n".join(rows) + r"""
\\
\bottomrule
\end{tabular}%
}
\end{table}
"""


def falsification_table() -> str:
    data = json.loads((METRICS_DIR / "falsification-summary.json").read_text())
    order = [
        "missing_intent",
        "missing_policy",
        "forged_receipt",
        "payload_tamper",
        "false_tamper_claim",
        "cross_run_replay_mismatch",
        "cross_bundle_receipt_swap",
        "policy_bypass_claim",
    ]
    labels = {
        "missing_intent": "Missing intent",
        "missing_policy": "Missing policy",
        "forged_receipt": "Forged receipt",
        "payload_tamper": "Payload tamper",
        "false_tamper_claim": "False tamper claim",
        "cross_run_replay_mismatch": "Cross-run replay mismatch",
        "cross_bundle_receipt_swap": "Cross-bundle receipt swap",
        "policy_bypass_claim": "Policy bypass claim",
    }
    source_labels = {
        "pass": "Pass",
        "policy_blocked": "Policy-blocked",
    }
    targets = {
        "missing_intent": "Intent",
        "missing_policy": "Policy",
        "forged_receipt": "Receipt",
        "payload_tamper": "Execution + receipt",
        "false_tamper_claim": "Tamper claim",
        "cross_run_replay_mismatch": "Replay chain",
        "cross_bundle_receipt_swap": "Receipt binding",
        "policy_bypass_claim": "Policy/result coherence",
    }
    by_name = {entry["scenario"]: entry for entry in data["scenarios"]}
    rows = []
    for scenario in order:
        entry = by_name[scenario]
        rows.append(
            "    {label} & {source} & {target} & {detected}/{total} & {intent}/{total} & {policy}/{total} & {verified}/{total} & {receipt}/{total} \\\\".format(
                label=labels[scenario],
                source=source_labels.get(entry["source_status"], entry["source_status"].replace("_", "-")),
                target=targets[scenario],
                detected=entry["detected_bundles"],
                total=entry["total_bundles"],
                intent=entry["intent_captured_true"],
                policy=entry["policy_checked_true"],
                verified=entry["execution_verified_true"],
                receipt=entry["receipt_exported_true"],
            )
        )

    return r"""
\begin{table}[t]
\centering
\caption{Negative-control bundle checks derived from review-passing and policy-blocked evidence-chain runs. Each scenario is re-reviewed with the same independent bundle contract used in the main study.}
\label{tab:falsification-summary}
\small
\resizebox{\linewidth}{!}{%
\begin{tabular}{llcccccc}
\toprule
Scenario & Source & Targeted failure & Detected & Intent & Policy & Exec.\ verified & Receipt \\
\midrule
""" + "\n".join(rows) + r"""
\\
\bottomrule
\end{tabular}%
}
\end{table}
"""


def main() -> None:
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    write(TABLES_DIR / "main_comparison.tex", main_table())
    write(TABLES_DIR / "external_comparison.tex", external_table())
    write(TABLES_DIR / "framework_pair_comparison.tex", framework_pair_table())
    write(TABLES_DIR / "ablation_summary.tex", ablation_table())
    write(TABLES_DIR / "falsification_summary.tex", falsification_table())


if __name__ == "__main__":
    main()
