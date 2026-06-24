# PM-52: Horizon Transparency Layer / 多视野透明展示层

**Date:** 2026-06-24
**Verdict:** ✅ PASS — COMPLETE

---

## Summary

PM-52 adds horizon transparency to the Factor Evaluation Page. Users can now switch between 1h/4h/24h/72h horizons for each factor's metrics, charts, and summary data. A new All-Horizon Summary Table enables direct cross-horizon comparison. Horizon Pattern Classification labels identify whether a factor's signal is consistent across time horizons or horizon-specific.

**No formula, expected_direction, factor_values, signal, or trading recommendation changes.**

---

## Files Changed

| File | Change |
|------|--------|
| `scripts/_build_factor_eval_html.py` | +135 lines: horizon_metrics/IC/LS/Cum payload + horizon_pattern classification |
| `scripts/_build_factor_eval_html.py` | +27 lines CSS: horizon switch, summary table, pattern badges |
| `scripts/_build_factor_eval_html.py` | +158 lines JS: HORIZON_PATTERN_LABELS, buildHorizonSwitch, switchHorizon, buildMetricGrid, buildAllHorizonTable |
| `scripts/_build_factor_eval_html.py` | Template: horizon switch buttons, metric grid IDs, chart IDs, summary table, pattern badge, glossary |
| `reports/site/factor-library/factor-evaluation.html` | Rebuilt (6,056,178 bytes) |

---

## Data Source Inspection

| File | Rows | Factors | Horizons | Coverage |
|------|------|---------|----------|----------|
| `factor_level_evaluation/factor_level_rankic_summary.csv` | 312 | 78 | 4 (1h/4h/24h/72h) | ✅ 78/78 × 4/4 |
| `factor_level_evaluation/factor_level_long_short_summary.csv` | 312 | 78 | 4 | ✅ 78/78 × 4/4 |
| `factor_diagnostics/factor_monthly_ic_series.csv` | 7,776 | 78 | 4 | ✅ 78/78 × 4/4 |
| `factor_diagnostics/factor_monthly_long_short_series.csv` | 7,776 | 78 | 4 | ✅ 78/78 × 4/4 |
| `factor_diagnostics/factor_cumulative_long_short_curve.csv` | 7,776 | 78 | 4 | ✅ 78/78 × 4/4 |

**All 78 factors × 4 horizons = 312 combinations have complete data.**

---

## Horizon Metrics Coverage

- 78/78 factors have `horizon_metrics` with 4 horizon keys (1h, 4h, 24h, 72h)
- Each horizon contains 13 metric fields: rankic_mean, rankic_std, rankic_ir, rankic_t_stat, monthly_ic_positive_rate, long_short_mean, long_short_std, long_short_sharpe, long_short_annualized_return, long_short_annualized_vol, long_short_max_drawdown, long_short_positive_month_rate, coverage_rate

## Monthly IC Coverage

- 78/78 factors have `horizon_monthly_ic` with 4 horizon keys
- Each horizon has 25 monthly data points (2024-06 to 2026-06)

## Monthly LS Coverage

- 78/78 factors have `horizon_monthly_ls` with 4 horizon keys
- Each horizon has 25 monthly data points

## Cumulative LS Coverage

- 78/78 factors have `horizon_cumulative_ls` with 4 horizon keys
- Each horizon has 25 monthly data points

---

## Frontend Changes

### Horizon Switch Buttons
- 1h | 4h | 24h | 72h buttons in each factor's Evidence section
- Default: best_horizon is active with "Best" tag
- Clicking switches metric grid, IC chart, LS chart, and cumulative chart

### Metric Grid Switching
- `buildMetricGrid(hm)` dynamically renders metrics for selected horizon
- Title changes: "Best Horizon Metrics" vs "Horizon Metrics (Xh) — Alternative Horizon / 对照视野"

### All-Horizon Summary Table
- Shows all 4 horizons in a single table with: RankIC, t-stat, ICIR, IC Win%, LS Sharpe, Ann Ret, MaxDD, LS Win%, Coverage
- Best horizon row highlighted with ★ Best
- ⚠️ marks direction conflicts (RankIC vs expected_direction)
- ⚡ marks IC-LS tension (significant IC but weak LS)

