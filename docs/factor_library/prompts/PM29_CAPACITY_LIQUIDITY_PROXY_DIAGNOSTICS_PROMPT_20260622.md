# PM-29 Prompt — Capacity / Liquidity Proxy Diagnostics

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows:

- PM-21B/22B: single-factor paper portfolio and page integration
- PM-23B/24B: BTC regime diagnostics and page integration
- PM-25: reusable staleness monitor + workflow reconciliation
- PM-26/27B/28: quantile shape, rolling stability, direction-aware decile diagnostics, and page integration

We are still in the **factor evaluation** phase. Do **not** enter signal evaluation.

## 0. PM objective

Add a reusable data-layer diagnostic module for **capacity and liquidity proxy risk**.

This is not a real execution simulator. It should provide factor-level evidence about whether a factor's implied turnover could be difficult to trade relative to available market volume.

The purpose is to help answer:

1. Is the factor's paper performance dependent on excessive turnover?
2. Are the selected long/short baskets concentrated in low-volume symbols?
3. What notional size would begin to imply high participation rates?
4. Which factors are capacity-fragile despite good IC / paper returns?
5. Which factors are liquidity-friendly candidates for later factor combination?

Do **not** update public HTML in PM-29. Page integration will be PM-30.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** create or modify public HTML pages.

Do **not** enter signal evaluation.

Do **not** claim real tradable capacity.

Do **not** model order books, queue position, latency, borrow, funding execution, or slippage beyond simple proxy metrics.

Do **not** fetch external data.

## 2. Required script

Create:

```text
scripts/build_factor_capacity_liquidity_diagnostics.py
```

Recommended CLI:

```bash
python scripts/build_factor_capacity_liquidity_diagnostics.py
```

Optional arguments:

```bash
--notionals 100000,1000000,10000000
--participation-thresholds 0.01,0.05,0.10
--output-dir research/factor_runs/crypto_top50_factor_library/factor_diagnostics
```

## 3. Required inputs

Use existing local canonical data only.

Preferred inputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_turnover.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_exposure_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_shape_stability_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_decile_shape_payload.json
```

For liquidity / volume data, use cached bars:

```text
data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet
```

If factor-level selected basket reconstruction is feasible from existing factor_values + labels, use it. If not feasible without large runtime, use turnover × universe-volume proxy and document the limitation.

Do not recompute factor_values.

## 4. Capacity proxy design

Use simple, transparent proxy metrics.

At minimum compute per factor:

```text
avg_turnover
median_turnover
p90_turnover
median_universe_hourly_quote_volume
p10_universe_hourly_quote_volume
median_selected_or_proxy_volume
p10_selected_or_proxy_volume
```

For each assumed notional, compute:

```text
assumed_notional
estimated_trade_notional_per_rebalance = assumed_notional * avg_turnover
participation_rate_median_volume
participation_rate_p10_volume
capacity_at_1pct_participation
capacity_at_5pct_participation
capacity_at_10pct_participation
```

Suggested capacity notional formula:

```text
capacity_at_x_pct = x_pct * reference_volume / max(turnover, epsilon)
```

Use p10 selected/proxy volume for conservative capacity estimates.

## 5. Liquidity / concentration diagnostics

If selected long/short basket reconstruction is possible, compute:

```text
long_basket_volume_median
short_basket_volume_median
long_basket_volume_p10
short_basket_volume_p10
long_top_symbol_volume_share
short_top_symbol_volume_share
selected_symbol_count_median
low_volume_symbol_share
```

If selected basket reconstruction is not feasible, compute a universe-level proxy and explicitly mark:

```text
liquidity_proxy_method = universe_volume_proxy
```

If selected basket reconstruction is feasible, mark:

```text
liquidity_proxy_method = selected_basket_proxy
```

## 6. Risk classes

Assign capacity / liquidity classes.

Suggested `capacity_risk_class`:

```text
CAPACITY_FRIENDLY
MODERATE_CAPACITY_RISK
CAPACITY_FRAGILE
CAPACITY_BLOCKED_BY_TURNOVER
INSUFFICIENT_DATA
```

Suggested `liquidity_risk_class`:

```text
LIQUIDITY_FRIENDLY
LOW_VOLUME_EXPOSURE
CONCENTRATED_LIQUIDITY
LIQUIDITY_FRAGILE
INSUFFICIENT_DATA
```

Suggested combined class:

```text
CAPACITY_LIQUIDITY_OK
WATCH_TURNOVER
WATCH_LIQUIDITY
WATCH_BOTH
INSUFFICIENT_DATA
```

## 7. Cross-check with existing factor evidence

Join existing metrics where available:

```text
paper_gross_sharpe
paper_net_return_10bps
cost_sensitivity_class
regime_dependency_class
quantile_shape_class
stability_class
decile_shape_class
```

Flag cases like:

```text
GOOD_ALPHA_BUT_CAPACITY_FRAGILE
STABLE_BUT_TOO_ILLIQUID
CHEAP_TO_TRADE_BUT_WEAK_SIGNAL
BALANCED_CANDIDATE
```

This is for factor evaluation only, not final signal selection.

## 8. Required outputs

Write to:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/
```

