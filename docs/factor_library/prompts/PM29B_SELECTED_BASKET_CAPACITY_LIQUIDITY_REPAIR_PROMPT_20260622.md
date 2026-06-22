# PM-29B Prompt — Selected-Basket Capacity / Liquidity Proxy Repair

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-29:

- `scripts/build_factor_capacity_liquidity_diagnostics.py`
- `docs/factor_library/audits/pm29_capacity_liquidity_proxy_diagnostics.md`
- capacity/liquidity outputs in `factor_diagnostics/`

PM-29 completed, but its audit states that it used a **universe volume proxy only** and did not reconstruct selected long/short baskets per factor. This made all 71 factors appear `CAPACITY_LIQUIDITY_OK`, which is likely too optimistic and not sufficiently useful for factor evaluation.

PM-29B should repair this by computing a selected-basket liquidity proxy where feasible.

Do **not** update public HTML in PM-29B.

## 0. PM objective

Improve capacity/liquidity diagnostics from universe-level proxy to **factor-specific selected-basket proxy**.

The goal is to estimate whether a factor's actual selected long/short basket tends to fall into thin or concentrated symbols.

This is still a proxy. It is not a real execution simulator.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** create or modify public HTML pages.

Do **not** enter signal evaluation.

Do **not** claim real tradable capacity.

Do **not** use external data.

Do **not** model order book depth, queue priority, impact curves, latency, borrow, or execution slippage.

## 2. Required code to inspect

Inspect and reuse conventions from:

```text
scripts/build_single_factor_paper_portfolio_diagnostics.py
scripts/build_factor_capacity_liquidity_diagnostics.py
scripts/factor_formula_registry.py
scripts/factor_specs.py
```

The selected basket construction should match the single-factor paper portfolio convention as closely as possible.

If the paper portfolio uses top/bottom quantile or decile selection, use the same or document the approximation.

## 3. Required script update

Modify:

```text
scripts/build_factor_capacity_liquidity_diagnostics.py
```

The script should attempt selected-basket reconstruction:

1. Load factor values for each factor.
2. Join with hourly bar volume / quote volume.
3. At each rebalance timestamp, rank the cross-section by factor value.
4. Select long and short baskets according to the same convention as paper diagnostics.
5. Compute liquidity for selected baskets, not just full universe.
6. Fall back to universe proxy only if selected basket reconstruction fails, and mark the fallback explicitly.

## 4. Required liquidity metrics

For each factor, compute:

```text
liquidity_proxy_method
selected_symbol_count_median
long_basket_volume_median
short_basket_volume_median
long_basket_volume_p10
short_basket_volume_p10
selected_basket_volume_median
selected_basket_volume_p10
long_top_symbol_volume_share_median
short_top_symbol_volume_share_median
selected_top_symbol_volume_share_median
low_volume_symbol_share
volume_concentration_class
```

Suggested `volume_concentration_class`:

```text
DIVERSIFIED_LIQUIDITY
MODERATE_CONCENTRATION
HIGH_CONCENTRATION
EXTREME_CONCENTRATION
INSUFFICIENT_DATA
```

## 5. Capacity metrics

Use selected basket volume as the denominator.

For assumed notionals:

```text
100000
1000000
10000000
```

Compute:

```text
estimated_trade_notional_per_rebalance = assumed_notional * avg_turnover
participation_rate_100k_selected_median
participation_rate_1m_selected_median
participation_rate_10m_selected_median
participation_rate_100k_selected_p10
participation_rate_1m_selected_p10
participation_rate_10m_selected_p10
capacity_at_1pct_participation_selected
capacity_at_5pct_participation_selected
capacity_at_10pct_participation_selected
```

Use conservative p10 selected-basket volume for capacity risk class.

## 6. Risk classes

Regenerate:

```text
capacity_risk_class
liquidity_risk_class
capacity_liquidity_class
factor_quality_cross_flag
```

Suggested classes:

```text
CAPACITY_FRIENDLY
MODERATE_CAPACITY_RISK
CAPACITY_FRAGILE
CAPACITY_BLOCKED_BY_TURNOVER
INSUFFICIENT_DATA
```

