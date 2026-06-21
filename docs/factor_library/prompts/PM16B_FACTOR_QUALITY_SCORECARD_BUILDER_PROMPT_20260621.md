# PM-16B Prompt — Factor Quality Scorecard Builder

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-16A:

- `docs/factor_library/audits/pm16a_factor_evaluation_sufficiency_framework.md`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_inventory.csv`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_framework_spec.json`

PM-16A concluded that the current factor evaluation page is sufficient for most factor-quality review, but important gaps remain. The next step is to build a transparent factor quality scorecard from existing evidence.

## 0. PM objective

Implement a reproducible, rule-based factor quality scorecard builder.

The scorecard should synthesize the evidence dimensions defined in PM-16A into one row per factor, with transparent sub-scores and a final review class.

The scorecard is **not** a trading signal selector. It is a research triage tool to help decide which factors deserve further review.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify `scripts/factor_formula_registry.py`.

Do **not** modify `scripts/factor_ops.py`.

Do **not** modify signal panel construction.

Do **not** rebuild signal panel.

Do **not** modify public HTML pages in PM-16B. Page integration is PM-17.

Do **not** make production/live/tradeability/alpha claims.

Do **not** over-weight redundancy, because PM-16A found redundancy coverage is sparse: only 6/2485 pairs currently measured.

Do **not** treat RankIC vs Sharpe disagreement as a simplistic contradiction. It should influence the score through separate dimensions: predictive ranking and portfolio extraction.

## 2. Inputs to consume

Read:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_framework_spec.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evaluation_evidence_inventory.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_ic_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_long_short_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_cumulative_long_short_curve.csv
research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_bilingual_cards.csv
research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_card_qa_report.csv
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_quantile_return_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_period_quantile_return_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_metric_panel.csv
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_redundancy.csv
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
```

If some optional files are missing, continue with explicit confidence flags, except core files `factor_diagnostics_summary.csv` and `factor_bilingual_cards.csv`, which are required.

## 3. Required script

Create:

```text
scripts/build_factor_quality_scorecard.py
```

The script should write:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard_manifest.json
```

## 4. Required scorecard schema

One row per factor.

Required columns:

```text
factor_id
name_zh
name_en
family
metadata_quality
best_horizon
final_quality_class
final_quality_score
score_confidence
computation_integrity_score
predictive_ranking_score
portfolio_extraction_score
stability_score
quantile_shape_score
direction_interpretability_score
redundancy_novelty_score
redundancy_confidence
coverage_rate
rankic_mean
rankic_ir
monthly_ic_positive_rate
long_short_sharpe
long_short_annualized_return
long_short_max_drawdown
long_short_positive_month_rate
quantile_shape
main_strengths_zh
main_weaknesses_zh
main_strengths_en
main_weaknesses_en
review_notes_zh
review_notes_en
recommended_next_action
```

## 5. Final quality classes

Use the following final classes:

```text
STRONG_RESEARCH_CANDIDATE
PROMISING_BUT_INCONSISTENT
DIRECTION_DEPENDENT
REDUNDANT_OR_WEAK
INSUFFICIENT_EVIDENCE
REVIEW_REQUIRED
```

Definitions:

### STRONG_RESEARCH_CANDIDATE

Strong ranking evidence, usable portfolio extraction, acceptable stability, acceptable drawdown, non-ambiguous or explainable direction, enough coverage.

### PROMISING_BUT_INCONSISTENT

Has meaningful RankIC or portfolio evidence, but evidence is mixed across IC, Sharpe, monthly stability, or quantile shape.

### DIRECTION_DEPENDENT

Potential signal exists, but metadata_quality or expected_direction indicates conditional or ambiguous interpretation.

### REDUNDANT_OR_WEAK

Weak predictive/portfolio evidence, or likely redundant when redundancy evidence is available.

Important: because redundancy matrix is sparse, do **not** classify a factor as redundant solely because no redundancy data exists. Use `redundancy_confidence`.

### INSUFFICIENT_EVIDENCE

Missing or insufficient metrics, low coverage, or severe computation/input gaps.

### REVIEW_REQUIRED

Metadata/formula/direction flags require human review before any quality judgment.

## 6. Scoring dimensions

Use transparent rule-based scoring, not ML.

Each dimension should be 0–100.

### 6.1 computation_integrity_score

Inputs:

- factor_values computed;
- coverage_rate;
- source_warning;
- metadata required fields.

Suggested rules:

- coverage >= 0.95 → strong;
- coverage 0.80–0.95 → medium;
- coverage < 0.80 → weak;
- source warnings reduce score.

### 6.2 predictive_ranking_score

Inputs:

