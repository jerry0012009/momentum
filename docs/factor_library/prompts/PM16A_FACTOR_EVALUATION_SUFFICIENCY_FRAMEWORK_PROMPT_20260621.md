# PM-16A Prompt — Factor Evaluation Sufficiency Framework and Roadmap

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This prompt supersedes the earlier PM-16 evidence-warning idea. Do **not** simply add flags for every metric contradiction. The user's real goal is broader:

> The factor library should compute factors reliably, display enough evidence to evaluate factor quality, remain readable, and be extensible when new factors are added.

PM-15 upgraded the existing factor evaluation page. Before adding more warnings or pages, PM-16A should define and audit the evidence framework required to judge factor quality.

## 0. PM objective

Create a factor evaluation sufficiency framework that answers:

1. What evidence is required to judge a factor?
2. Which evidence is already available in the current repository?
3. Which evidence is displayed on the current factor evaluation page?
4. Which evidence is missing or insufficient?
5. What should the next engineering tasks be, in the correct order?

This task is primarily an audit/spec/governance task. It should not add factors, change formulas, or create new pages.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify `scripts/factor_formula_registry.py`.

Do **not** modify `scripts/factor_ops.py`.

Do **not** modify signal panel construction.

Do **not** rebuild signal panel.

Do **not** create a new public page.

Do **not** make production/live/tradeability/alpha claims.

Do **not** turn every RankIC/Sharpe mismatch into a simplistic warning. Metric disagreement should be interpreted within an evidence framework, not mechanically flagged.

## 2. Repository structure to inspect

Read the current entry/governance docs:

```text
docs/factor_library/START_HERE.md
docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md
docs/factor_library/factor_library_manifest.json
```

Read current key scripts:

```text
scripts/factor_formula_registry.py
scripts/factor_specs.py
scripts/factor_ops.py
scripts/build_factor_values.py
scripts/evaluate_factors.py
scripts/build_factor_diagnostics_metrics.py
scripts/build_factor_bilingual_cards.py
scripts/_build_factor_eval_html.py
scripts/run_factor_intake.py
scripts/build_factor_redundancy.py
scripts/build_factor_conclusion_cards.py
scripts/generate_intake_report.py
```

Read current data/evaluation artifacts:

```text
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/
research/factor_runs/crypto_top50_factor_library/factor_metadata/
```

Read current public pages:

```text
reports/site/factor-library/index.html
reports/site/factor-library/actual-script-map.html
reports/site/factor-library/factor-evaluation.html
reports/site/factor-library/signal-evaluation-summary.html
```

## 3. Required output files

Create:

```text
docs/factor_library/audits/pm16a_factor_evaluation_sufficiency_framework.md
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_inventory.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_framework_spec.json
```

Do not modify public pages in this task.

## 4. Evidence framework dimensions

Define a factor evaluation framework with these dimensions at minimum:

### 4.1 Computation integrity

Questions:

- Is the factor registered in `FactorSpec`?
- Are required input columns available?
- Are factor_values computed for all canonical symbols/timestamps?
- Is coverage high enough?
- Is there any future leakage risk?
- Is direction semantics explicit?

Existing artifacts likely involved:

```text
factor_library_state.json
factor_formula_registry.py
factor_specs.py
factor_ops.py
factor_level_coverage_summary.csv
check_factor_registry_integrity.py
```

### 4.2 Predictive ranking evidence

Questions:

- Does the factor have stable RankIC?
- Is ICIR meaningful?
- Is monthly IC stable or regime-dependent?
- Is IC based on enough observations?

Existing artifacts likely involved:

```text
factor_level_metric_panel.csv
factor_level_rankic_summary.csv
factor_level_period_ic_summary.csv
factor_monthly_ic_series.csv
```

### 4.3 Portfolio extraction evidence

Questions:

- Does the factor produce usable top-bottom long-short returns?
- Are Sharpe, annualized return, volatility, drawdown, positive month rate reasonable?
- Are returns dominated by a few months?
- Does the cumulative curve look stable or path-dependent?

Existing artifacts likely involved:

```text
factor_level_period_long_short_summary.csv
factor_monthly_long_short_series.csv
factor_cumulative_long_short_curve.csv
factor_diagnostics_summary.csv
```

### 4.4 Quantile shape / monotonicity

Questions:

- Are bucket returns monotonic or at least near-monotonic?
- Is signal only present in tails?
- Does RankIC disagree with quantile shape?

Existing artifacts likely involved:

```text
factor_level_quantile_return_summary.csv
factor_level_period_quantile_return_summary.csv
```

### 4.5 Direction and economic interpretation

Questions:

