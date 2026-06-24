# PM-58D: Residual Metric Semantics Cleanup

**Date:** 2026-06-24
**Verdict:** PM58D_RESIDUAL_METRIC_SEMANTICS_CLEANUP_PASS

## Summary

Cleaned up residual portfolio-style language from LS metric tooltips, benchmarks, and formulas.
No numerical changes — purely semantic cleanup.

## Problem Statement

After PM-58C, several metrics still contained portfolio-style benchmark bands, formulas, and
high/low descriptions that could mislead users into reading edge diagnostics as portfolio metrics.

## Files Changed

| File | Change |
|------|--------|
| `scripts/factor_metric_glossary.json` | Ann Vol: removed portfolio-vol benchmark bands, fixed high/low. Max DD: fixed formula to monthly_edge curve, removed portfolio drawdown benchmarks, fixed high/low. LS Win Rate: fixed formula to include numerator/denominator. LS Std: fixed high/low to edge terminology. |
| `scripts/_build_factor_eval_html.py` | Renamed "Window Diagnostics" → "Period-Level Window Diagnostics". Updated How to Read section. Added period-level disclaimers. |
| `scripts/build_ls_window_diagnostics.py` | Updated docstring to clarify period-level nature. |
| `research/.../factor_ls_window_diagnostics.json` | Updated description and added period_level_note. |
| `research/.../manifest.json` | Updated window diagnostics description. |
| `reports/.../factor-evaluation.html` | Rebuilt with all fixes. |

## Ann Vol Cleanup

**Before:**
- benchmark_zh: "经验参考（年化多空波动率）：<5%, 5%–15%, 15%–30%, 30%–50%, >50%"
- high_zh: "策略波动大"
- low_zh: "策略波动小"

**After:**
- benchmark_zh: "无固定阈值。该指标不是组合年化波动率，不能用传统策略波动率分档解释。"
- high_zh: "月度 edge 在月份之间波动更大，稳定性较弱"
- low_zh: "月度 edge 更平滑，但可能只是 edge 本身很弱"

## Max Drawdown Cleanup

**Before:**
- formula_zh/en: "max(peak - trough) / peak over cumulative return series"
- benchmark_zh: "经验参考（多空组合最大回撤）：<5%, 5%–10%, 10%–20%, 20%–30%, >30%"
- high_zh: "回撤大，风险高"
- low_zh: "回撤小，但低回撤+低收益=弱信号"

**After:**
- formula_zh/en: "edge_curve_m = cumprod(1 + monthly_edge_m); peak_m = running_max(edge_curve); drawdown_m = edge_curve_m / peak_m - 1; Edge Curve Max DD = min(drawdown_m)"
- benchmark_zh: "无固定阈值。该指标衡量月度 edge 曲线的下行稳定性，不是组合净值回撤。"
- high_zh: "Edge 曲线回撤大，月度 edge 下行波动较大"
- low_zh: "Edge 曲线回撤小，但低回撤+低 edge = 弱信号"

## LS Win Rate Formula Clarification

**Before:** "LS 收益为正的时段数 / 总有效时段数"

**After:**
```
Monthly Edge Win Rate = count(monthly_edge_m > 0) / count(valid months)
分子 = 月度 per-bar LS edge 为正的月份数
分母 = 有效月份数
```

## LS Std Cleanup

**Before:**
- high_zh: "策略波动大，风险高"
- low_zh: "策略波动小，但低波动+低收益=稳定弱信号"

**After:**
- high_zh: "月度 edge 离散度大，稳定性较弱"
- low_zh: "月度 edge 离散度小，但低离散度+低 edge = 弱信号"

## Window Diagnostics Renamed

- Section title: "Window Diagnostics" → "Period-Level Window Diagnostics 月度窗口诊断"
- Added disclaimer: "当前实现使用月度 period LS return，每个月视为一个 window 记录。这不是真正逐 K 线的投资窗口数据。"
- Script docstring and JSON metadata updated accordingly.

## Source Field Checks

All core edge metrics point to `factor_diagnostics/factor_diagnostics_summary.csv`. ✅
No core edge metrics point to `single_factor_paper_summary.csv`. ✅

## QA Results

Rebuilt HTML verified:
- ✅ No "策略波动大/小" in glossary
- ✅ No "多空组合年化波动率" in glossary
- ✅ No "多空组合最大回撤" in glossary
- ✅ No portfolio-vol benchmark bands (Ann Vol)
- ✅ No portfolio drawdown benchmark bands (Max DD)
- ✅ LS Win Rate formula includes numerator/denominator
- ✅ Period-Level Window Diagnostics section with disclaimers

## No Numerical Recomputation

No numeric values changed. Purely semantic/tooltips/benchmarks/formula text cleanup.

## No Unauthorized Changes

- ✅ No new factors
- ✅ No factor formula changes
- ✅ No expected_direction / factor_values changes
- ✅ No scorecard / best_horizon changes
- ✅ No signal construction
- ✅ No trading recommendations

## Remaining Limitations

1. Window diagnostics still use monthly period LS returns (not true per-bar).
2. Non-overlap subsampling is a monthly-step approximation.
3. Some metrics in the embedded JSON payload (e.g., Gross Return) have their own benchmark bands which are appropriate for those specific metrics.

## Recommended Next PM

**PM-59:** True per-bar investment-window diagnostics — compute from raw factor values for precise non-overlapping window stats.
