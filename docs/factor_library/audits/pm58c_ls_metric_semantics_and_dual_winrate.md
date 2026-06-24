# PM-58C: LS Edge vs Window Diagnostics — Semantics + Dual-Metric Clarification

**Date:** 2026-06-24
**Verdict:** PM58C_LS_METRIC_SEMANTICS_AND_DUAL_WINRATE_PASS

## Summary

Clarified the semantic distinction between **Edge Diagnostics** (monthly per-bar LS edge stability)
and **Window Diagnostics** (per-evaluation-window LS stats). Renamed all LS metrics on the page
to use "edge" terminology, added window diagnostics section, updated glossary/tooltips, and
ensured the workflow documentation guides future new factor intake through the correct pipeline.

## Problem Statement

The factor evaluation page mixed two different LS diagnostic perspectives without clear distinction:
1. **Edge diagnostics** — monthly per-bar LS edge stability (already computed)
2. **Window diagnostics** — per-horizon evaluation window LS stats (not previously computed)

This caused users to misread factor edge diagnostics as portfolio backtest results.

## Files Changed

| File | Change |
|------|--------|
| `scripts/factor_metric_glossary.json` | Renamed 7 entries: LS Mean→LS Edge Mean, LS Std→Monthly Edge Std, LS Sharpe→Monthly Edge Sharpe, Ann Return→Annualized LS Edge, Ann Vol→Monthly Edge Vol, Max Drawdown→Edge Curve Max DD, LS Win Rate→Monthly Edge Win Rate. Updated all tooltips with edge semantics, numerator/denominator, and "not portfolio" disclaimers. |
| `scripts/build_ls_window_diagnostics.py` | **NEW.** Reads period LS summary, computes per-factor-horizon window stats (mean, std, win_rate, ann_edge, ann_vol, sharpe) with overlap warnings and non-overlap subsampling. |
| `scripts/_build_factor_eval_html.py` | Loads window diagnostics CSV. Injects `window_diagnostics` dict into each factor. Updated display names to edge terminology. Added "Edge Diagnostics Summary" and "Window Diagnostics" sections to per-factor detail. Added PM-58C "How to Read" section with formulas. |
| `scripts/check_factor_evaluation_page_completeness.py` | Added PM-58C check (8 sub-checks): no portfolio semantics, edge/window sections exist, overlap mentioned. |
| `scripts/check_active_factor_workflow_consistency.py` | Added PM-58C window diagnostics validation (336 rows, win_rate∈[0,1], valid overlap_warning). |
| `scripts/check_post_intake_workflow_integrity.py` | Added PM-58C window diagnostics integrity check. |
| `docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md` | Added §11B: Window Diagnostics workflow step with command, fields, overlap warnings, and metric semantics. |
| `docs/factor_library/FACTOR_EVALUATION_WORKFLOW_BOUNDARY.md` | Added PM-58C metric semantics section. |
| `docs/factor_library/START_HERE.md` | Added PM-58C metric taxonomy summary. |
| `research/.../manifest.json` | Added pm58c_ls_metric_semantics section. |
| `research/.../factor_ls_window_diagnostics.csv` | **NEW.** 336 rows (84 factors × 4 horizons). |
| `research/.../factor_ls_window_diagnostics.json` | **NEW.** Metadata and overlap warnings. |

## Old Ambiguity

| Metric | Old Name | Problem |
|--------|----------|---------|
| LS Mean | "多空收益均值" | No edge/monthly distinction |
| LS Std | "多空收益标准差" | Could be read as portfolio vol |
| LS Sharpe | "多空夏普比率" | Read as portfolio Sharpe |
| Ann Return | "年化收益" | Read as portfolio annual return |
| Ann Vol | "年化波动率" | **Tooltip said "多空组合年化波动率"** — portfolio language |
| Max Drawdown | "最大回撤" | **Tooltip said "多空组合累计收益的最大回撤"** — portfolio language |
| LS Win Rate | "LS 胜率" | No numerator/denominator, no monthly vs window distinction |

## New Metric Taxonomy

### Edge Diagnostics (monthly per-bar LS edge stability)
| Display Name | Formula | Not |
|---|---|---|
| LS Edge Mean | mean(monthly_edge_m) | Not portfolio return |
| Monthly Edge Std | std(monthly_edge_m, ddof=1) | Not portfolio vol |
| Monthly Edge Sharpe | mean/std × √12 | Not portfolio Sharpe |
| Annualized LS Edge | mean × bars_per_year | Not portfolio annual return |
| Monthly Edge Vol | std × √12 | Not portfolio volatility |
| Edge Curve Max DD | max DD of cumprod(1+monthly_edge_m) | Not portfolio max DD |
| Monthly Edge Win Rate | count(edge>0) / count(valid months) | Not trade win rate |

