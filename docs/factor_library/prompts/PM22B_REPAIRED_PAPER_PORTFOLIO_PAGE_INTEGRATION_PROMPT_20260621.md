# PM-22B Prompt — Repair Paper Portfolio Page Integration after PM-21B

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-21B:

- `docs/factor_library/audits/pm21b_reproducible_paper_portfolio_repair.md`
- `scripts/build_single_factor_paper_portfolio_diagnostics.py`
- `scripts/build_single_factor_paper_page_payload.py`
- `single_factor_paper_turnover.csv`
- `single_factor_paper_leg_decomposition.csv`
- `single_factor_paper_drawdown_curve.csv`
- repaired `single_factor_paper_page_payload.json`

PM-21B repaired the paper portfolio data layer, but did not update public HTML. PM-22B must update the existing factor-evaluation page to consume the repaired PM-21B payload.

Do **not** create a new page.

## 0. PM objective

Update:

```text
scripts/_build_factor_eval_html.py
reports/site/factor-library/factor-evaluation.html
```

so the existing factor-evaluation page displays the repaired single-factor paper diagnostics:

- long leg / short leg / long-short decomposition;
- turnover curve;
- drawdown curve;
- corrected NAV and monthly return series;
- fee sensitivity;
- cost-collapse warnings.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** create a new public page.

Do **not** use external CDN dependencies.

Do **not** embed hourly NAV rows.

Do **not** recompute paper portfolio metrics in the HTML builder.

Do **not** call the paper portfolio a production backtest or strategy.

## 2. Inputs

Use the repaired PM-21B compact payload:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_page_payload.json
```

The payload should include per factor:

```text
monthly_nav_series_compact
fee_sensitivity_series
monthly_return_series
turnover_series
leg_decomposition_series
drawdown_series
```

If any of these fields are missing for most factors, stop and report rather than silently falling back to old display.

## 3. Required page changes

### 3.1 Preserve existing page sections

The page must retain existing sections:

- factor metadata / formula / bilingual cards;
- scorecard;
- redundancy & novelty;
- original factor diagnostics charts;
- single-factor paper portfolio section;
- BTC / market regime diagnostics.

Do not regress PM-24 regime display.

### 3.2 Update paper portfolio section

In the detail panel section:

```text
Single-Factor Paper Portfolio / 单因子纸面组合
```

show metrics:

```text
paper_viability_class
cost_sensitivity_class
gross_sharpe
fee_0bps_total_return
fee_5bps_total_return
fee_10bps_total_return
fee_20bps_total_return
break_even_fee_bps
avg_turnover
median_turnover
max_drawdown
positive_month_rate
```

### 3.3 Required paper charts

Use existing inline SVG style. No external library.

Add or repair these charts:

1. **Corrected Paper NAV**
   - 0bps vs 10bps monthly NAV.
2. **Drawdown Curve**
   - monthly drawdown at 10bps.
3. **Long / Short Leg Decomposition**
   - monthly long_leg_return, short_leg_return, net_long_short_return at 10bps.
   - chart may be grouped bars or three compact lines/bars.
4. **Turnover Curve**
   - monthly avg_turnover.
5. **Fee Sensitivity**
   - total_return or Sharpe by fee_bps.
6. **Monthly Returns**
   - monthly_return at 10bps.

If chart space is too crowded, use compact stacked/paired bars, but do not drop drawdown or turnover.

### 3.4 Table columns

Ensure main table still has:

```text
Paper Viability
Cost Sensitivity
10bps Return
Break-even Fee
Avg Turnover
```

If useful, add:

```text
Max Drawdown
```

but avoid bloating the table excessively.

### 3.5 Caveats

Add clear copy:

- Research diagnostic only.
- Single-factor equal-weight long/short paper portfolio.
- No order-book slippage, market impact, latency, borrow/friction, or execution constraints.
- 1h sequential labels only.
- Turnover is a set/weight-change proxy, not exact executable turnover.

## 4. Regime consistency note

PM-23/PM-24 regime diagnostics were built before PM-21B paper recalculation. Do not silently recompute regime diagnostics in PM-22B.

Instead:

- keep current regime section visible;
- add an audit note that PM-23B should refresh regime diagnostics using repaired PM-21B paper monthly returns;
- do not modify PM-23 outputs in PM-22B.

## 5. Validation

Run:

```bash
python -m py_compile scripts/_build_factor_eval_html.py
python scripts/_build_factor_eval_html.py
```

Then:

```bash
python - <<'PY'
from pathlib import Path
html = Path('reports/site/factor-library/factor-evaluation.html').read_text(encoding='utf-8')
checks = [
    'Single-Factor Paper Portfolio',
    '单因子纸面组合',
    'leg_decomposition_series',
    'drawdown_series',
    'turnover_series',
    'Long / Short',
    'Drawdown',
    'Turnover',
    'Fee Sensitivity',
    'BTC / Market Regime Diagnostics',
    'BTC / 市场状态诊断',
    'research diagnostic',
    '不是交易策略',
]
for c in checks:
    print(c, c in html)
print('html size bytes', len(html.encode('utf-8')))
PY
```

Expected:

- existing paper section present;
- leg decomposition, turnover, and drawdown appear in HTML;
- BTC regime section still present;
- HTML size remains reasonable, preferably < 4MB.

## 6. Required audit

Create:

```text
docs/factor_library/audits/pm22b_repaired_paper_portfolio_page_integration.md
```

Audit must include:

1. Summary verdict:
   - `REPAIRED_PAPER_PAGE_INTEGRATION_PASS`
   - `REPAIRED_PAPER_PAGE_INTEGRATION_PASS_WITH_LIMITATIONS`
   - `REPAIRED_PAPER_PAGE_INTEGRATION_BLOCKED`
2. Files changed.
3. Confirmation no new public page was created.
4. Confirmation page consumes PM-21B payload fields.
5. Confirmation leg decomposition appears in page.
6. Confirmation turnover curve appears in page.
7. Confirmation drawdown curve appears in page.
8. Confirmation BTC regime section still appears.
9. HTML size before/after.
10. Validation results.
11. Limitations.
12. Non-change statement: no factors, formulas, factor_values, signal panel.
13. Recommended next PM: PM-23B regime refresh using repaired paper returns.

## 7. Allowed files to change

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
docs/factor_library/audits/pm22b_repaired_paper_portfolio_page_integration.md
```

Do not modify PM-21B paper diagnostic outputs in PM-22B unless there is a clear schema bug. If a schema bug exists, stop and report.

## 8. Stop conditions

Stop and report if:

- PM-21B payload is missing leg_decomposition_series, turnover_series, or drawdown_series for most factors;
- page size exceeds acceptable range;
- PM-24 regime section would be broken by the change;
- implementation would require recomputing factor_values, paper diagnostics, regime diagnostics, or signal panel.

## 9. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
fix: update factor page for repaired paper diagnostics
```

Final response should include:

- commit hash
- summary verdict
- page features added/repaired
- payload fields consumed
- HTML size
- validation results
- limitations
- recommended next PM
