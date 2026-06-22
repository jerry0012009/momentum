# PM-21B Prompt — Reproducible Single-Factor Paper Portfolio Repair

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task is a repair PM for PM-21 / PM-22.

Do **not** continue to PM-25. First fix the paper portfolio data layer.

## 0. Why this repair is needed

PM-21 audit claimed `single_factor_paper_nav_curves.csv` had 6,281,415 rows, but that file is not present in GitHub. PM-22 then introduced `build_single_factor_paper_page_payload.py`, which reads `single_factor_paper_turnover.csv` as an input and writes to the same path as output. However PM-21 did not generate a reproducible standalone turnover file.

This means the current paper portfolio layer is partially dependent on local/stale artifacts and is not reproducible from a clean checkout.

PM-21B must fix this.

## 1. PM objective

Make single-factor paper portfolio diagnostics reproducible, compact, and suitable for page integration.

The data layer must provide:

1. factor-level paper summary;
2. monthly paper returns by fee;
3. monthly NAV and drawdown curves by fee;
4. long leg / short leg / long-short decomposition;
5. monthly turnover for all factors;
6. fee sensitivity;
7. manifest and audit.

Do not update public HTML in PM-21B. Page repair is PM-22B.

## 2. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** create a new public page.

Do **not** commit a 6M+ row hourly NAV CSV unless explicitly justified. Prefer compact monthly outputs.

Do **not** depend on local uncommitted files.

Do **not** hand-edit generated outputs.

Do **not** call this a production backtest or live strategy.

## 3. Scripts to inspect and repair

Inspect:

```text
scripts/build_single_factor_paper_portfolio_diagnostics.py
scripts/build_single_factor_paper_page_payload.py
scripts/_build_factor_eval_html.py
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_monthly_returns.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_fee_sensitivity.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_turnover.csv
```

PM-21B should primarily repair:

```text
scripts/build_single_factor_paper_portfolio_diagnostics.py
scripts/build_single_factor_paper_page_payload.py
```

Do not modify the HTML page in this PM unless absolutely required to keep existing page generation from breaking.

## 4. Required output files

