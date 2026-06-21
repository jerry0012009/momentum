# PM-16 Prompt — Factor Evidence Consistency Audit and Evaluation Page Warnings

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-15:

- `docs/factor_library/audits/pm15_factor_evaluation_page_integration.md`
- `scripts/_build_factor_eval_html.py`
- `reports/site/factor-library/factor-evaluation.html`

PM-15 upgraded the existing factor evaluation page with bilingual factor cards, diagnostics metrics, and charts. However, a critical product issue remains: some factors may show positive RankIC but negative Sharpe / negative long-short behavior. The page must make these conflicts explicit so users do not overinterpret one metric.

## 0. PM objective

Create a factor evidence consistency layer that audits agreement/disagreement among:

- RankIC / direction-adjusted IC;
- ICIR;
- monthly IC positive rate;
- long-short mean;
- Sharpe;
- max drawdown;
- long-short positive month rate;
- quantile monotonicity;
- metadata quality / direction ambiguity.

Then update the existing factor evaluation page to display these consistency warnings clearly.

Do **not** create a new public page. Upgrade the existing page:

```text
reports/site/factor-library/factor-evaluation.html
```

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify `scripts/factor_formula_registry.py`.

Do **not** modify `scripts/factor_ops.py`.

Do **not** modify signal panel construction.

Do **not** rebuild signal panel.

Do **not** create a new public page.

Do **not** use external CDN dependencies.

Do **not** make production/live/tradeability/alpha claims.

Do **not** hide metric conflicts. The purpose of this PM is to expose conflicts.

## 2. Background: why RankIC positive and Sharpe negative can both be true

The page must explain this clearly.

RankIC measures cross-sectional rank association between factor values and forward returns at each timestamp.

Long-short Sharpe measures the return quality of a specific top-minus-bottom bucket construction over monthly periods.

These can diverge when:

1. the factor ranks the full universe correctly on average, but the extreme top/bottom buckets do not monetize well;
2. the quantile return curve is non-monotonic;
3. the selected horizon is IC-optimal but not LS-optimal;
4. the factor has regime dependence or direction ambiguity;
5. the long-short return series has negative mean or high volatility despite positive IC;
6. a few bad months dominate cumulative PnL even if IC is usually positive;
7. conditional factors are sorted one way but economic interpretation is not stable.

The page should treat `RankIC positive + Sharpe negative` as a warning, not automatically as a bug or as a tradable failure. It means the evidence is mixed and requires review.

## 3. Existing inputs to consume

Use existing artifacts:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_ic_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_long_short_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_cumulative_long_short_curve.csv
research/factor_runs/crypto_top50_factor_library/factor_metadata/factor_bilingual_cards.csv
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_metric_panel.csv
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_quantile_return_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_period_long_short_summary.csv
```

## 4. Required new outputs

Create:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evidence_consistency_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evidence_consistency_by_horizon.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evidence_consistency_manifest.json
```

Create or update a script:

```text
scripts/build_factor_evidence_consistency.py
```

Then update:

```text
scripts/_build_factor_eval_html.py
reports/site/factor-library/factor-evaluation.html
```

## 5. Required consistency fields

### 5.1 `factor_evidence_consistency_by_horizon.csv`

One row per factor × horizon.

Required fields:

```text
factor_id
horizon
metadata_quality
expected_direction
rankic_mean
rankic_ir
monthly_ic_positive_rate
long_short_mean
long_short_sharpe
long_short_max_drawdown
long_short_positive_month_rate
quantile_shape
ic_sign
sharpe_sign
ls_mean_sign
evidence_consistency
warning_flags
review_priority
explanation_zh
explanation_en
```

### 5.2 `factor_evidence_consistency_summary.csv`

One row per factor, focused on best horizon currently used on the page.

Required fields:

```text
factor_id
best_horizon
evidence_consistency
warning_flags
review_priority
primary_warning_zh
primary_warning_en
recommended_display_badge_zh
recommended_display_badge_en
```

## 6. Warning flag taxonomy

Use semicolon-separated warning flags.

At minimum support:

```text
IC_POS_SHARPE_NEG
IC_NEG_SHARPE_POS
IC_POS_LS_MEAN_NEG
IC_NEG_LS_MEAN_POS
SHARPE_NEGATIVE
HIGH_DRAWDOWN
LOW_IC_POSITIVE_RATE
LOW_LS_POSITIVE_RATE
NON_MONOTONIC_QUANTILES
DIRECTION_AMBIGUOUS
FORMULA_AMBIGUOUS
NEEDS_REVIEW_METADATA
LOW_COVERAGE
NO_WARNING
```

Do not overflag trivial near-zero values. Use small thresholds, for example:

- IC sign only if `abs(rankic_mean) >= 0.005`;
- Sharpe sign only if `abs(long_short_sharpe) >= 0.1`;
- long-short mean sign only if `abs(long_short_mean) >= 0.00005`;
- high drawdown if max drawdown < -0.02 unless the data scale suggests a better threshold;
- low positive month rate if < 0.45.

