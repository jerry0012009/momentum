# PM-26 Prompt — Quantile Shape and Rolling Stability Diagnostics

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows:

- PM-21B: repaired single-factor paper portfolio data layer
- PM-22B: repaired paper portfolio page integration
- PM-23B: refreshed regime diagnostics using repaired paper returns
- PM-24B: refreshed regime section on factor-evaluation page
- PM-25: reusable staleness monitor + workflow reconciliation

Do **not** enter signal evaluation. We are still strengthening the factor evaluation layer.

## 0. PM objective

Add a reusable data-layer diagnostic module for:

1. **Quantile return shape** — whether a factor has monotonic Q1–Q5 / Q1–Q10 return behavior, whether spread comes from both tails or one extreme bucket, and whether quantile ordering is stable.
2. **Rolling stability** — rolling 3M / 6M RankIC and long-short stability, recent deterioration, and sign consistency.

This PM should create data outputs and compact payloads for future page integration. Do **not** update public HTML in PM-26.

## 1. Why this matters

The current factor page already has scorecard, redundancy, paper portfolio, fee sensitivity, turnover, drawdown, and BTC regime diagnostics.

However, professional factor evaluation still needs:

- quantile return shape;
- monotonicity diagnostics;
- tail dependence diagnostics;
- rolling 3M / 6M stability;
- recent-vs-full-period deterioration checks.

A factor with good average RankIC but poor quantile shape or unstable rolling IC should be treated differently from a stable, monotonic factor.

## 2. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** create or modify public HTML pages.

Do **not** recompute raw factor values.

Do **not** make production/live/trading claims.

Do **not** create a parallel factor evaluation pipeline. Use existing PM-13B / PM-21B diagnostics as inputs.

## 3. Required inputs

Use existing canonical outputs where available:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_level_period_quantile_return_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_level_period_long_short_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_ic_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_long_short_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
```

If exact file names differ, inspect the diagnostics directory and use the canonical PM-13B outputs.

Before running, execute or inspect PM-25 staleness report. If it recommends only `state`, run:

```bash
python scripts/run_factor_library_refresh.py --stage state
```

This is a cheap consistency cleanup, not a new PM.

## 4. Required script

Create:

```text
scripts/build_factor_shape_stability_diagnostics.py
```

Recommended CLI:

```bash
python scripts/build_factor_shape_stability_diagnostics.py
```

Optional arguments:

```bash
--min-months 6
--rolling-windows 3,6
--output-dir research/factor_runs/crypto_top50_factor_library/factor_diagnostics
```

## 5. Quantile shape diagnostics

Use period-level quantile return data.

For each `factor_id` and `horizon`, compute:

```text
n_months
n_quantile_buckets
q_low_return
q_high_return
q_spread_return
q_return_slope
q_spearman_corr
monotonicity_score
monotonicity_class
tail_concentration_score
tail_concentration_class
positive_spread_month_rate
quantile_shape_class
main_shape_note_zh
main_shape_note_en
```

Suggested definitions:

- `q_spread_return`: highest expected-direction bucket minus lowest expected-direction bucket.
- `q_return_slope`: linear slope of mean quantile return across ordered buckets.
- `q_spearman_corr`: Spearman correlation between quantile index and mean return.
- `monotonicity_score`: share of adjacent quantile steps moving in expected direction.
- `tail_concentration_score`: absolute contribution of extreme buckets relative to full spread.

Suggested classes:

```text
MONOTONIC_STRONG
MONOTONIC_WEAK
U_SHAPED_OR_REVERSAL
TAIL_DEPENDENT
FLAT_NO_SHAPE
INSUFFICIENT_DATA
```

Do not assume positive direction blindly. Use existing direction metadata where available. If unavailable, compute raw shape and mark direction uncertainty.

## 6. Rolling stability diagnostics

Use monthly RankIC and monthly long-short series.

For each `factor_id` and `horizon`, compute:

```text
n_months
rolling_ic_3m_mean_latest
rolling_ic_3m_min
rolling_ic_3m_max
rolling_ic_6m_mean_latest
rolling_ic_6m_min
rolling_ic_6m_max
rolling_ls_3m_mean_latest
rolling_ls_6m_mean_latest
ic_positive_month_rate
ls_positive_month_rate
recent_6m_ic_mean
full_period_ic_mean
recent_vs_full_ic_delta
recent_6m_ls_mean
full_period_ls_mean
recent_vs_full_ls_delta
stability_score
stability_class
main_stability_note_zh
main_stability_note_en
```

Suggested classes:

```text
STABLE_POSITIVE
STABLE_WEAK
RECENT_DETERIORATION
REGIME_OR_PERIOD_DEPENDENT
UNSTABLE_SIGN_FLIP
INSUFFICIENT_HISTORY
```

## 7. Required outputs

Write to:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/
```

