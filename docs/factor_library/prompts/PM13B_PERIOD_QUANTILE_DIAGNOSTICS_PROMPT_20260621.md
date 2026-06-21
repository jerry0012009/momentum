# PM-13B Prompt — Period-Level Quantile Returns and Complete Factor Diagnostics

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-13:

- `docs/factor_library/audits/pm13_factor_diagnostics_metrics_builder.md`
- `scripts/build_factor_diagnostics_metrics.py`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/`

PM-13 successfully refreshed canonical factor evaluation to all 71 factors and generated monthly IC diagnostics, but it could not generate monthly long-short returns, cumulative long-short curves, Sharpe, annualized return/volatility, or drawdown because `factor_level_quantile_return_summary.csv` is aggregate-only and has no period/month column.

PM-13 identified the root cause: `scripts/evaluate_factors.py` already computes per-timestamp bucket returns internally:

```python
bucket_ts = hz_merged.groupby(["timestamp", "bucket"])[ret_col].mean().unstack(fill_value=np.nan)
```

but it only writes aggregate bucket means and aggregate long-short rows, not period-level/monthly bucket returns.

## 0. PM objective

Extend the existing canonical factor evaluator to output period-level quantile and long-short return diagnostics, then re-run the diagnostics builder to populate:

- monthly long-short return series;
- cumulative long-short curve;
- Sharpe ratio;
- annualized return;
- annualized volatility;
- max drawdown;
- positive long-short month rate.

This task completes the PM-13 metrics layer. It should not build public pages yet.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify `scripts/factor_formula_registry.py`.

Do **not** modify `scripts/factor_ops.py`.

Do **not** modify signal panel construction.

Do **not** modify `scripts/build_phase9b_signal_panel.py`.

Do **not** rebuild signal panel.

Do **not** build or modify public HTML pages.

Do **not** create a separate parallel evaluator.

Do **not** recompute IC from raw factor_values in a new script.

Do **not** fabricate monthly long-short data from aggregate returns.

Do **not** make production/live/tradeability/alpha claims.

## 2. Repository structure to respect

Current canonical research root:

```text
research/factor_runs/crypto_top50_factor_library/
```

Canonical factor evaluation outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/
```

Diagnostics metrics outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/
```

Existing scripts:

```text
scripts/evaluate_factors.py
scripts/build_factor_diagnostics_metrics.py
scripts/build_factor_library_state.py
```

Keep this structure. Do not create a new parallel directory tree.

## 3. Required pre-checks

Run:

```bash
git status --short
```

Inspect schemas from PM-13 outputs:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_level_evaluation')
for name in [
    'factor_level_quantile_return_summary.csv',
    'factor_level_long_short_summary.csv',
    'factor_level_period_ic_summary.csv',
]:
    p = base / name
    print('\n', name, p.exists())
    if p.exists():
        df = pd.read_csv(p)
        print('rows=', len(df))
        print('cols=', list(df.columns))
        if 'factor_name' in df.columns:
            print('n_factors=', df['factor_name'].nunique())
        if 'factor_id' in df.columns:
            print('n_factors=', df['factor_id'].nunique())
        for c in ['period', 'month', 'timestamp', 'horizon', 'bucket']:
            if c in df.columns:
                print(c, 'sample=', df[c].dropna().head().tolist())
PY
```

Confirm PM-13 diagnostics manifest says monthly LS is unavailable before this task.

## 4. Extend `scripts/evaluate_factors.py`

Modify the existing quantile/long-short section in `evaluate_factors.py`.

Current aggregate behavior must remain backward-compatible:

- Keep writing `factor_level_quantile_return_summary.csv` as before.
- Keep writing `factor_level_long_short_summary.csv` as before.
- Do not remove or rename existing columns.

Add new outputs:

```text
factor_level_period_quantile_return_summary.csv
factor_level_period_long_short_summary.csv
```

These should be written to the same output directory and respect any existing suffix/output-dir behavior if the evaluator supports suffixes.

### 4.1 `factor_level_period_quantile_return_summary.csv`

Required columns:

```text
factor_name
category
expected_direction
horizon
period
bucket
bucket_label
mean_forward_return
median_forward_return
n_timestamps
n_obs
status
```

Period should be monthly, string format `YYYY-MM`.

Recommended computation:

- `bucket_ts` already has timestamp index and bucket columns.
- Convert timestamp index to monthly period.
- For each month and bucket, compute mean/median of timestamp-level bucket returns.
- `n_timestamps`: number of timestamps in that month with non-null bucket return.
- `n_obs`: if raw per-symbol obs count is not easily available by bucket/month, use null or a documented approximation. Do not invent precision.

### 4.2 `factor_level_period_long_short_summary.csv`

Required columns:

```text
factor_name
category
expected_direction
horizon
period
long_short_return
long_leg_return
short_leg_return
n_timestamps
positive_ls
status
```

Recommended computation:

- From `bucket_ts`, compute per-timestamp LS as `top_bucket - bottom_bucket`.
- Group per-timestamp LS by month.
- `long_short_return`: mean monthly LS return.
- `long_leg_return`: mean monthly top bucket return.
- `short_leg_return`: mean monthly bottom bucket return.
- `positive_ls`: `long_short_return > 0`.

Important: continue respecting direction-adjusted sorting already used by the evaluator. Do not alter factor direction semantics in this task.

