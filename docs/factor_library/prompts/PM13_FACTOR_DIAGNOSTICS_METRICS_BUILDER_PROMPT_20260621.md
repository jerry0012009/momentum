# PM-13 Prompt — Factor Diagnostics Metrics Builder

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-12:

- `docs/factor_library/audits/pm12_factor_diagnostics_product_spec.md`

PM-12 confirmed that the factor library data layer is complete at 71 registered / 71 computed / 0 missing, but the user-facing factor evaluation layer is not decision-grade. Current factor evaluation artifacts are rich but incomplete as a product: no monthly IC curves, no monthly long-short / PnL curves, no Sharpe, no drawdown, no cumulative curve, no bilingual cards, and current public pages are basic.

PM-12 also found that existing factor-level evaluation artifacts appear to cover 65 factors, while the current registry has 71 factors. Therefore PM-13 must first verify whether canonical factor evaluation outputs include all 71 factors. If not, refresh canonical factor-level evaluation before building diagnostics metrics.

## 0. PM objective

Implement a new diagnostics metrics builder that converts canonical factor evaluation outputs into decision-grade machine-readable diagnostic artifacts.

This task should generate these outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_diagnostics_summary.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_ic_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_monthly_long_short_series.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_cumulative_long_short_curve.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/manifest.json
```

Also create a script:

```text
scripts/build_factor_diagnostics_metrics.py
```

Do not build public pages in this task. PM-13 is the data/metrics layer only.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify `scripts/factor_formula_registry.py`.

Do **not** modify `scripts/factor_ops.py`.

Do **not** modify signal panel construction.

Do **not** modify `scripts/build_phase9b_signal_panel.py`.

Do **not** rebuild signal panel.

Do **not** build or modify public HTML pages.

Do **not** make production/live/tradeability/alpha claims.

Do **not** create a parallel evaluator that recomputes factor IC from raw factor_values unless existing evaluation outputs lack the required fields and you explicitly document why.

Prefer consuming canonical outputs from `scripts/evaluate_factors.py`.

## 2. Required pre-checks

Run:

```bash
git status --short
```

Verify current state:

```bash
python - <<'PY'
import json
from pathlib import Path
p = Path('research/factor_runs/crypto_top50_factor_library/factor_library_state.json')
state = json.loads(p.read_text())
print('registered', state.get('registered_factors'))
print('computed', state.get('computed_factor_values'))
print('missing_fv', state.get('missing_factor_values'))
print('missing_input', state.get('missing_input'))
PY
```

If key names differ, inspect and print the relevant count fields.

Inspect current factor evaluation artifact schemas:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_level_evaluation')
for name in [
    'factor_level_metric_panel.csv',
    'factor_level_rankic_summary.csv',
    'factor_level_period_ic_summary.csv',
    'factor_level_quantile_return_summary.csv',
    'factor_level_long_short_summary.csv',
    'factor_level_candidate_review.csv',
    'factor_level_coverage_summary.csv',
]:
    p = base / name
    print('\n', name, 'exists=', p.exists())
    if p.exists():
        df = pd.read_csv(p)
        print('rows=', len(df), 'cols=', list(df.columns))
        if 'factor_id' in df.columns:
            print('n_factors=', df['factor_id'].nunique())
        if 'horizon' in df.columns:
            print('horizons=', sorted(map(str, df['horizon'].dropna().unique()))[:20])
        for c in ['period', 'month', 'date']:
            if c in df.columns:
                print(c, 'sample=', df[c].dropna().head().tolist())
PY
```

## 3. Refresh canonical factor evaluation if needed

If the canonical factor-level evaluation outputs do not include all 71 factors, run the canonical factor evaluation once:

```bash
python scripts/evaluate_factors.py \
  --dataset-id crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1
```

Only do this if needed.

Do not rebuild public pages.

After running, verify the main factor-level outputs include 71 factor IDs, or explain why any factor is excluded.

## 4. Implement `scripts/build_factor_diagnostics_metrics.py`

The script should be read-only with respect to factor_values and evaluation outputs. It should consume canonical evaluation artifacts and write derived diagnostics artifacts under:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/
```

Recommended CLI:

```bash
python scripts/build_factor_diagnostics_metrics.py \
  --input-dir research/factor_runs/crypto_top50_factor_library/factor_level_evaluation \
  --state-path research/factor_runs/crypto_top50_factor_library/factor_library_state.json \
  --output-dir research/factor_runs/crypto_top50_factor_library/factor_diagnostics