```text
LIQUIDITY_FRIENDLY
LOW_VOLUME_EXPOSURE
CONCENTRATED_LIQUIDITY
LIQUIDITY_FRAGILE
INSUFFICIENT_DATA
```

```text
CAPACITY_LIQUIDITY_OK
WATCH_TURNOVER
WATCH_LIQUIDITY
WATCH_BOTH
INSUFFICIENT_DATA
```

Cross flags:

```text
GOOD_ALPHA_BUT_CAPACITY_FRAGILE
STABLE_BUT_TOO_ILLIQUID
CHEAP_TO_TRADE_BUT_WEAK_SIGNAL
BALANCED_CANDIDATE
INSUFFICIENT_DATA
```

## 7. Performance constraints

Selected-basket reconstruction may be heavy.

Use efficient processing:

- process one factor at a time;
- downcast / select only needed columns;
- avoid loading unnecessary raw data repeatedly where possible;
- write monthly aggregates, not timestamp-level holdings.

If full hourly reconstruction for all 71 factors is too slow, use a deterministic sampling scheme, for example:

```text
sample every 4h or 8h
```

But the audit must clearly state the sampling method and coverage.

Do not silently fall back to universe proxy for all factors unless selected-basket reconstruction is genuinely blocked.

## 8. Required outputs to regenerate

Regenerate the PM-29 outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_summary.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_monthly.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_manifest.json
```

## 9. Dynamic coverage requirements

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
volume_concentration_class_distribution
```

## 10. Required audit

Create:

```text
docs/factor_library/audits/pm29b_selected_basket_capacity_liquidity_repair.md
```

Audit must include:

1. Summary verdict:
   - `SELECTED_BASKET_CAPACITY_REPAIR_PASS`
   - `SELECTED_BASKET_CAPACITY_REPAIR_PASS_WITH_LIMITATIONS`
   - `SELECTED_BASKET_CAPACITY_REPAIR_BLOCKED`
2. Why PM-29B was needed after PM-29.
3. Implementation method.
4. Whether selected-basket reconstruction succeeded.
5. If sampling was used, exact sampling method.
6. Files changed.
7. Factor coverage.
8. Liquidity proxy method distribution.
9. Capacity risk class distribution.
10. Liquidity risk class distribution.
11. Volume concentration distribution.
12. Combined class distribution.
13. Factors that changed risk class versus PM-29 if comparison is available.
14. Capacity-friendly examples.
15. Capacity-fragile or liquidity-fragile examples.
16. Good-alpha-but-capacity-fragile examples.
17. Payload size.
18. Validation results.
19. Limitations.
20. Non-change statement: no factors, formulas, factor_values, signal panel, public page.
21. Recommended next PM: PM-30 capacity/liquidity page integration.

## 11. Validation

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
print('volume concentration')
print(summary['volume_concentration_class'].value_counts(dropna=False).to_string())
print('combined')
print(summary['capacity_liquidity_class'].value_counts(dropna=False).to_string())
PY
```

Also run:

```bash
python scripts/check_factor_library_staleness.py
```

If PM-25 monitor does not yet know about capacity outputs, report that as future monitor extension; do not modify PM-25 here.

## 12. Allowed files to change

Allowed script:

```text
scripts/build_factor_capacity_liquidity_diagnostics.py
```

Allowed regenerated outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_summary.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_monthly.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_manifest.json
```

Allowed audit:

```text
docs/factor_library/audits/pm29b_selected_basket_capacity_liquidity_repair.md
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

## 13. Stop conditions

Stop and report if:

- factor_values cannot be loaded;
- bar volume data cannot be joined to selected symbols;
- selected basket reconstruction is not feasible even with deterministic sampling;
- outputs become too large;
- implementation would require modifying factor formulas, factor_values, or signal panel.

## 14. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
fix: use selected basket liquidity proxy for capacity diagnostics
```

Final response should include:

- commit hash
- summary verdict
- selected basket method
- sampling method if any
- factor coverage
- liquidity proxy method distribution
- capacity/liquidity/volume concentration distributions
- examples of changed risk interpretation
- validation results
- limitations
- recommended next PM
