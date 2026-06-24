# PM-56: Robust Return-Side Diagnostics Layer

**Date:** 2026-06-24
**Status:** Research diagnostics. NOT production. NOT live trading.
**Verdict:** PM56_ROBUST_RETURN_SIDE_DIAGNOSTICS_PASS_WITH_LIMITATIONS

---

## 1. Summary

PM-54/55 covered robust RankIC significance. PM-56 extends robust diagnostics to the return side: long-short monthly returns, paper portfolio returns, and fee-adjusted returns.

**This PM does NOT:**
- Add new factors
- Modify formulas / expected_direction / factor_values
- Modify RankIC results / scorecard / best_horizon
- Rebuild the page
- Enter signal construction
- Make trading recommendations

---

## 2. Files Changed

| File | Type |
|------|------|
| `scripts/compute_return_robust_significance.py` | New script |
| `.../factor_ls_robust_significance_summary.csv` | New (336 rows) |
| `.../factor_ls_robust_significance_summary.json` | New |
| `.../factor_paper_robust_significance_summary.csv` | New (5 rows) |
| `.../factor_paper_robust_significance_summary.json` | New |
| `.../factor_fee_robust_significance_summary.csv` | New (13 rows) |
| `.../factor_fee_robust_significance_summary.json` | New |
| `.../factor_return_robust_significance_manifest.json` | New |
| `docs/factor_library/audits/pm56_robust_return_side_diagnostics_layer.md` | New audit |

**Not changed:** scorecard, best_horizon, RankIC results, page, formulas, expected_direction, factor_values

---

## 3. Input File Map

| Input File | Description | Rows |
|------------|-------------|------|
| `factor_diagnostics/factor_monthly_long_short_series.csv` | Monthly LS returns per factor × horizon | 8,376 |
| `paper_portfolio_diagnostics/paper_portfolio_monthly_returns.csv` | Monthly paper returns (5 factors only) | 125 |
| `factor_diagnostics/single_factor_fee_sensitivity.csv` | Fee sensitivity (13 factors × 5 fee levels) | 65 |
| `factor_library_state.json` | Active factor list | 84 factors |

---

## 4. Coverage Table

| Diagnostic | Factors | Horizons | Rows | Coverage |
|------------|---------|----------|------|----------|
| LS robust | 84 | 4 (1h/4h/24h/72h) | 336 | Full active universe |
| Paper robust | 5 | 1 (1h only) | 5 | Subset — only 5 factors have paper diagnostics |
| Fee robust | 13 | N/A (factor-level) | 13 | Subset — only 13 factors have fee sensitivity data |

**Note:** Paper and fee coverages are limited by existing diagnostic outputs. Not all factors have paper portfolio or fee sensitivity data.

---

## 5. Output Row Counts

| Output | Rows | Expected |
|--------|------|----------|
| `factor_ls_robust_significance_summary.csv` | 336 | 84 × 4 = 336 ✓ |
| `factor_paper_robust_significance_summary.csv` | 5 | 5 factors × 1 horizon ✓ |
| `factor_fee_robust_significance_summary.csv` | 13 | 13 factors ✓ |
| `factor_return_robust_significance_manifest.json` | 1 | Manifest ✓ |

---

## 6. Newey-West Lag Rule

```
lag = min(horizon_hours, floor(sqrt(n_periods)))
```

| Horizon | horizon_hours | Typical n_months | lag |
|---------|---------------|------------------|-----|
| 1h | 1 | 25 | 1 |
| 4h | 4 | 25 | 4 |
| 24h | 24 | 25 | 5 |
| 72h | 72 | 25 | 5 |

---

## 7. Block Bootstrap Method

- **Block size:** `min(6, max(3, floor(sqrt(n_periods))))` → typically 5 for 25 months
- **n_bootstrap:** 2000
- **seed:** 42
- **Output:** 95% CI, bootstrap sign consistency
- **Rationale:** Block bootstrap preserves temporal autocorrelation structure within blocks

---

## 8. Classification Rules