```

The script should fail loudly with a clear error if required input files are missing.

## 5. Required output schemas

### 5.1 `factor_monthly_ic_series.csv`

One row per factor × horizon × month.

Required columns:

```text
factor_id
horizon
month
rank_ic
rank_ic_adj
n_obs
positive_ic
```

Source: `factor_level_period_ic_summary.csv` if it has monthly/period-level IC.

If column names differ, map carefully and document mapping in manifest.

### 5.2 `factor_monthly_long_short_series.csv`

One row per factor × horizon × month.

Required columns:

```text
factor_id
horizon
month
long_short_return
long_leg_return
short_leg_return
n_long
n_short
positive_ls
```

Preferred source: monthly bucket-level quantile return data, if available.

Important: inspect the actual `factor_level_quantile_return_summary.csv` schema. If it lacks a month/period column, do **not** fabricate monthly long-short data. In that case:

1. generate an empty or partial file with documented status;
2. set manifest warning `monthly_long_short_unavailable=true`;
3. explain that PM-13B or evaluator extension is needed to output period-level quantile returns.

Do not invent monthly LS by spreading aggregate returns across months.

### 5.3 `factor_cumulative_long_short_curve.csv`

One row per factor × horizon × month.

Required columns:

```text
factor_id
horizon
month
long_short_return
cum_long_short_return
drawdown
```

Only compute if monthly long-short series is available.

Use simple return compounding:

```text
cum_long_short_return = cumulative product of (1 + monthly_long_short_return) - 1
```

Drawdown:

```text
drawdown = cumulative_value / rolling_peak - 1
```

If monthly LS is unavailable, produce a documented partial/empty file and manifest warning.

### 5.4 `factor_diagnostics_summary.csv/json`

One row per factor.

Required columns:

```text
factor_id
family
lifecycle_status
required_columns
expected_direction
best_horizon
rankic_mean
rankic_std
rankic_ir
rankic_t_stat
monthly_ic_positive_rate
long_short_mean
long_short_std
long_short_sharpe
long_short_annualized_return
long_short_annualized_vol
long_short_max_drawdown
long_short_positive_month_rate
coverage_rate
redundancy_level
nearest_redundant_factor
decision_bucket
recommended_action
source_warning
```

Use best horizon from existing coverage/candidate/metric outputs if available. If best horizon is ambiguous, choose the horizon with highest absolute direction-adjusted IC and document rule in manifest.

Metric formulas:

- `monthly_ic_positive_rate`: fraction of months with positive `rank_ic_adj` if available, else positive `rank_ic`.
- `long_short_mean`: mean monthly long-short return if monthly LS is available.
- `long_short_std`: std monthly long-short return.
- `long_short_sharpe`: `mean / std * sqrt(12)` if std > 0.
- `long_short_annualized_return`: `mean * 12`.
- `long_short_annualized_vol`: `std * sqrt(12)`.
- `long_short_max_drawdown`: min drawdown from cumulative LS curve.
- `long_short_positive_month_rate`: fraction of months with positive LS.
- `coverage_rate`: from coverage summary if available.
- `redundancy_level` and `nearest_redundant_factor`: from redundancy file if available. If redundancy is sparse, mark `source_warning`.

If monthly LS is unavailable, leave LS risk metrics null and set `source_warning` clearly. Do not fabricate Sharpe.

## 6. Manifest

Create:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/manifest.json
```

Must include:

- generated_at
- input files used
- output files generated
- factor_count
- horizon_count
- whether factor evaluation was refreshed in this task
- whether monthly IC is available
- whether monthly LS is available
- whether cumulative LS curve is available
- warnings
- metric formula definitions

## 7. Required audit note

Create:

```text
docs/factor_library/audits/pm13_factor_diagnostics_metrics_builder.md
```

The audit note must include:

1. Summary verdict:
   - `DIAGNOSTICS_METRICS_PASS`
   - `PARTIAL_PASS_MONTHLY_LS_MISSING`
   - `BLOCKED_SCHEMA_GAP`
2. Whether full factor evaluation was refreshed.
3. Current factor count in evaluation outputs.
4. Files generated.
5. Monthly IC availability.
6. Monthly LS availability.
7. Sharpe availability.
8. Drawdown availability.
9. Any schema gaps found.
10. Next PM recommendation.
11. Non-change statement: no factor formulas, no signal panel, no public pages.

## 8. Validation

Run py_compile:

```bash
python -m py_compile \
  scripts/build_factor_diagnostics_metrics.py \
  scripts/evaluate_factors.py \
  scripts/build_factor_library_state.py
```

Run the new builder:

```bash
python scripts/build_factor_diagnostics_metrics.py \
  --input-dir research/factor_runs/crypto_top50_factor_library/factor_level_evaluation \
  --state-path research/factor_runs/crypto_top50_factor_library/factor_library_state.json \
  --output-dir research/factor_runs/crypto_top50_factor_library/factor_diagnostics
```

Then inspect generated outputs:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
for name in ['factor_diagnostics_summary.csv','factor_monthly_ic_series.csv','factor_monthly_long_short_series.csv','factor_cumulative_long_short_curve.csv']:
    p = base / name
    print('\n', name, 'exists=', p.exists())
    if p.exists():
        df = pd.read_csv(p)
        print('rows=', len(df), 'cols=', list(df.columns))
        if 'factor_id' in df.columns:
            print('n_factors=', df['factor_id'].nunique())
PY
```

## 9. Allowed files to change

Allowed code:

- `scripts/build_factor_diagnostics_metrics.py`

Allowed generated diagnostics:

- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/*`

Allowed evaluation outputs:

- `research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/*` only if full canonical evaluation must be refreshed to include all 71 factors.

Allowed audit:

- `docs/factor_library/audits/pm13_factor_diagnostics_metrics_builder.md`

Do not edit public pages in this task.

## 10. Stop conditions

Stop and report if:

- factor library state is not 71/71/0 and the mismatch is unexplained;
- canonical factor evaluation refresh fails;
- existing evaluation artifacts do not contain enough schema to produce even monthly IC;
- monthly long-short cannot be computed and you cannot clearly document the schema gap;
- new builder would need to recompute factor IC directly from factor_values, which is out of scope for this task.

## 11. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: build factor diagnostics metrics layer
```

Final response should include:

- commit hash
- summary verdict
- whether factor evaluation was refreshed to 71 factors
- output files generated
- whether monthly IC is available
- whether monthly LS is available
- whether Sharpe/drawdown are available
- schema gaps and warnings
- next recommended PM