## 5. Extend `scripts/build_factor_diagnostics_metrics.py`

Update the diagnostics builder to consume the new period-level long-short output.

Expected behavior after PM-13B:

- `factor_monthly_long_short_series.csv` should be populated.
- `factor_cumulative_long_short_curve.csv` should be populated.
- `factor_diagnostics_summary.csv/json` should include non-null values for:
  - `long_short_mean`
  - `long_short_std`
  - `long_short_sharpe`
  - `long_short_annualized_return`
  - `long_short_annualized_vol`
  - `long_short_max_drawdown`
  - `long_short_positive_month_rate`
  where enough data exists.

Use formulas from PM-12:

```text
long_short_sharpe = mean(monthly_LS) / std(monthly_LS) * sqrt(12)
long_short_annualized_return = mean(monthly_LS) * 12
long_short_annualized_vol = std(monthly_LS) * sqrt(12)
cum_long_short_return = cumulative product of (1 + monthly_LS) - 1
drawdown = cumulative_value / rolling_peak - 1
positive month rate = fraction of months with monthly_LS > 0
```

Guardrails:

- If monthly LS std is zero or insufficient data, leave Sharpe null and set warning.
- Do not compute Sharpe from aggregate LS mean/t-stat.
- Use monthly returns only.
- Preserve PM-13 monthly IC behavior.

## 6. Required runs

Run py_compile:

```bash
python -m py_compile \
  scripts/evaluate_factors.py \
  scripts/build_factor_diagnostics_metrics.py \
  scripts/build_factor_library_state.py
```

Re-run canonical factor evaluation because evaluator output schema changed:

```bash
python scripts/evaluate_factors.py \
  --dataset-id crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1
```

Then run diagnostics builder:

```bash
python scripts/build_factor_diagnostics_metrics.py \
  --input-dir research/factor_runs/crypto_top50_factor_library/factor_level_evaluation \
  --state-path research/factor_runs/crypto_top50_factor_library/factor_library_state.json \
  --output-dir research/factor_runs/crypto_top50_factor_library/factor_diagnostics
```

## 7. Validation checks

Inspect output row counts:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
paths = [
 'research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_period_quantile_return_summary.csv',
 'research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_period_long_short_summary.csv',
 'research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_long_short_series.csv',
 'research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_cumulative_long_short_curve.csv',
 'research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv',
]
for p in paths:
    p = Path(p)
    print('\n', p.name, 'exists=', p.exists())
    if p.exists():
        df = pd.read_csv(p)
        print('rows=', len(df), 'cols=', list(df.columns))
        for c in ['factor_name','factor_id']:
            if c in df.columns:
                print('n_factors=', df[c].nunique())
        if 'period' in df.columns:
            print('periods=', df['period'].nunique(), df['period'].dropna().head().tolist())
        if 'month' in df.columns:
            print('months=', df['month'].nunique(), df['month'].dropna().head().tolist())
PY
```

Spot-check that summary has non-null Sharpe/drawdown for factors with enough monthly LS data:

```bash
python - <<'PY'
import pandas as pd
p = 'research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv'
df = pd.read_csv(p)
cols = ['factor_id','best_horizon','long_short_sharpe','long_short_max_drawdown','long_short_positive_month_rate']
print(df[cols].head(20).to_string(index=False))
print('non_null_sharpe', df['long_short_sharpe'].notna().sum())
print('non_null_drawdown', df['long_short_max_drawdown'].notna().sum())
PY
```

## 8. Required audit note

Create:

```text
docs/factor_library/audits/pm13b_period_quantile_diagnostics.md
```

The audit note must include:

1. Summary verdict:
   - `PERIOD_LS_DIAGNOSTICS_PASS`
   - `PARTIAL_PASS_PERIOD_LS_LIMITED`
   - `BLOCKED_EVALUATOR_SCHEMA`
2. Code changes made.
3. New evaluator outputs generated.
4. Diagnostics outputs generated.
5. Whether monthly LS is now available.
6. Whether cumulative LS curve is now available.
7. Whether Sharpe is now available.
8. Whether drawdown is now available.
9. Factor count and horizon count.
10. Known limitations of monthly aggregation.
11. Non-change statement: no factor formulas, no signal panel, no public pages.
12. Recommended next PM.

## 9. Allowed files to change

Allowed code:

- `scripts/evaluate_factors.py`
- `scripts/build_factor_diagnostics_metrics.py`

Allowed generated evaluation outputs:

- `research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/*`

Allowed generated diagnostics:

- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/*`

Allowed audit:

- `docs/factor_library/audits/pm13b_period_quantile_diagnostics.md`

Do not edit public pages in this task.

## 10. Stop conditions

Stop and report if:

- evaluator refresh fails;
- period-level bucket returns cannot be generated from existing `bucket_ts` without changing factor semantics;
- diagnostics builder cannot compute monthly LS after evaluator extension;
- output factor count falls below 71;
- new code breaks existing aggregate evaluator outputs;
- Sharpe/drawdown would require fabricated or aggregate-only data.

## 11. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: add period-level factor long-short diagnostics
```

Final response should include:

- commit hash
- summary verdict
- evaluator outputs added
- diagnostics outputs populated
- factor/horizon/month counts
- whether monthly LS, cumulative curve, Sharpe, and drawdown are now available
- limitations
- next recommended PM