### Chart Switching (P0)
- Monthly RankIC chart: switches by horizon
- Monthly LS chart: switches by horizon (P1)
- Cumulative LS chart: switches by horizon (P1)

### Horizon Pattern Classification
- 8 classification labels displayed as badges
- Distribution: HORIZON_CONSISTENT_NEGATIVE: 46, HORIZON_CONSISTENT_POSITIVE: 20, HORIZON_REVERSAL: 12

### Glossary Update
- "How to Read Horizons / 如何阅读不同视野" section added to How-to-Read
- Explains: best_horizon meaning, consistency, single-horizon spike, reversal, switch as diagnostic not trading tool

---

## Horizon Pattern Classification

| Pattern | Count | Description |
|---------|-------|-------------|
| HORIZON_CONSISTENT_NEGATIVE | 46 | All horizons negative, ≥2 significant |
| HORIZON_CONSISTENT_POSITIVE | 20 | All horizons positive, ≥2 significant |
| HORIZON_REVERSAL | 12 | Short vs long horizon direction conflict |
| SHORT_TERM_ONLY | 0 | Only 1h/4h significant |
| LONG_TERM_ONLY | 0 | Only 24h/72h significant |
| SINGLE_HORIZON_SPIKE | 0 | Only 1 significant horizon |
| MIXED_WEAK | 0 | Weak or mixed signals |
| INSUFFICIENT_HORIZON_DATA | 0 | No data |

---

## QA Results

| # | Check | Result |
|---|-------|--------|
| 1 | 78/78 factors have horizon_metrics | ✅ |
| 2 | Each factor has 1h/4h/24h/72h keys | ✅ |
| 3 | best_horizon in horizon_metrics | ✅ |
| 4 | All-Horizon Summary Table in page | ✅ |
| 5 | clv_20h defaults to 72h | ✅ |
| 6 | rev_2h defaults to 1h | ✅ |
| 7 | Horizon switch buttons exist | ✅ |
| 8 | Monthly IC chart supports horizon switching | ✅ |
| 9 | Page shows 78/78 factors | ✅ |
| 10 | Page size (5.8 MB) within threshold | ✅ |
| 11 | No signal construction | ✅ |
| 12 | No trading recommendation | ✅ |
| 13 | PM-49 interpretation visible | ✅ |
| 14 | Glossary tooltip visible | ✅ |

---

## Public Page Result

- URL: https://jp.jerrypsy.top/momentum/factor-library/factor-evaluation.html
- Status: ✅ Deployed and functional
- Size: 6,170,883 bytes (5.9 MB)

---

## Test Cases

### clv_20h (HORIZON_REVERSAL)
| Horizon | RankIC | t-stat | LS Sharpe | Note |
|---------|--------|--------|-----------|------|
| 1h | -0.00348 | -3.53 | -1.40 | ⚠️ direction conflict |
| 4h | -0.00074 | -0.73 | 0.93 | not significant |
| 24h | 0.01177 | 11.64 | 5.85 | strong positive |
| 72h | 0.01773 | 18.45 | 5.87 | ★ Best, strong positive |

### rev_2h (HORIZON_CONSISTENT_POSITIVE)
- Best horizon: 1h
- Pattern: HORIZON_CONSISTENT_POSITIVE
- All horizons show positive RankIC

---

## No Changes To

- ❌ Factor formulas
- ❌ expected_direction
- ❌ factor_values
- ❌ Signal construction
- ❌ Trading recommendations
- ❌ Existing evaluation results

---

## Remaining Limitations

1. Paper/Fee/Regime/Shape/Capacity sections do NOT switch by horizon (P2 — not implemented)
2. Horizon pattern classification uses simple rules; edge cases may need refinement
3. Cumulative LS chart re-renders on horizon switch (may flicker on slow devices)

---

## Recommended Next PM

- PM-53: Horizon-Aware Signal Design — use horizon transparency to inform signal horizon selection
- PM-54: Cross-Horizon Factor Screening — add horizon pattern filter to scoreboard
