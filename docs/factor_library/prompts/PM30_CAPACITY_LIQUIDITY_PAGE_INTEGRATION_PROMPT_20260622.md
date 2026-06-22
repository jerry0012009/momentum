# PM-30 Prompt — Capacity / Liquidity Proxy Page Integration

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows:

- PM-29: universe-level capacity/liquidity proxy diagnostics
- PM-29B: selected-basket capacity/liquidity repair

PM-29B passed and generated selected-basket proxy outputs. PM-30 should integrate these diagnostics into the existing `factor-evaluation.html` page.

This is page integration only. Do **not** recompute capacity diagnostics in PM-30.

## 0. PM objective

Update the existing factor-evaluation page so each factor detail panel can show capacity/liquidity proxy evidence:

1. turnover vs selected-basket volume;
2. capacity at 1% / 5% / 10% participation;
3. participation rates for assumed notionals;
4. selected-basket volume and concentration metrics;
5. capacity/liquidity risk classes;
6. factor quality cross flags such as stable-but-too-illiquid or good-alpha-but-capacity-fragile;
7. explicit caveat that these are proxies, not execution estimates.

This strengthens factor evaluation before factor expansion or signal construction.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** recompute capacity/liquidity diagnostics.

Do **not** create a new public page.

Do **not** use external CDN dependencies.

Do **not** remove existing page sections.

Do **not** claim real tradable capacity.

Do **not** make production/live/trading claims.

## 2. Existing sections that must be preserved

Preserve all existing factor-evaluation page sections:

```text
Factor metadata / formula / bilingual cards
Factor Quality Scorecard
Redundancy & novelty
Single-Factor Paper Portfolio
Corrected paper NAV
Paper drawdown
Long / short leg decomposition
Turnover
Fee sensitivity
BTC / Market Regime Diagnostics
Quantile Shape & Rolling Stability
Direction-aware Decile Shape Diagnostics
```

Do not regress PM-21B through PM-29B outputs.

## 3. Required inputs

Use existing compact capacity/liquidity outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_monthly.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_capacity_liquidity_manifest.json
```

Do not embed excessive monthly rows if avoidable. Use compact payload first.

## 4. Required files to update

Update:

```text
scripts/_build_factor_eval_html.py
reports/site/factor-library/factor-evaluation.html
```

Optional if the build pattern requires it:

```text
reports/site/factor-library/assets/factor_diagnostics_payload.json
```

## 5. Required page section

Add a new section in the factor detail panel:

```text
Capacity / Liquidity Proxy Diagnostics
容量 / 流动性代理诊断
```

It should appear after paper/turnover diagnostics and before or near shape/regime diagnostics. Placement should preserve readability.

## 6. Required display elements

### 6.1 Summary badges

For the selected factor, show:

```text
liquidity_proxy_method
capacity_risk_class
liquidity_risk_class
capacity_liquidity_class
volume_concentration_class
factor_quality_cross_flag
```

Use cautious labels. Since PM-29B selected-basket proxy classified all factors as liquidity-fragile, do not present this as real execution impossibility.

Label this clearly as:

```text
Selected-basket proxy warning, not real execution capacity.
```

### 6.2 Metric grid

Show:

```text
avg_turnover
median_turnover
p90_turnover
selected_basket_volume_median
selected_basket_volume_p10
selected_symbol_count_median
long_basket_volume_median
short_basket_volume_median
low_volume_symbol_share
selected_top_symbol_volume_share_median
```

If some fields are missing, omit gracefully and report in audit.

### 6.3 Capacity estimates

Show:

```text
capacity_at_1pct_participation_selected
capacity_at_5pct_participation_selected
capacity_at_10pct_participation_selected
```

Show assumed-notional participation rates:

```text
participation_rate_100k_selected_median
participation_rate_1m_selected_median
participation_rate_10m_selected_median
participation_rate_100k_selected_p10
participation_rate_1m_selected_p10
participation_rate_10m_selected_p10
```

Use readable formatting: USD compact, percent, bps/ratio as appropriate.

### 6.4 Monthly capacity chart

If compact enough, show monthly trend for:

```text
capacity_at_5pct_participation
selected_basket_volume_median
avg_turnover
```

If monthly data would make the page too large, skip chart and show latest/summary values. Document choice in audit.

### 6.5 Interpretation notes

Show bilingual notes if available:

```text
main_capacity_note_zh
main_capacity_note_en
```

If not available, generate a concise rule-based note from class labels.

## 7. Top-level table / filters

If clean and low-risk, add optional table columns or filters for:

```text
capacity_risk_class
capacity_liquidity_class
factor_quality_cross_flag
```

Do not overcomplicate UI. Detail panel integration is more important.

## 8. Size and performance constraints

Current page is about 2.61MB after PM-28. Keep final page preferably under 4MB.

Do not embed unnecessarily large monthly capacity data. Use compact payload.

Avoid duplicate JSON blobs.

## 9. Required caveats on page

The section must clearly state:

```text
These are capacity/liquidity proxies based on selected-basket volume and turnover. They are not order-book simulation, slippage estimates, or real execution capacity.
```

Chinese equivalent:

```text
这些是基于选中篮子成交量与换手率的容量 / 流动性代理指标，不是订单簿模拟、滑点估计或真实可交易容量结论。
```

## 10. Validation

Run:

```bash
python -m py_compile scripts/_build_factor_eval_html.py
python scripts/_build_factor_eval_html.py
```

Then validate HTML:

```bash
python - <<'PY'
from pathlib import Path
html = Path('reports/site/factor-library/factor-evaluation.html').read_text(encoding='utf-8')
checks = [
    'Capacity / Liquidity Proxy Diagnostics',
    '容量 / 流动性代理诊断',
    'capacity_risk_class',
    'liquidity_risk_class',
    'capacity_liquidity_class',
    'factor_quality_cross_flag',
    'Selected-basket proxy warning',
    'not real execution capacity',
    'Single-Factor Paper Portfolio',
    'Quantile Shape & Rolling Stability',
    'BTC / Market Regime Diagnostics',
    '不是交易策略',
]
for c in checks:
    print(c, c in html)
