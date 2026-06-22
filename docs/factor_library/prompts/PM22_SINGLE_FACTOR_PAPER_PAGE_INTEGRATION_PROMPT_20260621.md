# PM-22 Prompt — Integrate Single-Factor Paper Diagnostics into Factor Evaluation Page

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows PM-21:

- `docs/factor_library/audits/pm21_single_factor_paper_portfolio_diagnostics.md`
- `scripts/build_single_factor_paper_portfolio_diagnostics.py`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_summary.csv`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_monthly_returns.csv`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_fee_sensitivity.csv`
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_nav_curves.csv`

PM-21 generated useful single-factor paper diagnostics. The next step is to integrate compact, page-safe diagnostics into the existing factor-evaluation page.

Important: `single_factor_paper_nav_curves.csv` has millions of rows. Do **not** embed raw hourly NAV curves directly into HTML.

## 0. PM objective

1. Create a compact page payload for single-factor paper diagnostics.
2. Add missing standalone turnover output if not present.
3. Upgrade existing `factor-evaluation.html` with paper portfolio diagnostics.

Do **not** create a new page.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify `scripts/factor_formula_registry.py`.

Do **not** modify `scripts/factor_ops.py`.

Do **not** modify signal panel construction.

Do **not** rebuild signal panel.

Do **not** create a new public page.

Do **not** embed the full 6M+ row NAV CSV into HTML.

Do **not** use external CDN dependencies.

Do **not** make production/live/tradeability/alpha claims.

Do **not** call this a backtest strategy. Use terms like `paper diagnostic`, `single-factor diagnostic`, `research portfolio`.

## 2. Inputs

Use existing PM-21 outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_monthly_returns.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_fee_sensitivity.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_nav_curves.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_manifest.json
```

Use existing page inputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
scripts/_build_factor_eval_html.py
reports/site/factor-library/factor-evaluation.html
```

## 3. Required compact payload builder

Create:

```text
scripts/build_single_factor_paper_page_payload.py
```

This script should read PM-21 outputs and create compact page-safe files:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_page_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_turnover.csv
```

### 3.1 Page payload content

For each factor, include:

```text
factor_id
paper_viability_class
cost_sensitivity_class
gross_sharpe
gross_total_return
max_drawdown
positive_month_rate
avg_turnover
median_turnover
break_even_fee_bps
fee_0bps_total_return
fee_2bps_total_return
fee_5bps_total_return
fee_10bps_total_return
fee_20bps_total_return
monthly_nav_series_compact
fee_sensitivity_series
monthly_return_series
```

`monthly_nav_series_compact` should be monthly, not hourly.

Build it from `single_factor_paper_monthly_returns.csv` by compounding monthly returns by factor and fee_bps.

Only include fee_bps values needed for page charts:

```text
0, 5, 10, 20
```

Do not include all hourly rows.

### 3.2 Turnover output

If `single_factor_paper_turnover.csv` does not exist, create it.

A compact monthly turnover file is sufficient:

```text
factor_id
month
avg_turnover
median_turnover
max_turnover
n_observations
```

Use `single_factor_paper_nav_curves.csv` if needed, but read it in chunks if large.

## 4. Required page integration

Update existing page builder:

```text
scripts/_build_factor_eval_html.py
```

Regenerate:

```text
reports/site/factor-library/factor-evaluation.html
```

Do not create a new page.

### 4.1 Main table additions

Add columns or compact badges:

```text
Paper viability / 纸面组合
Cost sensitivity / 成本敏感性
10bps return / 10bps收益
Break-even fee / 盈亏平衡成本
Avg turnover / 平均换手
```

Preserve existing scorecard, redundancy, RankIC, Sharpe, drawdown, and metadata columns.

### 4.2 Detail panel additions

Add a section:

```text
Single-Factor Paper Portfolio / 单因子纸面组合
```

Show:

- paper_viability_class;
- cost_sensitivity_class;
- gross Sharpe;
- 0bps / 5bps / 10bps / 20bps total return;
- break-even fee bps;
- avg/median turnover;
- max drawdown;
- positive month rate;
- explanation that this is research diagnostic, not a strategy.

### 4.3 Charts

Use lightweight inline SVG or existing chart pattern. No external library.

Add at minimum:

1. **Paper NAV chart**
   - monthly NAV, fee 0bps vs 10bps;
   - optionally 20bps if compact.
2. **Fee sensitivity chart**
   - total return or Sharpe by fee_bps.
3. **Monthly return chart**
   - monthly returns under 0bps or 10bps.
4. **Turnover chart**
   - monthly avg turnover if available.

Do not embed raw hourly data.

## 5. Page copy / interpretation

Add clear caveats:

- This is a single-factor research portfolio diagnostic.
- It is not a production backtest.
- It does not include order book slippage, latency, borrow constraints, market impact, or execution constraints.
- 1h sequential horizon was used to avoid overlapping-return NAV distortion.
- High gross Sharpe but cost-collapsed net return means the factor is not robust to simple transaction cost assumptions.

## 6. Validation

Run:

```bash
python -m py_compile scripts/build_single_factor_paper_page_payload.py scripts/_build_factor_eval_html.py
python scripts/build_single_factor_paper_page_payload.py
python scripts/_build_factor_eval_html.py
```

Then:

```bash
python - <<'PY'
from pathlib import Path
import json
import pandas as pd
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
payload = json.loads((base / 'single_factor_paper_page_payload.json').read_text(encoding='utf-8'))
turn = pd.read_csv(base / 'single_factor_paper_turnover.csv')
html = Path('reports/site/factor-library/factor-evaluation.html').read_text(encoding='utf-8')
print('payload factors', len(payload.get('factors', [])) if isinstance(payload, dict) else 'unknown')
print('turnover factors', turn['factor_id'].nunique(), 'rows', len(turn))
checks = [
  'Single-Factor Paper Portfolio',
  '单因子纸面组合',
  'paper_viability_class',
  'cost_sensitivity_class',
  'break_even_fee_bps',
  'Cost sensitivity',
  '成本敏感性',
  'not a strategy',
  '不是交易策略',
]
for c in checks:
    print(c, c in html)