| Class | Rule |
|-------|------|
| RETURN_ROBUST_POSITIVE | robust_t ≥ 2 and mean > 0 |
| RETURN_ROBUST_NEGATIVE | robust_t ≤ -2 and mean < 0 |
| NAIVE_ONLY_RETURN_SIGNIFICANT | \|naive_t\| ≥ 2 and \|robust_t\| < 2 |
| RETURN_COST_COLLAPSED | gross Sharpe ≥ 0.8 but net Sharpe < 0.5 |
| RETURN_NOT_SIGNIFICANT | otherwise |
| INSUFFICIENT_PERIODS | n < 4 |

---

## 9. Key Examples

### clv_20h

| Horizon | Mean Return | Naive t | Robust t | Class | Inflation | Bootstrap 95% CI |
|---------|-------------|---------|----------|-------|-----------|------------------|
| 1h | -0.000038 | -1.10 | -1.25 | NOT_SIGNIFICANT | 0.9x | |
| 4h | +0.000100 | +0.81 | +1.27 | NOT_SIGNIFICANT | 0.6x | |
| 24h | +0.001214 | +1.65 | +1.70 | NOT_SIGNIFICANT | 1.0x | |
| 72h | +0.002075 | +1.12 | +1.43 | NOT_SIGNIFICANT | 0.8x | |

**Insight:** clv_20h has robust RankIC significance (PM-54) but NO robust return-side significance. IC translates poorly to actual LS returns.

### rev_2h

| Horizon | Mean Return | Naive t | Robust t | Class | Inflation |
|---------|-------------|---------|----------|-------|-----------|
| 1h | +0.000079 | +1.27 | +1.30 | NOT_SIGNIFICANT | 1.0x |
| 4h | -0.000019 | -0.12 | -0.17 | NOT_SIGNIFICANT | 0.7x |
| 24h | -0.000773 | -2.19 | -2.38 | ROBUST_NEGATIVE | 0.9x |
| 72h | -0.002093 | -2.41 | -3.09 | ROBUST_NEGATIVE | 0.8x |

**Insight:** rev_2h LS returns are robust NEGATIVE at 24h/72h (short-term reversal → negative long-horizon LS). Return inflation ratios near 1.0 — no overlap issue for monthly LS returns.

### funding_rate_zscore_80h

| Horizon | Mean Return | Naive t | Robust t | Class | Inflation |
|---------|-------------|---------|----------|-------|-----------|
| 1h | +0.000181 | +0.94 | +0.96 | NOT_SIGNIFICANT | 1.0x |
| 4h | +0.000269 | +0.64 | +0.64 | NOT_SIGNIFICANT | 1.0x |
| 24h | +0.000118 | +0.19 | +0.19 | NOT_SIGNIFICANT | 1.0x |
| 72h | +0.002714 | +1.33 | +1.11 | NOT_SIGNIFICANT | 1.2x |

**Insight:** funding_rate_zscore_80h has extreme naive-only RankIC (PM-54/55) but return-side is NOT_SIGNIFICANT even naively. The RankIC significance doesn't translate to returns at all.

### a101_volume_cap_alpha_min_80_80

| Horizon | Mean Return | Naive t | Robust t | Class | Inflation |
|---------|-------------|---------|----------|-------|-----------|
| 1h | +0.000068 | +3.18 | +2.96 | ROBUST_POSITIVE | 1.1x |
| 4h | +0.000261 | +2.77 | +3.11 | ROBUST_POSITIVE | 0.9x |
| 24h | +0.001006 | +1.60 | +1.71 | NOT_SIGNIFICANT | 0.9x |
| 72h | +0.001734 | +0.97 | +1.08 | NOT_SIGNIFICANT | 0.9x |

### a101_volume_cap_alpha_min_56_84