Required outputs:

```text
factor_capacity_liquidity_summary.csv
factor_capacity_liquidity_summary.json
factor_capacity_liquidity_monthly.csv
factor_capacity_liquidity_payload.json
factor_capacity_liquidity_manifest.json
```

Payload should be compact and suitable for PM-30 page integration.

## 9. Required schema

`factor_capacity_liquidity_summary.csv` should include:

```text
factor_id
liquidity_proxy_method
avg_turnover
median_turnover
p90_turnover
reference_volume_median
reference_volume_p10
capacity_at_1pct_participation
capacity_at_5pct_participation
capacity_at_10pct_participation
participation_rate_100k_median
participation_rate_1m_median
participation_rate_10m_median
participation_rate_100k_p10
participation_rate_1m_p10
participation_rate_10m_p10
capacity_risk_class
liquidity_risk_class
capacity_liquidity_class
factor_quality_cross_flag
main_capacity_note_zh
main_capacity_note_en
```

`factor_capacity_liquidity_monthly.csv` should include:

```text
factor_id
month
avg_turnover
median_turnover
reference_volume_median
reference_volume_p10
capacity_at_1pct_participation
capacity_at_5pct_participation
capacity_at_10pct_participation
capacity_risk_class
liquidity_risk_class
```

## 10. Dynamic coverage requirements

Use expected factor count from `factor_library_state.json` or registry. Do not hardcode 71.

Audit must report:

```text
expected_factor_count
summary_factor_count
monthly_factor_count
payload_factor_count
missing_factor_ids
liquidity_proxy_method_distribution
capacity_risk_distribution
liquidity_risk_distribution
capacity_liquidity_class_distribution
```

Do not silently drop factors.

## 11. Required audit

Create:

```text
docs/factor_library/audits/pm29_capacity_liquidity_proxy_diagnostics.md
```

Audit must include:

1. Summary verdict:
   - `CAPACITY_LIQUIDITY_PROXY_PASS`
   - `CAPACITY_LIQUIDITY_PROXY_PASS_WITH_LIMITATIONS`
   - `CAPACITY_LIQUIDITY_PROXY_BLOCKED`
2. Why PM-29 is needed before factor expansion and signal construction.
3. Files changed.
4. Input files used.
5. Liquidity proxy method used.
6. Factor coverage.
7. Capacity risk class distribution.
8. Liquidity risk class distribution.
9. Combined class distribution.
10. Examples of capacity-friendly factors.
11. Examples of capacity-fragile factors.
12. Examples of good-alpha-but-capacity-fragile factors.
13. Payload size.
14. Validation results.
15. Limitations.
16. Non-change statement: no factors, formulas, factor_values, signal panel, public page.
17. Recommended next PM: PM-30 capacity/liquidity page integration.

## 12. Validation

Run:

```bash
python -m py_compile scripts/build_factor_capacity_liquidity_diagnostics.py
python scripts/build_factor_capacity_liquidity_diagnostics.py
```

Then:

```bash
python - <<'PY'
import json
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
summary = pd.read_csv(base / 'factor_capacity_liquidity_summary.csv')
monthly = pd.read_csv(base / 'factor_capacity_liquidity_monthly.csv')
payload = json.loads((base / 'factor_capacity_liquidity_payload.json').read_text(encoding='utf-8'))
print('summary factors', summary['factor_id'].nunique())
print('monthly factors', monthly['factor_id'].nunique())
print('payload factors', len(payload.get('factors', [])))
print('liquidity proxy methods')
print(summary['liquidity_proxy_method'].value_counts(dropna=False).to_string())
print('capacity risk')
print(summary['capacity_risk_class'].value_counts(dropna=False).to_string())
print('liquidity risk')
print(summary['liquidity_risk_class'].value_counts(dropna=False).to_string())
print('combined')
print(summary['capacity_liquidity_class'].value_counts(dropna=False).to_string())
PY
```

Also run:

```bash
python scripts/check_factor_library_staleness.py
```

If PM-25 monitor does not yet know about capacity outputs, report that as a future monitor extension rather than modifying PM-25 here.

## 13. Allowed files to change

Allowed script:

```text
scripts/build_factor_capacity_liquidity_diagnostics.py
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_summary.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_monthly.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_manifest.json
```

Allowed audit:

```text
docs/factor_library/audits/pm29_capacity_liquidity_proxy_diagnostics.md
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

## 14. Stop conditions

Stop and report if:

- bars_1h.parquet is missing or does not contain usable volume fields;
- turnover data is missing;
- factor coverage cannot be reconciled;
- implementation would require factor formula/factor_values/signal changes;
- selected basket reconstruction is too expensive or unreliable;
- outputs become too large for repository use.

## 15. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: add capacity liquidity proxy diagnostics
```

Final response should include:

- commit hash
- summary verdict
- liquidity proxy method
- factor coverage
- capacity risk distribution
- liquidity risk distribution
- combined class distribution
- representative examples
- validation results
- limitations
- recommended next PM
