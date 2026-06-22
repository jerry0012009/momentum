# PM-22: Single-Factor Paper Diagnostics Page Integration

## Summary
Integrated PM-21 single-factor paper portfolio diagnostics into the factor-evaluation.html page.

## What was done

### 1. Created `scripts/build_single_factor_paper_page_payload.py`
- Reads PM-21 summary (71 factors), monthly returns (8845 rows), fee sensitivity (355 rows)
- Builds compact JSON payload with per-factor:
  - `paper_viability_class`, `cost_sensitivity_class`, `gross_sharpe`, `gross_total_return`
  - `max_drawdown`, `positive_month_rate`, `avg_turnover`, `median_turnover`, `break_even_fee_bps`
  - `fee_0/5/10/20bps_total_return`
  - `monthly_nav_series_compact`: compounded NAV for fee_bps [0, 5, 10, 20]
  - `fee_sensitivity_series`: [{fee_bps, total_return, sharpe}]
  - `monthly_return_series`: [{month, monthly_return, fee_bps=10}]
- Writes `factor_diagnostics/single_factor_paper_page_payload.json` (422KB, 71 factors)
- Also creates `single_factor_paper_turnover.csv` (75 rows, monthly aggregated from timestamp-level data)

### 2. Updated `scripts/_build_factor_eval_html.py`
- Loads page payload JSON and merges paper fields into each factor
- Adds table columns: Paper Viability / Cost Sensitivity / 10bps Return / Break-even / Avg Turnover
- Adds paper viability filter dropdown
- Adds top summary section with paper viability and cost sensitivity class counts
- Adds detail panel section "Single-Factor Paper Portfolio / 单因子纸面组合" with:
  - All paper metrics in metric grid
  - Inline SVG chart: monthly NAV (0bps blue vs 10bps red)
  - Inline SVG chart: fee sensitivity bar chart
  - Inline SVG chart: monthly returns (10bps) bar chart
  - Diagnostic note (bilingual)
  - Caveat: "This is a research diagnostic, not a strategy / 这是研究诊断，不是交易策略"

### 3. Rebuilt HTML
- Output: `reports/site/factor-library/factor-evaluation.html` (1.4MB, under 3MB limit)

## Validation
- ✅ `py_compile` passes for both scripts
- ✅ Payload covers 71 factors
- ✅ All required keywords present in HTML
- ✅ HTML size 1.4MB < 3MB

## Files created/modified
- `scripts/build_single_factor_paper_page_payload.py` (new)
- `scripts/_build_factor_eval_html.py` (modified)
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_page_payload.json` (new)
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_turnover.csv` (new, monthly aggregated)
- `reports/site/factor-library/factor-evaluation.html` (rebuilt)
