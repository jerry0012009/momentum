# PM-21 Prompt — Single-Factor Paper Portfolio Diagnostics

You are the server-side engineering AI working inside the `jerry0012009/momentum` repository.

This task follows the factor library evaluation stack through PM-19, and assumes PM-20 regeneration contract has been completed or is in progress.

Current factor evaluation already includes:

- factor values;
- factor-level RankIC / ICIR;
- monthly IC;
- long-short diagnostics;
- bilingual factor cards;
- factor quality scorecard;
- full pairwise redundancy matrix;
- redundancy-aware factor-evaluation page.

The next useful evidence layer is single-factor paper portfolio diagnostics. This answers:

> If this factor alone were used as a cross-sectional ranking signal, what would a simple long/short paper portfolio have looked like historically, before and after transaction costs?

This is still research diagnostics only. It is not a trading strategy and not a production/live system.

## 0. PM objective

Build a reproducible single-factor paper portfolio diagnostic layer for all 71 factors.

The output should support future page charts showing:

- single-factor gross NAV curve;
- net NAV curves under fee assumptions;
- long leg / short leg / long-short decomposition;
- monthly returns;
- turnover;
- fee sensitivity;
- break-even transaction cost estimate;
- portfolio extraction viability beyond RankIC and scorecard.

Do **not** update public HTML pages in PM-21. Page integration is a later PM.

## 1. Strict prohibitions

Do **not** add new factors.

Do **not** modify factor formulas.

Do **not** modify factor_values.

Do **not** modify `scripts/factor_formula_registry.py`.

Do **not** modify `scripts/factor_ops.py`.

Do **not** modify signal panel construction.

Do **not** rebuild signal panel.

Do **not** create or modify public HTML pages.

Do **not** make production/live/tradeability/alpha claims.

Do **not** call this a backtest strategy. Use terms like `paper diagnostic`, `single-factor diagnostic`, `research portfolio`.

## 2. Inputs

Use existing canonical data:

```text
research/factor_runs/crypto_top50_factor_library/factor_library_state.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_quality_scorecard.csv
data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/labels.parquet
data/features/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/<factor_id>/factor_values.parquet
```

Optional raw bars for liquidity/volume context if already available:

```text
data/cache/crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1/bars_1h.parquet
```

If raw bars are too heavy or unavailable, skip liquidity context and document it.

## 3. Required script

Create:

```text
scripts/build_single_factor_paper_portfolio_diagnostics.py
```

Recommended CLI:

```bash
python scripts/build_single_factor_paper_portfolio_diagnostics.py \
  --horizon 1h \
  --top-frac 0.20 \
  --bottom-frac 0.20 \
  --fee-bps-list 0,2,5,10,20 \
  --max-factors 0
```

Arguments:

```text
--horizon             default 1h. Use 1h sequential labels for NAV-like diagnostic.
--top-frac            default 0.20
--bottom-frac         default 0.20
--fee-bps-list        comma-separated fee assumptions
--max-factors         0 = all factors; positive number for smoke testing
--factor-ids          optional subset
--output-dir          default research/factor_runs/crypto_top50_factor_library/factor_diagnostics
```

Why default 1h:

- 4h/24h/72h labels are useful for forward-return diagnostics but create overlapping-return complications for a NAV curve.
- PM-21 should start with 1h sequential paper diagnostics.
- Later PMs can add non-overlapping multi-horizon variants.

## 4. Portfolio construction

For each factor at each timestamp:

1. Merge factor_value with 1h forward return label.
2. Drop missing factor/return rows.
3. Direction-adjust score using expected_direction:
   - positive: use factor_value;
   - negative: use `-factor_value`;
   - conditional: use raw factor_value and mark `direction_warning = CONDITIONAL_DIRECTION`.
4. Rank within timestamp.
5. Long top `top_frac` equal-weight.
6. Short bottom `bottom_frac` equal-weight.
7. Compute:
   - long_leg_return;
   - short_leg_return;
   - long_short_return;
   - gross_long_short_return before cost.
8. Compute turnover from changes in per-symbol weights across timestamps.
9. Apply transaction costs:
   - net_return_fee_bps = gross_return - turnover * fee_bps / 10000.
10. Compound NAV curves.

Keep dollar-neutral interpretation simple and explicit. This is diagnostic, not execution-ready.

## 5. Required outputs

