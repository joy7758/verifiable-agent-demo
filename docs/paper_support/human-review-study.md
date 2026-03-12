# Human Review Study

The repository includes a lightweight local blinded review kit under `evaluation/human_review/`.

Reviewer-facing contents:

- `reviewer/instructions.md`
- `reviewer/blinded-bundle-manifest.csv`
- `reviewer/review-sheet-template.csv`
- `blinded_bundles/bundle-XXX/`

Admin-only contents:

- `admin/answer-key.json`
- `admin/bundle-manifest.csv`

Required review fields:

- `reviewer_id`
- `bundle_id`
- `condition_hidden`
- `answer_1`
- `answer_2`
- `answer_3`
- `answer_4`
- `confidence`
- `time_spent_seconds`
- `uncertainty_notes`

Question mapping:

- `answer_1`: was intent captured?
- `answer_2`: was policy checked?
- `answer_3`: was execution verified?
- `answer_4`: was receipt exported?

Summarization:

- `scripts/summarize_human_review.py` reads completed review sheets plus the hidden answer key.
- It emits Markdown, CSV, and JSON summaries with per-condition accuracy, mean confidence, mean review time, and error counts.
- The repository includes a clearly labeled synthetic example sheet for smoke testing only.

Run command:

```bash
make human-review-kit
```

Synthetic example output:

- `artifacts/human_review/synthetic-review-summary.md`
- `artifacts/human_review/synthetic-review-summary.csv`
- `artifacts/human_review/synthetic-review-summary.json`
