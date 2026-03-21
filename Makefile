PYTHON ?= python3

.PHONY: killer-demo eval-baseline eval-evidence eval-external-baseline eval-framework-pair eval-langchain-pair eval-ablation falsification-checks review-sample compare human-review-kit paper-eval top-journal-pack

killer-demo:
	$(PYTHON) scripts/export_minimal_killer_demo.py

eval-baseline:
	$(PYTHON) scripts/run_paper_eval.py --mode baseline

eval-evidence:
	$(PYTHON) scripts/run_paper_eval.py --mode evidence_chain

eval-external-baseline: eval-evidence
	$(PYTHON) scripts/run_paper_eval.py --mode external_baseline
	$(PYTHON) scripts/compare_runs.py --modes external_baseline evidence_chain --output-stem external-baseline-summary --title "External Baseline vs Evidence Chain" --description "Generated from actual artifacts comparing a minimal live CrewAI baseline against the full evidence chain." --doc-reference docs/paper_support/external-baseline.md

eval-framework-pair:
	$(PYTHON) scripts/run_paper_eval.py --mode external_baseline
	$(PYTHON) scripts/run_paper_eval.py --mode external_evidence_chain
	$(PYTHON) scripts/compare_runs.py --modes external_baseline external_evidence_chain --output-stem framework-pair-summary --title "Same-Framework Comparison" --description "Generated from actual artifacts comparing a minimal live CrewAI baseline with the same live CrewAI path wrapped by the full evidence chain." --doc-reference docs/paper_support/same-framework-comparison.md

eval-langchain-pair:
	$(PYTHON) scripts/run_paper_eval.py --mode langchain_baseline
	$(PYTHON) scripts/run_paper_eval.py --mode langchain_evidence_chain
	$(PYTHON) scripts/compare_runs.py --modes langchain_baseline langchain_evidence_chain --output-stem langchain-pair-summary --title "LangChain Same-Framework Comparison" --description "Generated from actual artifacts comparing a minimal live LangChain baseline with the same live LangChain path wrapped by the full evidence chain." --doc-reference docs/paper_support/langchain-comparison.md

eval-ablation: eval-baseline eval-external-baseline eval-evidence
	$(PYTHON) scripts/run_paper_eval.py --mode no_intent
	$(PYTHON) scripts/run_paper_eval.py --mode no_governance
	$(PYTHON) scripts/run_paper_eval.py --mode no_integrity
	$(PYTHON) scripts/run_paper_eval.py --mode no_receipt
	$(PYTHON) scripts/compare_runs.py --modes baseline external_baseline no_intent no_governance no_integrity no_receipt evidence_chain --output-stem ablation-summary --title "Top-Journal Mode Comparison" --description "Generated from actual artifacts across baseline, external baseline, four ablations, and the full evidence chain." --doc-reference docs/paper_support/ablation-study.md

falsification-checks: eval-evidence
	$(PYTHON) scripts/run_falsification_checks.py

review-sample: eval-baseline eval-evidence
	$(PYTHON) scripts/review_bundle.py --run-dir artifacts/runs/task-001/baseline
	$(PYTHON) scripts/review_bundle.py --run-dir artifacts/runs/task-001/evidence_chain

compare: eval-baseline eval-evidence
	$(PYTHON) scripts/compare_runs.py

human-review-kit: eval-baseline eval-evidence
	$(PYTHON) scripts/generate_human_review_kit.py
	$(PYTHON) scripts/summarize_human_review.py --sheet evaluation/human_review/examples/synthetic_review_sheet.csv --output-prefix artifacts/human_review/synthetic-review-summary

paper-eval: eval-baseline eval-evidence review-sample compare

top-journal-pack: paper-eval eval-external-baseline eval-framework-pair eval-langchain-pair eval-ablation falsification-checks human-review-kit