print('html size bytes', len(html.encode('utf-8')))
PY
```

Also run:

```bash
python scripts/check_factor_library_staleness.py
```

If the staleness monitor does not yet include capacity outputs, report as a future monitor extension. Do not modify PM-25 here unless the fix is trivial and low-risk.

## 11. Required audit

Create:

```text
docs/factor_library/audits/pm30_capacity_liquidity_page_integration.md
```

Audit must include:

1. Summary verdict:
   - `CAPACITY_LIQUIDITY_PAGE_INTEGRATION_PASS`
   - `CAPACITY_LIQUIDITY_PAGE_INTEGRATION_PASS_WITH_LIMITATIONS`
   - `CAPACITY_LIQUIDITY_PAGE_INTEGRATION_BLOCKED`
2. Files changed.
3. Confirmation no new page was created.
4. Payloads consumed.
5. Confirmation selected-basket proxy metrics appear.
6. Confirmation caveat appears.
7. Confirmation existing paper charts preserved.
8. Confirmation shape/rolling/decile section preserved.
9. Confirmation BTC regime section preserved.
10. HTML size before/after.
11. Validation results.
12. Limitations.
13. Non-change statement: no factors, formulas, factor_values, signal panel.
14. Recommended next PM: PM-31 redundancy cluster / marginal information view.

## 12. Allowed files to change

Allowed script:

```text
scripts/_build_factor_eval_html.py
```

Allowed page output:

```text
reports/site/factor-library/factor-evaluation.html
reports/site/factor-library/assets/factor_diagnostics_payload.json
```

Allowed audit:

```text
docs/factor_library/audits/pm30_capacity_liquidity_page_integration.md
```

Do not modify:

```text
scripts/build_factor_capacity_liquidity_diagnostics.py
scripts/factor_formula_registry.py
scripts/factor_ops.py
scripts/build_factor_values.py
scripts/build_phase9b_signal_panel.py
```

## 13. Stop conditions

Stop and report if:

- PM-29B capacity payload is missing;
- selected-basket proxy fields are missing;
- HTML would exceed acceptable size;
- integration would require recomputing diagnostics;
- existing paper/regime/shape sections would break.

## 14. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: add capacity liquidity diagnostics to factor page
```

Final response should include:

- commit hash
- summary verdict
- sections added
- payloads consumed
- confirmation caveat appears
- confirmation existing sections preserved
- HTML size
- validation results
- limitations
- recommended next PM