| Horizon | Mean Return | Naive t | Robust t | Class | Inflation |
|---------|-------------|---------|----------|-------|-----------|
| 1h | +0.000091 | +3.89 | +3.74 | ROBUST_POSITIVE | 1.0x |
| 4h | +0.000346 | +3.70 | +4.21 | ROBUST_POSITIVE | 0.9x |
| 24h | +0.000995 | +1.85 | +2.22 | ROBUST_POSITIVE | 0.8x |
| 72h | +0.002251 | +1.69 | +2.39 | ROBUST_POSITIVE | 0.7x |

**Insight:** Cap factors show robust return-side significance, especially at 1h/4h. a101_volume_cap_alpha_min_56_84 is robust across ALL horizons.

---

## 10. Top Naive-Only Return Significant Factors

Only 3 total (much fewer than RankIC naive-only):

| Factor | Horizon | Naive t | Robust t | Inflation |
|--------|---------|---------|----------|-----------|
| funding_rate_level_20h | 24h | -2.43 | -1.94 | 1.2x |
| qvol_zscore_20h | 1h | +2.08 | +1.94 | 1.1x |
| vol_zscore_48h | 1h | +2.03 | +1.79 | 1.1x |

**Key difference from RankIC:** Monthly LS returns have much less overlap inflation (typically 0.7-1.2x) than RankIC computed on overlapping forward returns (1-600x). The naive vs robust disagreement is minimal for return-side metrics.

---

## 11. Cost-Collapsed Factors

5 factors have gross Sharpe ≥ 0.8 but net Sharpe < 0.5 (fee-adjusted collapse):

| Factor | Gross Sharpe | Net Sharpe | Sharpe Decay |
|--------|-------------|------------|-------------|
| range_breakout_vol_confirm_20h | 4.54 | -0.55 | 5.09 |
| mom_vol_adjusted_20h | 2.50 | -2.06 | 4.56 |
| up_down_vol_ratio_20h | 2.00 | -2.33 | 4.32 |
| volume_pressure_20h | 1.77 | -2.07 | 3.84 |
| rev_2h | 1.22 | -1.93 | 3.14 |

**These factors are NOT tradable** after realistic transaction costs (20 bps round-trip).

---

## 12. Factors with Robust RankIC but Weak Return Translation

| Factor | Best RankIC Robust t | Best LS Robust t | Gap |
|--------|---------------------|------------------|-----|
| funding_rate_zscore_80h | +2.55 (24h) | +0.96 (1h) | IC significant, returns not |
| clv_20h | +3.73 (72h) | +1.70 (24h) | IC significant, returns marginal |
| many others | varies | NOT_SIGNIFICANT | Common pattern |

---

## 13. QA Results

| Check | Result |
|-------|--------|
| LS: 84 factors × 4 horizons = 336 rows | ✓ |
| Paper: 5 factors × 1 horizon = 5 rows | ✓ (documented subset) |
| Fee: 13 factors = 13 rows | ✓ (documented subset) |
| No missing active factors in LS | ✓ |
| Active workflow consistency | 13/13 PASS |
| Page QA | 33/33 PASS |
| No formula changes | ✓ |
| No scorecard changes | ✓ |
| No best_horizon changes | ✓ |
| No page rebuild | ✓ |
| No signal construction | ✓ |

---

## 14. Remaining Limitations

1. **Paper coverage:** Only 5/84 factors have paper portfolio diagnostics. Expanding paper diagnostics to all 84 factors would require running paper simulation for each.
2. **Fee coverage:** Only 13/84 factors have fee sensitivity data. Fee sensitivity is computed during single-factor deep-dive, not for all factors.
3. **Fee analysis is not time-series:** Fee sensitivity compares gross vs net at a single point, not a monthly series. NW/bootstrap not applicable.
4. **Return-side inflation is low:** Monthly LS returns have minimal overlap (inflation 0.7-1.2x), unlike RankIC (1-600x). The robust correction matters less for returns than for IC.
5. **Not integrated into page:** Return-side robust diagnostics are standalone CSV/JSON outputs, not yet in factor-evaluation.html.

---

## 15. Recommended Next PM

- **PM-57**: Integrate return-side robust diagnostics into factor-evaluation.html page
- **PM-58**: Expand paper portfolio diagnostics to all 84 factors