print('html size bytes', len(html.encode('utf-8')))
PY
```

Expected:

- payload covers 71 factors;
- turnover covers 71 factors unless documented;
- page contains paper diagnostics section;
- HTML remains reasonably sized, preferably < 3MB.

## 7. Required audit note

Create:

```text
docs/factor_library/audits/pm22_single_factor_paper_page_integration.md
```

Audit must include:

1. Summary verdict:
   - `SINGLE_FACTOR_PAPER_PAGE_INTEGRATION_PASS`
   - `SINGLE_FACTOR_PAPER_PAGE_INTEGRATION_PASS_WITH_LIMITATIONS`
   - `SINGLE_FACTOR_PAPER_PAGE_INTEGRATION_BLOCKED`
2. Files generated/changed.
3. Confirmation that no new public page was created.
4. Compact payload coverage.
5. Turnover file status.
6. Page features added.
7. HTML size before/after.
8. Validation results.
9. Limitations.
10. Non-change statement: no factors, formulas, factor_values, signal panel.
11. Recommended next PM.

## 8. Allowed files to change

Allowed scripts:

```text
scripts/build_single_factor_paper_page_payload.py
scripts/_build_factor_eval_html.py
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_page_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_turnover.csv
reports/site/factor-library/factor-evaluation.html
reports/site/factor-library/assets/factor_diagnostics_payload.json
```

Allowed audit:

```text
docs/factor_library/audits/pm22_single_factor_paper_page_integration.md
```

Do not modify PM-21 raw outputs unless a schema issue requires a small bug fix. Document any such change.

## 9. Stop conditions

Stop and report if:

- compact payload cannot be built without loading the entire hourly NAV file into memory;
- page size becomes too large;
- paper diagnostics cannot join 71/71 factors;
- adding charts breaks existing scorecard/redundancy sections;
- implementation would require changing factor_values or signal logic.

## 10. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: integrate single-factor paper diagnostics into factor page
```

Final response should include:

- commit hash
- summary verdict
- payload coverage
- turnover coverage
- page features added
- HTML size
- validation results
- limitations
- recommended next PM