Required outputs:

```text
factor_quantile_shape_summary.csv
factor_quantile_shape_summary.json
factor_rolling_stability_summary.csv
factor_rolling_stability_summary.json
factor_shape_stability_timeseries.csv
factor_shape_stability_payload.json
factor_shape_stability_manifest.json
```

Payload should be compact and suitable for later PM-27 page integration. Do not embed excessive raw rows.

## 8. Dynamic coverage requirements

Use expected factor count from `factor_library_state.json` or registry. Do not hardcode 71.

The audit must report:

```text
expected_factor_count
shape_summary_factor_count
stability_summary_factor_count
payload_factor_count
missing_factor_ids
```

If some factors lack enough history, keep them in outputs with `INSUFFICIENT_DATA`, not silently dropped.

## 9. Required audit

Create:

```text
docs/factor_library/audits/pm26_quantile_shape_rolling_stability.md
```

Audit must include:

1. Summary verdict:
   - `SHAPE_STABILITY_DIAGNOSTICS_PASS`
   - `SHAPE_STABILITY_DIAGNOSTICS_PASS_WITH_LIMITATIONS`
   - `SHAPE_STABILITY_DIAGNOSTICS_BLOCKED`
2. Why PM-26 is needed before factor expansion and signal construction.
3. Files changed.
4. Input files used.
5. Factor coverage.
6. Horizon coverage.
7. Quantile shape class distribution.
8. Rolling stability class distribution.
9. Examples of strong monotonic factors.
10. Examples of unstable or tail-dependent factors.
11. Payload size.
12. Validation results.
13. Limitations.
14. Non-change statement: no factors, formulas, factor_values, signal panel, public page.
15. Recommended next PM: PM-27 page integration for quantile/rolling diagnostics.

## 10. Validation

Run:

```bash
python -m py_compile scripts/build_factor_shape_stability_diagnostics.py
python scripts/build_factor_shape_stability_diagnostics.py
```

Then:

```bash
python - <<'PY'
import json
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
shape = pd.read_csv(base / 'factor_quantile_shape_summary.csv')
stab = pd.read_csv(base / 'factor_rolling_stability_summary.csv')
ts = pd.read_csv(base / 'factor_shape_stability_timeseries.csv')
payload = json.loads((base / 'factor_shape_stability_payload.json').read_text(encoding='utf-8'))
print('shape factors', shape['factor_id'].nunique())
print('stability factors', stab['factor_id'].nunique())
print('timeseries factors', ts['factor_id'].nunique())
print('payload factors', len(payload.get('factors', [])))
print('shape classes')
print(shape['quantile_shape_class'].value_counts(dropna=False).to_string())
print('stability classes')
print(stab['stability_class'].value_counts(dropna=False).to_string())
PY
```

Also run PM-25 monitor after outputs are generated:

```bash
python scripts/check_factor_library_staleness.py
```

If the monitor does not know about PM-26 outputs yet, do not force integration in this PM. Report as future PM-25B/PM-31 consideration.

## 11. Allowed files to change

Allowed script:

```text
scripts/build_factor_shape_stability_diagnostics.py
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quantile_shape_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quantile_shape_summary.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_rolling_stability_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_rolling_stability_summary.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_shape_stability_timeseries.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_shape_stability_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_shape_stability_manifest.json
```

Allowed audit:

```text
docs/factor_library/audits/pm26_quantile_shape_rolling_stability.md
```

Do not modify:

```text
reports/site/factor-library/factor-evaluation.html
scripts/_build_factor_eval_html.py
scripts/factor_formula_registry.py
scripts/factor_ops.py
scripts/build_factor_values.py
scripts/build_phase9b_signal_panel.py
```

## 12. Stop conditions

Stop and report if:

- period-level quantile return data is missing;
- monthly IC / long-short series is missing;
- factor coverage cannot be reconciled;
- implementation would require factor formula or factor_values changes;
- outputs become too large for the repository.

## 13. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: add quantile shape and rolling stability diagnostics
```

Final response should include:

- commit hash
- summary verdict
- factor coverage
- shape class distribution
- stability class distribution
- representative strong/weak examples
- validation results
- limitations
- recommended next PM
