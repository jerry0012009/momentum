# PM-24B Prompt — Refresh Regime Page after Paper Portfolio Repair

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows:

- PM-21B: repaired single-factor paper portfolio data layer
- PM-22B: repaired paper portfolio page integration
- PM-23B: refreshed BTC / market regime diagnostics using repaired PM-21B paper monthly returns

PM-23B regenerated regime outputs and found that 25 factors changed regime dependency class. The public `factor-evaluation.html` page must now be rebuilt so the regime section reflects PM-23B outputs.

Do **not** create a new public page.

## 0. PM objective

Refresh the existing factor-evaluation page so its BTC / market regime diagnostics section consumes PM-23B refreshed outputs.

Update:

```text
scripts/_build_factor_eval_html.py
reports/site/factor-library/factor-evaluation.html
```

Only modify the page builder if needed. If the builder already reads the refreshed files correctly, simply rebuild the page and audit the result.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify signal panel construction.

Do **not** recompute paper portfolio diagnostics.

Do **not** recompute regime diagnostics.

Do **not** create a new public page.

Do **not** use external CDN dependencies.

Do **not** remove PM-22B repaired paper portfolio charts.

Do **not** call regime diagnostics production/live/tradeable signals.

## 2. Inputs

Use current PM-23B refreshed regime outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_diagnostics_payload.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_exposure_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_class_distribution.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_regime_top_lists.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/market_regime_monthly_labels.csv
```

Also preserve PM-21B / PM-22B paper payload fields already integrated:

```text
turnover_series
leg_decomposition_series
drawdown_series
monthly_nav_series_compact
fee_sensitivity_series
monthly_return_series
```

## 3. Required page behavior

### 3.1 Top summary

Top regime summary must reflect PM-23B refreshed distribution:

```text
REGIME_ROBUST: 29
BULL_DEPENDENT: 11
VOL_DEPENDENT: 17
BEAR_DEPENDENT: 12
DRAWDOWN_FRAGILE: 2
```

Do not hardcode these values in source code. They must come from the regenerated PM-23B payload / CSV.

### 3.2 Main table

Main table regime fields should reflect PM-23B:

```text
Regime Dependency
BTC Beta
BTC Corr
Bull-Bear Δ
Drawdown Fragility
```

The filter dropdown should use PM-23B classes.

### 3.3 Detail panel

The BTC / Market Regime Diagnostics section should display refreshed per-factor values:

```text
regime_dependency_class
paper_return_btc_corr
paper_return_btc_beta
long_short_btc_corr
long_short_btc_beta
ic_btc_return_corr
bull_minus_bear_paper_return
highvol_minus_lowvol_paper_return
drawdown_minus_normal_paper_return
main_regime_note_zh
main_regime_note_en
regime_detail
```

### 3.4 Charts

Regime charts should use PM-23B refreshed data:

1. Paper return by BTC trend regime;
2. RankIC by BTC trend regime;
3. Paper return by volatility regime;
4. Paper return by drawdown regime.

Keep existing PM-22B paper charts:

1. corrected paper NAV;
2. drawdown curve;
3. long/short decomposition;
4. turnover curve;
5. fee sensitivity;
6. monthly return.

## 4. Rebuild command

Run:

```bash
python -m py_compile scripts/_build_factor_eval_html.py
python scripts/_build_factor_eval_html.py
```

Do not run PM-23B again unless the page builder proves the refreshed payload is missing.

## 5. Validation

Run:

```bash
python - <<'PY'
from pathlib import Path
html = Path('reports/site/factor-library/factor-evaluation.html').read_text(encoding='utf-8')
checks = [
    'BTC / Market Regime Diagnostics',
    'BTC / 市场状态诊断',
    'REGIME_ROBUST',
    'BULL_DEPENDENT',
    'BEAR_DEPENDENT',
    'VOL_DEPENDENT',
    'DRAWDOWN_FRAGILE',
    'Single-Factor Paper Portfolio',
    'leg_decomposition_series',
    'drawdown_series',
    'turnover_series',
    '不是交易策略',
]
for c in checks:
    print(c, c in html)
print('html size bytes', len(html.encode('utf-8')))
PY
```

Also verify the page embeds the refreshed PM-23B distribution. Do not rely only on keyword presence.

Expected:

- paper charts from PM-22B are still present;
- regime section reflects PM-23B refreshed payload;
- page size remains reasonable, preferably < 4MB;
- no new page created.

## 6. Required audit

Create:

```text
docs/factor_library/audits/pm24b_refresh_regime_page_after_paper_repair.md
```

Audit must include:

1. Summary verdict:
   - `REGIME_PAGE_REFRESH_AFTER_PAPER_REPAIR_PASS`
   - `REGIME_PAGE_REFRESH_AFTER_PAPER_REPAIR_PASS_WITH_LIMITATIONS`
   - `REGIME_PAGE_REFRESH_AFTER_PAPER_REPAIR_BLOCKED`
2. Files changed.
3. Confirmation no new public page was created.
4. Confirmation page consumes PM-23B refreshed regime payload.
5. Refreshed regime class distribution shown in page.
6. Confirmation paper charts from PM-22B remain present.
7. HTML size before/after.
8. Validation results.
9. Limitations.
10. Non-change statement: no factors, formulas, factor_values, signal panel.
11. Recommended next PM: PM-25 reusable staleness / workflow monitor.

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
docs/factor_library/audits/pm24b_refresh_regime_page_after_paper_repair.md
```

Do not change PM-23B regime outputs unless page integration proves the schema is broken. If schema is broken, stop and report.

## 8. Stop conditions

Stop and report if:

- refreshed PM-23B regime payload is missing;
- page cannot distinguish PM-23B refreshed values from stale PM-24 values;
- PM-22B paper charts would be broken;
- page size exceeds acceptable range;
- implementation requires recomputing factor_values, paper portfolio, regime diagnostics, or signal panel.

## 9. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
fix: refresh regime diagnostics on factor page after paper repair
```

Final response should include:

- commit hash
- summary verdict
- refreshed regime distribution shown in page
- confirmation PM-22B paper charts preserved
- HTML size
- validation results
- limitations
- recommended next PM