- Is expected direction positive/negative/conditional?
- Does the bilingual explanation match the formula?
- Is direction ambiguous or regime-dependent?
- Does metadata overstate the factor?

Existing artifacts likely involved:

```text
factor_bilingual_cards.csv
factor_card_qa_report.csv
```

### 4.6 Novelty / redundancy

Questions:

- Is the factor distinct from existing factors?
- Is it redundant with same-family factors?
- Is redundancy sufficiently measured, or still sparse?

Existing artifacts likely involved:

```text
factor_redundancy.csv
factor_intake/*/factor_redundancy.csv
```

### 4.7 Extensibility / intake readiness

Questions:

- Can a new factor be added through `run_factor_intake.py`?
- Does the new factor automatically receive diagnostics, metadata, page integration?
- What scripts must be rerun after new factors are added?

Existing artifacts likely involved:

```text
START_HERE.md
run_factor_intake.py
build_factor_values.py
evaluate_factors.py
build_factor_diagnostics_metrics.py
build_factor_bilingual_cards.py
_build_factor_eval_html.py
```

## 5. Required evidence inventory CSV

Create:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_inventory.csv
```

One row per evidence dimension.

Columns:

```text
dimension
question
existing_artifact
existing_status
is_displayed_on_factor_page
current_gap
severity
recommended_next_task
notes
```

Severity values:

```text
NONE
LOW
MEDIUM
HIGH
BLOCKING
```

## 6. Required framework JSON

Create:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_framework_spec.json
```

This should define a future factor quality scorecard schema, but do not implement the scorecard yet.

Suggested structure:

```json
{
  "framework_version": "pm16a_v1",
  "dimensions": [
    {
      "name": "computation_integrity",
      "required_evidence": [...],
      "source_artifacts": [...],
      "future_score_fields": [...]
    }
  ],
  "recommended_scorecard_fields": [...],
  "do_not_use_as_trade_signal": true
}
```

## 7. Required audit note

Create:

```text
docs/factor_library/audits/pm16a_factor_evaluation_sufficiency_framework.md
```

The audit note must include:

1. Summary verdict:
   - `EVALUATION_FRAMEWORK_READY`
   - `EVALUATION_FRAMEWORK_READY_WITH_GAPS`
   - `EVALUATION_FRAMEWORK_BLOCKED`
2. Current repository state: factor count, computed count, page count, current page capability.
3. Evidence dimensions and whether each is covered.
4. Whether current factor-evaluation page is sufficient to evaluate factor quality.
5. Specific gaps that remain.
6. Clarification of RankIC vs Sharpe: not a simple contradiction, but two different evidence dimensions.
7. Recommended next 3–5 PM tasks.
8. Non-change statement: no factors, no formulas, no factor_values, no signal panel, no public pages.

## 8. Expected recommendation logic

The next plan should likely be:

### PM-16B — Factor Quality Scorecard Builder

Implement a transparent scorecard from the PM-16A framework. It should synthesize evidence dimensions into a review status such as:

```text
STRONG_RESEARCH_CANDIDATE
PROMISING_BUT_INCONSISTENT
DIRECTION_DEPENDENT
REDUNDANT_OR_WEAK
INSUFFICIENT_EVIDENCE
REVIEW_REQUIRED
```

### PM-17 — Integrate Scorecard into Existing Factor Evaluation Page

Update existing `factor-evaluation.html` to show scorecard dimensions and explanation.

### PM-18 — Extensibility / Regeneration Contract

Document and script the exact regeneration sequence after new factors are added:

```text
build_factor_values → evaluate_factors → build_factor_diagnostics_metrics → build_factor_bilingual_cards → build_factor_quality_scorecard → _build_factor_eval_html
```

### PM-19 — Factor Expansion Backlog

Only after scorecard and regeneration contract are stable, return to factor expansion.

## 9. Validation

Run lightweight checks only. Do not run expensive evaluation.

```bash
python - <<'PY'
import json
from pathlib import Path
paths = [
 'research/factor_runs/crypto_top50_factor_library/factor_library_state.json',
 'research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv',
 'research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_bilingual_cards.csv',
 'reports/site/factor-library/factor-evaluation.html',
]
for p in paths:
    print(p, Path(p).exists())
PY
```

## 10. Allowed files to change

Allowed:

```text
docs/factor_library/audits/pm16a_factor_evaluation_sufficiency_framework.md
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_inventory.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_framework_spec.json
```

Do not edit public pages in this task.

## 11. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
docs: define factor evaluation sufficiency framework
```

Final response should include:

- commit hash
- summary verdict
- whether current page is sufficient or insufficient and why
- highest-severity gaps
- recommended next 3–5 PM tasks