Write to:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/
```

Required files:

```text
single_factor_paper_summary.csv
single_factor_paper_summary.json
single_factor_paper_nav_curves.csv
single_factor_paper_monthly_returns.csv
single_factor_paper_turnover.csv
single_factor_fee_sensitivity.csv
single_factor_paper_manifest.json
```

### 5.1 `single_factor_paper_summary.csv`

One row per factor.

Required columns:

```text
factor_id
family
final_quality_class
score_confidence
horizon
n_timestamps
avg_long_count
avg_short_count
gross_total_return
gross_annualized_return
gross_annualized_vol
gross_sharpe
max_drawdown
positive_month_rate
avg_turnover
median_turnover
fee_0bps_total_return
fee_2bps_total_return
fee_5bps_total_return
fee_10bps_total_return
fee_20bps_total_return
break_even_fee_bps
cost_sensitivity_class
paper_viability_class
main_diagnostic_note_zh
main_diagnostic_note_en
```

Suggested `cost_sensitivity_class`:

```text
ROBUST_TO_COSTS
MODERATELY_COST_SENSITIVE
COST_FRAGILE
COST_COLLAPSED
INSUFFICIENT_DATA
```

Suggested `paper_viability_class`:

```text
PAPER_STRONG
PAPER_PROMISING
PAPER_MIXED
PAPER_WEAK
PAPER_REVIEW_REQUIRED
```

### 5.2 `single_factor_paper_nav_curves.csv`

Rows by factor × timestamp × fee assumption.

Required columns:

```text
factor_id
timestamp
fee_bps
gross_return
net_return
nav
long_leg_return
short_leg_return
long_short_return
turnover
n_long
n_short
```

### 5.3 `single_factor_paper_monthly_returns.csv`

Rows by factor × month × fee assumption.

Required columns:

```text
factor_id
month
fee_bps
monthly_return
monthly_vol
monthly_turnover
positive_month
```

### 5.4 `single_factor_paper_turnover.csv`

Rows by factor × timestamp or factor × month. Choose a compact useful schema.

Required factor-level summary can be included in summary; detailed turnover file should support future charts.

### 5.5 `single_factor_fee_sensitivity.csv`

Rows by factor × fee_bps.

Required columns:

```text
factor_id
fee_bps
total_return
annualized_return
annualized_vol
sharpe
max_drawdown
positive_month_rate
avg_turnover
```

## 6. Performance and memory guidance

Avoid loading all factor_values into memory.

Process one factor at a time.

Persist each factor result to in-memory list only if size is manageable. If output becomes too large, stream append CSVs or reduce to monthly curves.

The NAV curves for 71 factors × timestamps × fee assumptions may become large. Keep it reasonable:

- Use one horizon only: 1h.
- Fee list limited to 0,2,5,10,20 bps.
- If output exceeds practical size, keep full NAV for top scorecard factors and summary for all; document this in audit.

Preferred first implementation: all factors, 1h horizon, hourly timestamps if manageable.

## 7. Required audit note

Create:

```text
docs/factor_library/audits/pm21_single_factor_paper_portfolio_diagnostics.md
```

Audit must include:

1. Summary verdict:
   - `SINGLE_FACTOR_PAPER_DIAGNOSTICS_PASS`
   - `SINGLE_FACTOR_PAPER_DIAGNOSTICS_PASS_WITH_LIMITATIONS`
   - `SINGLE_FACTOR_PAPER_DIAGNOSTICS_BLOCKED`
2. Files generated.
3. Factor coverage: expected 71 vs actual.
4. Horizon used and why.
5. Portfolio construction definition.
6. Fee assumptions.
7. Distribution of paper_viability_class.
8. Distribution of cost_sensitivity_class.
9. Top 10 factors by gross Sharpe.
10. Top 10 factors by fee-adjusted 10bps Sharpe or total return.
11. Factors that collapse after costs.
12. Limitations: overlapping returns avoided by 1h only; not execution-ready; no slippage order book; not live trading.
13. Non-change statement: no factors, formulas, factor_values, signal panel, public pages.
14. Recommended next PM.

## 8. Validation

Run:

```bash
python -m py_compile scripts/build_single_factor_paper_portfolio_diagnostics.py
python scripts/build_single_factor_paper_portfolio_diagnostics.py --max-factors 3
python scripts/build_single_factor_paper_portfolio_diagnostics.py
```

Then:

```bash
python - <<'PY'
import pandas as pd
from pathlib import Path
base = Path('research/factor_runs/crypto_top50_factor_library/factor_diagnostics')
summary = pd.read_csv(base / 'single_factor_paper_summary.csv')
fee = pd.read_csv(base / 'single_factor_fee_sensitivity.csv')
monthly = pd.read_csv(base / 'single_factor_paper_monthly_returns.csv')
print('summary rows', len(summary), 'factors', summary['factor_id'].nunique())
print('fee rows', len(fee), 'factors', fee['factor_id'].nunique(), 'fees', sorted(fee['fee_bps'].unique()))
print('monthly rows', len(monthly), 'factors', monthly['factor_id'].nunique())
print(summary['paper_viability_class'].value_counts(dropna=False))
print(summary['cost_sensitivity_class'].value_counts(dropna=False))
PY
```

Expected:

- summary rows = 71 if all factors processed;
- fee rows = 71 × number of fee assumptions;
- no missing factor IDs unless documented.

## 9. Allowed files to change

Allowed script:

```text
scripts/build_single_factor_paper_portfolio_diagnostics.py
```

Allowed outputs:

```text
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_summary.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_summary.json
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_nav_curves.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_monthly_returns.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_turnover.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_fee_sensitivity.csv
research/factor_runs/crypto_top50_factor_library/factor_diagnostics/single_factor_paper_manifest.json
```

Allowed audit:

```text
docs/factor_library/audits/pm21_single_factor_paper_portfolio_diagnostics.md
```

Do not update public HTML pages in PM-21.

## 10. Stop conditions

Stop and report if:

- labels cannot be joined to factor_values;
- portfolio construction would require modifying factor_values;
- outputs become too large to commit safely;
- cost model cannot be computed without pretending to have order book/slippage data;
- implementing this would require changing signal panel logic.

## 11. Commit rules

Before commit:

```bash
git diff --stat
git status --short
```

Commit with:

```bash
feat: add single-factor paper portfolio diagnostics
```

Final response should include:

- commit hash
- summary verdict
- factor coverage
- output sizes
- portfolio construction summary
- fee assumptions
- viability/cost sensitivity distributions
- top factors by gross and fee-adjusted diagnostics
- limitations
- recommended next PM