Document thresholds in manifest and audit.

## 7. Quantile monotonicity

Use `factor_level_quantile_return_summary.csv` to evaluate the aggregate quantile shape per factor × horizon.

For each factor/horizon:

- sort buckets Q1..Q5;
- check whether bucket returns are monotonic increasing or monotonic decreasing;
- if not monotonic or near-monotonic, flag `NON_MONOTONIC_QUANTILES`.

Be careful with direction-adjusted sorting. Use the same convention as existing evaluator output.

## 8. Page update requirements

Update the existing `factor-evaluation.html` via `scripts/_build_factor_eval_html.py`.

Add visible evidence warnings:

1. In main table, add a column:

```text
Evidence 证据一致性
```

2. In factor detail panel, add:

```text
Evidence Consistency / 证据一致性
```

with bilingual explanation.

3. Add a methodology note explaining why RankIC and Sharpe may disagree.

4. For factors with `IC_POS_SHARPE_NEG`, show a clear badge such as:

```text
IC positive but Sharpe negative / IC为正但夏普为负
```

5. Do not hide DIRECTION_AMBIGUOUS / NEEDS_REVIEW / FORMULA_AMBIGUOUS.

6. Add page build metadata to the footer or top summary:

```text
generated_at
factor_count
source: PM-15/PM-16 diagnostics
```

This makes deployment/cache mismatch easier to detect.

## 9. Validation

Run:

```bash
python -m py_compile scripts/build_factor_evidence_consistency.py scripts/_build_factor_eval_html.py
python scripts/build_factor_evidence_consistency.py
python scripts/_build_factor_eval_html.py
```

Then validate:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
summary = pd.read_csv(base / 'factor_evidence_consistency_summary.csv')
by_hz = pd.read_csv(base / 'factor_evidence_consistency_by_horizon.csv')
print('summary rows', len(summary), 'factors', summary['factor_id'].nunique())
print('by_hz rows', len(by_hz), 'factors', by_hz['factor_id'].nunique(), 'horizons', by_hz['horizon'].nunique())
print('warning counts')
print(summary['warning_flags'].value_counts().head(20))
html = Path('reports/site/factor-library/factor-evaluation.html').read_text(encoding='utf-8')
checks = [
  'Evidence', '证据一致性', 'IC_POS_SHARPE_NEG', 'IC为正但夏普为负',
  'generated_at', 'factor_count', 'Sharpe', '最大回撤'
]
for c in checks:
    print(c, c in html)
PY
```

Expected:

- summary rows = 71;
- by_hz rows = 284;
- factor count = 71;
- HTML contains evidence warning text.

## 10. Required audit note

Create:

```text
docs/factor_library/audits/pm16_factor_evidence_consistency_audit.md
```

The audit note must include:

1. Summary verdict:
   - `EVIDENCE_CONSISTENCY_PASS`
   - `EVIDENCE_CONSISTENCY_PASS_WITH_WARNINGS`
   - `EVIDENCE_CONSISTENCY_BLOCKED`
2. Files generated/changed.
3. Warning taxonomy and thresholds.
4. Count of factors by evidence consistency category.
5. Count of `IC_POS_SHARPE_NEG` factors.
6. Count of `NON_MONOTONIC_QUANTILES` factors.
7. Explanation of why RankIC and Sharpe can disagree.
8. Confirmation that existing factor-evaluation page was upgraded, not replaced.
9. Known limitations.
10. Non-change statement: no formulas, no factors, no factor_values, no signal panel.
11. Recommended next PM.

## 11. Allowed files to change

Allowed code:

```text
scripts/build_factor_evidence_consistency.py
scripts/_build_factor_eval_html.py
```

Allowed diagnostics outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evidence_consistency_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evidence_consistency_by_horizon.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_evidence_consistency_manifest.json
```

Allowed public output:

```text
reports/site/factor-library/factor-evaluation.html
reports/site/factor-library/assets/factor_diagnostics_payload.json
```

Allowed audit:

```text
docs/factor_library/audits/pm16_factor_evidence_consistency_audit.md
```

Do not edit other public pages in this task.

## 12. Stop conditions

Stop and report if:

- diagnostics summary cannot join to monthly series;
- by-horizon evidence cannot be computed for 71 × 4 rows;
- quantile shape cannot be evaluated from existing outputs;
- page builder cannot display warnings without breaking current page;
- implementing this would require changing formulas, signals, or factor_values.

## 13. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: add factor evidence consistency warnings
```

Final response should include:

- commit hash
- summary verdict
- files generated/changed
- factor and horizon coverage
- warning distribution
- number of IC-positive/Sharpe-negative factors
- whether page now displays evidence consistency warnings
- known limitations
- recommended next PM
