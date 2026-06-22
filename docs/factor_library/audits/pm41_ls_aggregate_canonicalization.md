# PM-41: LS Aggregate Canonicalization for Factor-Level Evaluation

**Date:** 2026-06-22
**Verdict:** `PM41_LS_AGGREGATE_CANONICALIZED`
**Commit:** `dd40baf`

---

## Summary

LS aggregate statistics (std, annualized return, annualized vol, max drawdown, positive period rate) were missing from the page because no canonical pipeline computed them. The old diagnostics pipeline didn't have them for PM-35 factors, and the new `evaluate_factors.py` only output spread_mean/t_stat/win_rate. PM-41 fixes this at two layers.

## Why This Before Docs

The missing LS aggregates were a **real pipeline breakpoint**, not a documentation gap. The page showed `—` for LS Std / Ann Return / Ann Vol / Max DD for all PM-35 factors, which was misleading. Fixing the computation chain first, then documenting the lesson.

## LS Aggregate Computation Formula

All aggregates are computed from **monthly period LS returns** (from `factor_level_period_long_short_summary.csv`):

| Field | Formula | Annualization |
|-------|---------|---------------|
| `long_short_spread_std` | `std(monthly_ls_returns, ddof=1)` | N/A (monthly std) |
| `long_short_spread_annualized_return` | `mean(monthly_ls_returns) × 12` | Monthly × 12 |
| `long_short_spread_annualized_vol` | `std(monthly_ls_returns) × √12` | Monthly × √12 |
| `long_short_spread_max_drawdown` | `min((cumprod(1+r) - peak) / peak)` | N/A |
| `long_short_spread_positive_period_rate` | `count(r > 0) / count(r)` | N/A |
| `n_monthly_periods` | `len(monthly_ls_returns)` | N/A |
| `annualization_method` | `"monthly_x12"` | Fixed |

## Files Changed

### `scripts/evaluate_factors.py` — Canonical pipeline fix
- Collect monthly LS returns during period loop
- Compute aggregate stats after period loop (inside horizon loop)
- Add 7 new fields to `factor_level_long_short_summary.csv` output
- Add 7 new fields to merged rankic+LS summary output

### `scripts/_build_factor_eval_html.py` — Builder fallback
- Extended LS fallback to read new aggregate fields from canonical source
- `long_short_std`, `long_short_annualized_return`, `long_short_annualized_vol`, `long_short_max_drawdown` now populated from canonical LS summary

### `factor_level_long_short_summary.csv` — Data
- Merged PM-41 batch output (5 factors × 4 horizons = 20 rows) into canonical CSV
- 304 rows total (284 existing + 20 new)

### `factor-evaluation.html` — Rebuilt

---

## PM-35 Five-Factor QA

| Factor | Horizon | LS Std | Ann Return | Ann Vol | Max DD | Pos Rate |
|--------|---------|--------|------------|---------|--------|----------|
| rev_2h | 1h | 0.000310 | +0.094% | 0.107% | -0.059% | 56% |
| rev_2h | 4h | 0.000827 | -0.023% | 0.287% | -0.384% | 56% |
| mom_vol_adjusted_20h | 1h | 0.000242 | +0.133% | 0.084% | -0.036% | 76% |
| mom_vol_adjusted_20h | 4h | 0.000912 | +0.577% | 0.316% | -0.113% | 68% |
| range_breakout_vol_confirm_20h | 1h | 0.000827 | +0.148% | 0.287% | -0.333% | 48% |
| range_breakout_vol_confirm_20h | 4h | 0.002564 | +0.385% | 0.888% | -1.173% | 56% |
| volume_pressure_20h | 1h | 0.000182 | +0.092% | 0.063% | -0.048% | 60% |
| volume_pressure_20h | 4h | 0.000650 | +0.377% | 0.225% | -0.190% | 72% |
| xs_rank_mom_accel | 1h | 0.000226 | +0.060% | 0.078% | -0.095% | 44% |
| xs_rank_mom_accel | 4h | 0.000896 | +0.179% | 0.310% | -0.207% | 40% |

All 5 factors: LS Std ✓, Ann Return ✓, Ann Vol ✓, Max DD ✓, Pos Rate ✓, unavailable_reason=None ✓

---

## QA Results

- `check_factor_evaluation_page_completeness.py`: 23/23 PASS
- Public page: HTTP 200, JSON valid, factor_count=76
- No `ls_metrics_unavailable_reason` for PM-35 factors

---

## No Formula / Factor Values / Signal Changes

- No `factor_formula_registry.py` changes
- No `factor_ops.py` changes
- No `build_factor_values.py` changes
- No `expected_direction` changes
- No signal panel changes

---

## Remaining Limitations

1. **Paper portfolio regime decomposition** (bull_minus_bear, highvol_minus_lowvol) — no script computes these (PM-42)
2. **BTC correlation** (paper_return_btc_corr, ic_btc_return_corr) — no script computes these (PM-42)
3. **LS aggregate for old factors** — the canonical CSV merge only covered PM-35 factors. Old factors still use per-timestamp stats from old diagnostics. Full re-run of `evaluate_factors.py` would fix this but is expensive (~135s × 76 factors / 5 = ~35 min)

---

## Recommended Next PM

**PM-42: Paper regime decomposition and BTC correlation integration**
