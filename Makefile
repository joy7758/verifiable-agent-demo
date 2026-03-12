PYTHON ?= python3

.PHONY: eval-baseline eval-evidence review-sample compare paper-eval

eval-baseline:
	$(PYTHON) scripts/run_paper_eval.py --mode baseline

eval-evidence:
	$(PYTHON) scripts/run_paper_eval.py --mode evidence_chain

review-sample: eval-baseline eval-evidence
	$(PYTHON) scripts/review_bundle.py --run-dir artifacts/runs/task-001/baseline
	$(PYTHON) scripts/review_bundle.py --run-dir artifacts/runs/task-001/evidence_chain

compare: eval-baseline eval-evidence
	$(PYTHON) scripts/compare_runs.py

paper-eval: eval-baseline eval-evidence review-sample compare