- rankic_mean;
- rankic_ir;
- rankic_t_stat;
- monthly_ic_positive_rate.

Treat RankIC as ranking evidence, not PnL.

### 6.3 portfolio_extraction_score

Inputs:

- long_short_sharpe;
- annualized return;
- max drawdown;
- positive month rate.

Do not promote factors solely because Sharpe is positive. Use as one dimension.

### 6.4 stability_score

Inputs:

- monthly_ic_positive_rate;
- monthly long-short positive month rate;
- cumulative curve drawdown.

### 6.5 quantile_shape_score

Inputs:

- factor_level_quantile_return_summary.csv;
- factor_level_period_quantile_return_summary.csv if useful.

Compute simple aggregate quantile monotonicity for the best horizon:

- MONOTONIC_GOOD
- NEAR_MONOTONIC
- NON_MONOTONIC
- INSUFFICIENT

Do not over-engineer. A simple Q1–Q5 return shape check is enough.

### 6.6 direction_interpretability_score

Inputs:

- metadata_quality;
- expected_direction;
- review flags;
- factor card QA report.

Direction ambiguous factors can still be promising, but should not become `STRONG_RESEARCH_CANDIDATE` without review.

### 6.7 redundancy_novelty_score

Inputs:

- factor_redundancy.csv if available.

Because PM-16A found only 6/2485 pairs covered, set:

```text
redundancy_confidence = LOW
```

unless a factor has explicit redundancy evidence.

Do not assume missing redundancy means uniqueness.

## 7. Score confidence

Use:

```text
HIGH
MEDIUM
LOW
```

Score confidence should fall if:

- metadata_quality is not COMPLETE;
- redundancy evidence is missing;
- quantile shape is non-monotonic;
- coverage is low;
- monthly evidence is sparse.

## 8. Recommended next action

Use controlled vocabulary:

```text
KEEP_FOR_RESEARCH_REVIEW
REVIEW_DIRECTION_BEFORE_USE
REVIEW_FORMULA_OR_METADATA
REVIEW_REDUNDANCY_FIRST
LOW_PRIORITY_WEAK_EVIDENCE
INSUFFICIENT_DATA
```

Do not use words like BUY, SELL, TRADE, DEPLOY, PRODUCTION, LIVE.

## 9. Required audit note

Create:

```text
docs/factor_library/audits/pm16b_factor_quality_scorecard.md
```

The audit note must include:

1. Summary verdict:
   - `FACTOR_SCORECARD_PASS`
   - `FACTOR_SCORECARD_PASS_WITH_LIMITATIONS`
   - `FACTOR_SCORECARD_BLOCKED`
2. Files generated.
3. Factor count coverage.
4. Distribution of final_quality_class.
5. Distribution of score_confidence.
6. Top 10 factors by final_quality_score.
7. Examples of each quality class where present.
8. Explicit treatment of RankIC vs Sharpe as separate evidence dimensions.
9. Explicit limitation: redundancy matrix sparse; novelty score is low-confidence until PM-18.
10. Non-change statement: no formulas, no factors, no factor_values, no signal panel, no public pages.
11. Recommended next PM.

## 10. Validation

Run:

```bash
python -m py_compile scripts/build_factor_quality_scorecard.py
python scripts/build_factor_quality_scorecard.py
```

Then run:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
p = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv')
df = pd.read_csv(p)
print('rows', len(df))
print('factors', df['factor_id'].nunique())
print('classes')
print(df['final_quality_class'].value_counts())
print('confidence')
print(df['score_confidence'].value_counts())
print('score range', df['final_quality_score'].min(), df['final_quality_score'].max())
PY
```

Expected:

- rows = 71;
- factor_id unique = 71;
- final_quality_class not empty;
- score_confidence not empty;
- final_quality_score bounded 0–100.

## 11. Allowed files to change

Allowed code:

```text
scripts/build_factor_quality_scorecard.py
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard_manifest.json
```

Allowed audit:

```text
docs/factor_library/audits/pm16b_factor_quality_scorecard.md
```

Do not edit public pages in this task.

## 12. Stop conditions

Stop and report if:

- core diagnostics summary is missing;
- factor metadata cannot join to diagnostics at 71 factors;
- final quality classes cannot be assigned without overclaiming;
- scorecard would require modifying formulas, signals, or factor_values;
- redundancy gaps make novelty scoring impossible — in that case set redundancy confidence LOW rather than stopping.

## 13. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: build factor quality scorecard
```

Final response should include:

- commit hash
- summary verdict
- factor count coverage
- final quality class distribution
- score confidence distribution
- top 10 factors by score
- major limitations
- recommended next PM