Write to:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/
```

Required files:

```text
single_factor_paper_summary.csv
single_factor_paper_summary.json
single_factor_paper_monthly_returns.csv
single_factor_fee_sensitivity.csv
single_factor_paper_turnover.csv
single_factor_paper_leg_decomposition.csv
single_factor_paper_drawdown_curve.csv
single_factor_paper_page_payload.json
single_factor_paper_manifest.json
```

`single_factor_paper_nav_curves.csv` should be optional and should not be required for page rendering. If you generate it locally for debugging, do not commit it unless file size is acceptable and audit justifies it.

## 5. Required schema corrections

### 5.1 `single_factor_paper_turnover.csv`

This must be generated directly and reproducibly by `build_single_factor_paper_portfolio_diagnostics.py`.

It must cover **all factors**, not only one factor.

Required columns:

```text
factor_id
month
avg_turnover
median_turnover
max_turnover
n_observations
```

Expected approximate row count:

```text
number_of_factors × number_of_months
```

Do not hardcode 71. Read factor count dynamically.

### 5.2 `single_factor_paper_leg_decomposition.csv`

Required columns:

```text
factor_id
month
fee_bps
long_leg_return
short_leg_return
long_short_return
gross_long_short_return
net_long_short_return
```

Compute monthly values by compounding hourly returns within each month, not by naive summation.

### 5.3 `single_factor_paper_drawdown_curve.csv`

Required columns:

```text
factor_id
month
fee_bps
nav
drawdown
monthly_return
```

This should be monthly and compact.

### 5.4 `single_factor_paper_monthly_returns.csv`

Ensure monthly fee-adjusted return is computed by compounding hourly net returns within each month.

Avoid the current kind of approximation:

```text
monthly_gross_ret - monthly_turnover * fee_bps / 10000 * 24
```

That approximation is fragile and should be replaced with compounding of hourly net returns.

### 5.5 `single_factor_paper_page_payload.json`

Update `build_single_factor_paper_page_payload.py` so it reads the corrected compact monthly files, not a missing timestamp-level turnover file.

It should include per factor:

```text
monthly_nav_series_compact
fee_sensitivity_series
monthly_return_series
turnover_series
leg_decomposition_series
drawdown_series
```

Keep payload compact. Do not embed hourly rows.

## 6. Portfolio construction rules

Keep the PM-21 construction:

- 1h sequential horizon only;
- cross-sectional rank per timestamp;
- top 20% long equal-weight;
- bottom 20% short equal-weight;
- direction-adjusted factor value;
- equal-weight paper diagnostic;
- fees applied to turnover at bps assumptions 0, 2, 5, 10, 20.

But ensure calculations are reproducible and internally consistent.

Turnover should be documented as a simple set/weight-change proxy, not execution turnover.

## 7. Required audit

Create:

```text
docs/factor_library/audits/pm21b_reproducible_paper_portfolio_repair.md
```

Audit must include:

1. Summary verdict:
   - `PAPER_PORTFOLIO_REPAIR_PASS`
   - `PAPER_PORTFOLIO_REPAIR_PASS_WITH_LIMITATIONS`
   - `PAPER_PORTFOLIO_REPAIR_BLOCKED`
2. Explanation of what was wrong in PM-21/PM-22.
3. Files changed.
4. Factor coverage count, dynamically computed.
5. Month coverage count.
6. Output row counts for every paper diagnostic file.
7. Confirmation that `single_factor_paper_turnover.csv` covers all factors.
8. Confirmation that monthly fee returns compound hourly net returns.
9. Confirmation that page payload no longer depends on missing timestamp-level turnover file.
10. Top factors by 10bps return after recalculation.
11. Cost sensitivity distribution after recalculation.
12. Limitations.
13. Non-change statement: no factors, formulas, factor_values, signal panel, public page.
14. Recommended next PM: PM-22B page repair.

## 8. Validation

Run:

```bash
python -m py_compile scripts/build_single_factor_paper_portfolio_diagnostics.py scripts/build_single_factor_paper_page_payload.py
python scripts/build_single_factor_paper_portfolio_diagnostics.py
python scripts/build_single_factor_paper_page_payload.py
```

Then:

```bash
python - <<'PY'
import json
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
files = [
    'single_factor_paper_summary.csv',
    'single_factor_paper_monthly_returns.csv',
    'single_factor_fee_sensitivity.csv',
    'single_factor_paper_turnover.csv',
    'single_factor_paper_leg_decomposition.csv',
    'single_factor_paper_drawdown_curve.csv',
]
for f in files:
    df = pd.read_csv(base / f)
    print(f, 'rows=', len(df), 'factors=', df['factor_id'].nunique() if 'factor_id' in df.columns else None)
payload = json.loads((base / 'single_factor_paper_page_payload.json').read_text(encoding='utf-8'))
print('payload factors', len(payload.get('factors', [])))
PY
```

Expected:

- summary covers all registered factors;
- turnover covers all registered factors;
- leg decomposition covers all registered factors;
- drawdown curve covers all registered factors;
- payload covers all registered factors;
- no public page is changed.

## 9. Allowed files to change

Allowed scripts:

```text
scripts/build_single_factor_paper_portfolio_diagnostics.py
scripts/build_single_factor_paper_page_payload.py
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_summary.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_monthly_returns.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_fee_sensitivity.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_turnover.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_leg_decomposition.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_drawdown_curve.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_page_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_manifest.json
```

Allowed audit:

```text
docs/factor_library/audits/pm21b_reproducible_paper_portfolio_repair.md
```

Do not update factor-evaluation.html in PM-21B.

## 10. Stop conditions

Stop and report if:

- PM-21 outputs cannot be regenerated from committed scripts;
- factor_values or labels cannot be joined;
- compact outputs become too large;
- fixing this would require factor formula changes;
- page payload cannot be built without missing local artifacts.

## 11. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
fix: make paper portfolio diagnostics reproducible
```

Final response should include:

- commit hash
- summary verdict
- what was wrong
- files changed
- output coverage and row counts
- recalculated cost sensitivity distribution
- validation results
- limitations
- recommended next PM