### Window Diagnostics (per-evaluation-window LS stats)
| Display Name | Formula | Not |
|---|---|---|
| Window LS Mean | mean(window_LS_t) | Not portfolio return |
| Window LS Win Rate | count(window_LS>0) / count(windows) | Not independent trade win rate |
| Window LS Sharpe | mean/std × √(bpy) | Not portfolio Sharpe |
| Window LS Ann Vol | std × √(bpy) | Not portfolio vol |

## Monthly Edge Win Rate Formula

```
Numerator = count(monthly_edge_m > 0) across all valid months
Denominator = count(valid months)
monthly_edge_m = mean(per-bar LS returns within month m)
```

## Window LS Win Rate Formula

```
Numerator = count(window_LS_t > 0) across all valid evaluation windows
Denominator = count(valid evaluation windows)
window_LS_t = monthly period LS return (monthly aggregate of per-bar LS)
```

⚠️ For 24h/72h horizons sampled at 1h, windows overlap heavily. NOT independent trade win rate.

## Edge Curve Max DD Formula

```
edge_curve_m = cumulative_product(1 + monthly_edge_m)
peak_m = running_max(edge_curve_1, ..., edge_curve_m)
drawdown_m = edge_curve_m / peak_m - 1
Edge Curve Max DD = min(drawdown_m)
```

Peak = running maximum of cumulative monthly edge curve.
Trough = lowest point relative to prior running peak.
NOT portfolio max drawdown.

## Window Diagnostics Coverage

- 84 factors × 4 horizons = 336 rows
- All rows have window_ls_win_rate ∈ [0, 1]
- Overlap warnings: 1h=LOW, 4h=MODERATE, 24h=HIGH, 72h=VERY_HIGH
- Non-overlap subsampling available (monthly step approximation)

## Page Layout Changes

Per-factor detail now has two distinct sections:
1. **Edge Diagnostics Summary 边缘诊断概要** — Edge Curve Max DD, Monthly Edge Win Rate, Monthly Edge Sharpe
2. **Window Diagnostics 窗口诊断** — Window LS Mean, Window LS Win Rate, Window LS Sharpe, Window LS Ann Vol, n_windows, Overlap Level, Non-overlap Win Rate

"How to Read" section now includes PM-58C formulas and semantics explanation.

## Source Field Corrections

All 7 core edge metrics now point to `factor_diagnostics/factor_diagnostics_summary.csv` (was `single_factor_paper_summary.csv`).

## QA Results

| Script | Checks | Result |
|--------|--------|--------|
| `check_factor_evaluation_page_completeness.py` | 60 | ✅ PASS |
| `check_active_factor_workflow_consistency.py` | 18 | ✅ PASS |
| `check_post_intake_workflow_integrity.py` | All | ✅ PASS |

PM-58C specific:
- ✅ No affirmative "portfolio Sharpe/volatility/max drawdown" in page
- ✅ Edge Diagnostics Summary section exists
- ✅ Window Diagnostics section exists
- ✅ Monthly Edge Win Rate / LS Edge Mean present
- ✅ Overlap warning mentioned
- ✅ Window diagnostics 336 rows, win_rate valid, overlap valid

## No Unauthorized Changes

- ✅ No new factors
- ✅ No factor formula changes
- ✅ No expected_direction changes
- ✅ No factor_values changes
- ✅ No scorecard / best_horizon changes
- ✅ No signal construction
- ✅ No trading recommendations

## Workflow Entry Points (for future new factors)

1. `evaluate_factors.py` → produces `factor_level_period_long_short_summary.csv` (canonical)
2. `build_factor_diagnostics_metrics.py` → produces `factor_diagnostics_summary.csv` (edge diagnostics)
3. **`build_ls_window_diagnostics.py`** → produces `factor_ls_window_diagnostics.csv` (window diagnostics) ← NEW
4. `_build_factor_eval_html.py` → builds page with both edge + window sections
5. QA: `check_factor_evaluation_page_completeness.py` verifies PM-58C semantics

## Remaining Limitations

1. Window diagnostics use monthly period LS returns, not per-bar window returns. True per-window stats would need raw evaluation output.
2. Non-overlap subsampling is a monthly-step approximation. True non-overlapping requires per-bar data.
3. Window LS Win Rate for 24h/72h is NOT independent — overlap warning is displayed but users must interpret carefully.

## Recommended Next PM

**PM-59:** Per-bar window diagnostics — compute true per-evaluation-window LS returns from raw factor values for precise non-overlapping window stats and overlap-corrected win rates.
