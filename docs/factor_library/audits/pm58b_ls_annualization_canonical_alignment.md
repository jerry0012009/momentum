# PM-58B: LS Annualization Canonical Alignment

**Date:** 2026-06-24
**Verdict:** PM58B_LS_ANNUALIZATION_CANONICAL_ALIGNMENT_PASS

## Summary

Unified LS annualized return canonical definition across all pipeline scripts.
Changed from `mean × 12` to horizon-aware `per-bar LS mean × bars_per_year`.

## Root Cause

`evaluate_factors.py` (PM-41) used `_annualization_factor = 12` for LS annualized return,
assuming `long_short_spread_mean` was a monthly cumulative return. In reality, it's the
mean of per-bar LS returns within a month — a fundamentally different quantity.

This caused:
- Ann Return understated by ~12× for 1h factors (should be ×8760, was ×12)
- Ann Return understated by ~182× for 4h factors (should be ×2190, was ×12)
- Inconsistent with `build_factor_diagnostics_metrics.py` which was already fixed

## Files Changed

| File | Change |
|------|--------|
| `scripts/evaluate_factors.py` | `_annualization_factor=12` → `_BARS_PER_YEAR.get(hz)` + comments |
| `scripts/backfill_ls_monthly_aggregate_fields.py` | `mean*12` → `mean*bpy`, recompute ALL rows |
| `scripts/build_factor_diagnostics_metrics.py` | Already aligned (PM-58A fix) |
| `scripts/factor_metric_glossary.json` | Canonical tooltips with bars_per_year |
| `scripts/check_active_factor_workflow_consistency.py` | PM-58B annualization checks |
| `scripts/check_post_intake_workflow_integrity.py` | PM-58B formula verification |
| `scripts/check_factor_evaluation_page_completeness.py` | PM-58B HTML tooltip checks |
| `docs/factor_library/FACTOR_EVALUATION_WORKFLOW_BOUNDARY.md` | Added PM-58B canonical section |
| `docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md` | Updated annualization table |
| `docs/factor_library/START_HERE.md` | Updated annualization rule |
| `research/.../manifest.json` | Added pm58b_ls_annualization section |

## Old Formula

```python
_annualization_factor = 12  # monthly periods
_ls_ann_ret = _ls_mean_m * _annualization_factor
_ls_ann_vol = _ls_std_m * np.sqrt(_annualization_factor)
```

## New Canonical Formula

```python
_BARS_PER_YEAR = {"1h": 8760, "4h": 2190, "24h": 365, "72h": 365 / 3}
_bpy = _BARS_PER_YEAR.get(hz, 8760)
_ls_ann_ret = _ls_mean_m * _bpy          # per-bar LS mean × bars_per_year
_ls_ann_vol = _ls_std_m * np.sqrt(12)    # monthly edge stability (unchanged)
```

## bars_per_year Mapping

| Horizon | bars_per_year | Rationale |
|---------|--------------|-----------|
| 1h | 8,760 | 24 × 365 |
| 4h | 2,190 | 6 × 365 |
| 24h | 365 | 1 × 365 |
| 72h | 121.67 | 365 / 3 |

## Before/After Examples

| Factor | Horizon | LS Mean | Old Ann Ret | New Ann Ret | Paper Ann Ret |
|--------|---------|---------|-------------|-------------|---------------|
| mom_20h | 4h | 0.000565 | 0.0068 | **123.7%** | 122.3% |
| vol_ret_corr_20h | 24h | 0.00132 | 0.0158 | **48.2%** | 34.8% |
| volatility_20h | 72h | -0.00577 | -0.0693 | **-70.2%** | 41.8% |

## Canonical Evaluator Update

`evaluate_factors.py` L427-433: Replaced `_annualization_factor = 12` with
`_BARS_PER_YEAR.get(hz, 8760)`. Added clarifying comments that Sharpe/Vol are
monthly edge stability metrics, not portfolio metrics.

## Backfill Update

`backfill_ls_monthly_aggregate_fields.py`: Rewritten to:
- Accept `horizon` parameter in `compute_aggregates()`
- Use `bars_per_year` for ann ret
- Keep `√12` for vol
- Recompute ALL 336 rows (not just missing ones)
- All 336 rows successfully recomputed

## Diagnostics Builder Alignment

`build_factor_diagnostics_metrics.py` L258-271: Already aligned from previous fix.
Uses `_BARS_PER_YEAR` dict and `np.sqrt(12)` for vol.

## Glossary/Page Tooltip Update

- **Ann Return:** "年化 LS 边际收益 = 每根 K 线 long-short 收益均值 × 每年 K 线数。这不是组合累计年化收益，也不是交易信号。"
- **LS Sharpe:** "月度 LS 边际收益稳定性指标...不是组合 Sharpe。"
- **LS Std:** "月度 LS 边际收益标准差...不是组合波动率。"

## QA Results

| Script | Checks | Result |
|--------|--------|--------|
| `check_active_factor_workflow_consistency.py` | 17 tables | **PASS** |
| `check_post_intake_workflow_integrity.py` | 1764 (84×21) | **PASS** |
| `check_factor_evaluation_page_completeness.py` | 52 | **PASS** |

PM-58B specific checks:
- ✅ LS summary ann ret == monthly_mean × bars_per_year (336/336)
- ✅ Cross-validation LS summary vs diagnostics (79/79, tolerance 1e-4)
- ✅ Diagnostics ann ret == monthly_mean × bars_per_year (79/79)
- ✅ annualization_method == "per_bar_mean_x_bars_per_year"
- ✅ bars_per_year present in tooltip
- ✅ No affirmative "portfolio annual return" description
- ✅ LS Sharpe tooltip mentions monthly/月度

## No Unauthorized Changes

- ✅ No new factors added
- ✅ No factor formula changes
- ✅ No expected_direction changes
- ✅ No factor_values changes
- ✅ No cap data changes
- ✅ No RankIC changes
- ✅ No LS mean/t-stat/win-rate raw value changes
- ✅ No scorecard changes
- ✅ No best_horizon changes
- ✅ No signal construction introduced
- ✅ No trading recommendations added
- ✅ No paper simulation run
- ✅ No fee sensitivity run

## Remaining Limitations

1. **Cross-validation tolerance:** LS summary vs diagnostics differ by ~1e-5 due to
   floating point precision across computation paths. Tolerance set to 1e-4 (absolute).
2. **`long_short_spread_mean` field:** This field in the LS summary is per-bar mean,
   NOT monthly mean. The canonical ann ret formula uses monthly mean from the monthly
   series CSV. This semantic difference should be documented.
3. **Historical audit docs:** Old audit files (pm41, pm12, pm58a) retain original
   formulas as historical records — not updated.

## Recommended Next PM

**PM-59:** Factor Evaluation Page — Add explicit "monthly LS mean" column to
`factor_level_long_short_summary.csv` to eliminate semantic confusion between
per-bar mean and monthly mean.
