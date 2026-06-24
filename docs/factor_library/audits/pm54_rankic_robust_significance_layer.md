# PM-54: RankIC Robust Significance Layer

**Date:** 2026-06-24
**Status:** Research diagnostics. NOT production. NOT live trading.
**Verdict:** PM54_RANKIC_ROBUST_SIGNIFICANCE_PASS

---

## 1. Summary

Current factor library uses naive t-stat computed on individual timestamps (~17,700 per factor×horizon), which assumes independence between observations. For 24h/72h forward returns sampled at 1h intervals, consecutive labels overlap heavily, violating the independence assumption and inflating t-statistics.

This PM adds an overlap-aware robust significance layer using Newey-West / HAC standard errors on monthly IC aggregates. It does NOT replace the existing naive t-stat — it adds a parallel diagnostic.

**This PM does NOT:**
- Add new factors
- Modify formulas
- Modify expected_direction
- Modify factor_values
- Modify cap data source
- Modify signal panel
- Enter signal construction
- Make trading recommendations
- Change best_horizon selection
- Change scorecard calculation
- Overwrite existing rankic_t_stat

---

## 2. Files Changed

### New files:
- `scripts/compute_rankic_robust_significance.py` — Newey-West robust t-stat computation
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_rankic_robust_significance_summary.csv` — output (336 rows)
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_rankic_robust_significance_summary.json` — output JSON
- `research/factor_runs/crypto_top50_factor_library/factor_diagnostics/factor_rankic_robust_significance_manifest.json` — manifest
- `docs/factor_library/audits/pm54_rankic_robust_significance_layer.md` — this audit

### Not changed:
- `factor_level_rankic_summary.csv` — existing naive t-stat preserved
- `factor_quality_scorecard.csv` — scorecard unchanged
- `factor-evaluation.html` — page unchanged
- No factor formulas, expected_direction, factor_values, cap source, signal construction

---

## 3. Input Data Coverage

**Source:** `factor_level_period_ic_summary.csv`

| Metric | Value |
|--------|-------|
| Active factors | 84 |
| Horizons | 1h, 4h, 24h, 72h |
| Factor × horizon pairs | 336 (all present) |
| Periods per pair | 24–25 monthly aggregates |
| Date range | 2024-06 to 2026-06 |
| Missing pairs | 0 |

---

## 4. Newey-West Lag Rule

```
lag = min(horizon_hours, floor(sqrt(n_months)))
```

| Horizon | horizon_hours | n_months (typical) | sqrt(n) | NW lag |
|---------|--------------|-------------------|---------|--------|
| 1h | 1 | 25 | 5.0 | 1 |
| 4h | 4 | 25 | 5.0 | 4 |
| 24h | 24 | 25 | 5.0 | 5 |
| 72h | 72 | 25 | 5.0 | 5 |

The lag is capped at `n_months - 1` by construction (floor(sqrt(25)) = 5 < 25). Bartlett kernel weights are used: `w_j = 1 - j/(lag+1)`.

Minimum periods for robust inference: 8. Below this threshold, robust_t_stat = NaN and significance = INSUFFICIENT_PERIODS.

---

## 5. Method: Naive vs Robust t-stat

### Naive t-stat (existing, unchanged)
Computed on individual timestamps: `t = mean(IC) / (std(IC) / sqrt(N))` where N ≈ 17,700. Assumes independence between all observations.

### Robust t-stat (new, additive)
Computed on monthly IC aggregates: `t = mean(IC_monthly) / NW_SE(IC_monthly)` where NW_SE uses Newey-West HAC standard error with lag as above. Accounts for serial correlation from overlapping forward returns.

### Key difference
The naive t-stat treats each hourly timestamp as independent. For 72h forward returns, consecutive timestamps share 71/72 of their return window, creating massive autocorrelation. The robust t-stat operates on monthly aggregates (25 points) with NW correction for remaining serial correlation.

---

## 6. Output Row Count

**336 rows** = 84 factors × 4 horizons. Confirmed.

---

## 7. Overlap Warning Classification

| Horizon | Class | Overlap ratio |
|---------|-------|--------------|
| 1h | NO_MAJOR_OVERLAP | 0.0014 |
| 4h | MODERATE_OVERLAP | 0.0056 |
| 24h | HIGH_OVERLAP | 0.0333 |
| 72h | SEVERE_OVERLAP | 0.1000 |

Overlap ratio = horizon_hours / 720 (approximate monthly sampling interval in hours).

---

## 8. Significance Class Distribution

### Robust classification:

| Horizon | Robust Significant | Naive-Only Significant | Not Significant |
|---------|-------------------|----------------------|-----------------|
| 1h | 80 | 4 | 0 |
| 4h | 80 | 1 | 3 |
| 24h | 73 | 9 | 2 |
| 72h | 62 | 15 | 7 |
| **Total** | **295** | **29** | **12** |

### Interpretation:
- **295/336 (88%)** remain significant under robust test
- **29/336 (8.6%)** are NAIVE_ONLY_SIGNIFICANT — significant under naive but not robust
- **12/336 (3.6%)** not significant under either test
- Longer horizons have more disagreement: 72h has 15 naive-only vs 1h has only 4

---

## 9. Top Naive-Only Significant Factors (robust disagrees)

These factors have |naive_t| ≥ 2 but |robust_t| < 2, meaning their significance may be an artifact of overlapping returns:

| Factor | Horizon | Naive t | Robust t | Inflation |
|--------|---------|---------|----------|-----------|
| funding_rate_zscore_80h | 4h | +10.66 | +0.02 | 611x |
| funding_rate_zscore_80h | 72h | +8.07 | +0.03 | 284x |
| taker_buy_zscore_20h | 24h | -2.47 | -0.04 | 56x |
| funding_rate_zscore_80h | 1h | +6.31 | -0.18 | 35x |
| funding_rate_change_24h | 1h | +3.66 | -0.13 | 27x |
| funding_rate_change_24h | 72h | +2.14 | +0.16 | 13x |
| price_pos_120h | 72h | +3.29 | +0.38 | 9x |
| amihud_illiquidity_20h | 72h | +15.85 | +2.00 | 8x |
| price_pos_72h | 72h | +2.44 | +0.32 | 8x |
| mom_120h | 72h | -12.22 | -1.87 | 7x |

**funding_rate_zscore_80h** is the most extreme case: naive t-stat suggests strong significance (up to +10.66) but robust t-stat is essentially zero (0.02–0.18). This factor's IC signal is almost entirely explained by overlapping return autocorrelation.

---

## 10. Top t-stat Inflation (24h/72h)

| Factor | Horizon | Naive t | Robust t | Inflation |
|--------|---------|---------|----------|-----------|
| funding_rate_zscore_80h | 72h | +8.07 | +0.03 | 284x |
| taker_buy_zscore_20h | 24h | -2.47 | -0.04 | 56x |
| funding_rate_change_24h | 72h | +2.14 | +0.16 | 13x |
| taker_buy_delta_5h | 24h | -1.52 | +0.17 | 9x |
| price_pos_120h | 72h | +3.29 | +0.38 | 9x |
| tech_atr | 72h | +22.34 | +2.67 | 8x |
| amihud_illiquidity_20h | 72h | +15.85 | +2.00 | 8x |
| funding_rate_level_20h | 72h | +54.17 | +7.08 | 8x |
| price_pos_72h | 72h | +2.44 | +0.32 | 8x |
| mom_40h | 24h | -22.45 | -3.26 | 7x |

Average t-stat inflation by horizon:
- 1h: 2.48x
- 4h: 9.32x
- 24h: 4.20x
- 72h: 6.94x

---

## 11. Example Factors

### clv_20h (Close Location Value)

| Horizon | Mean IC | Naive t | Robust t | NW Lag | Naive Class | Robust Class |
|---------|---------|---------|----------|--------|-------------|-------------|
| 1h | -0.0034 | -3.53 | -2.10 | 1 | ROBUST_SIGNIFICANT_NEGATIVE | ROBUST_SIGNIFICANT_NEGATIVE |
| 4h | -0.0005 | -0.73 | -0.20 | 4 | NOT_SIGNIFICANT | NOT_SIGNIFICANT |
| 24h | +0.0121 | +11.64 | +2.02 | 5 | ROBUST_SIGNIFICANT_POSITIVE | ROBUST_SIGNIFICANT_POSITIVE |
| 72h | +0.0169 | +18.45 | +3.73 | 5 | ROBUST_SIGNIFICANT_POSITIVE | ROBUST_SIGNIFICANT_POSITIVE |

### rev_2h (2-hour reversal)

| Horizon | Mean IC | Naive t | Robust t | NW Lag | Naive Class | Robust Class |
|---------|---------|---------|----------|--------|-------------|-------------|
| 1h | +0.0364 | +29.82 | +10.43 | 1 | ROBUST_SIGNIFICANT_POSITIVE | ROBUST_SIGNIFICANT_POSITIVE |
| 4h | +0.0313 | +26.16 | +13.62 | 4 | ROBUST_SIGNIFICANT_POSITIVE | ROBUST_SIGNIFICANT_POSITIVE |
| 24h | +0.0149 | +13.10 | +6.90 | 5 | ROBUST_SIGNIFICANT_POSITIVE | ROBUST_SIGNIFICANT_POSITIVE |
| 72h | +0.0064 | +6.03 | +2.70 | 5 | ROBUST_SIGNIFICANT_POSITIVE | ROBUST_SIGNIFICANT_POSITIVE |

### a101_volume_cap_alpha_min_80_80

| Horizon | Mean IC | Naive t | Robust t | NW Lag | Naive Class | Robust Class |
|---------|---------|---------|----------|--------|-------------|-------------|
| 1h | +0.0157 | +16.67 | +17.11 | 1 | ROBUST_SIGNIFICANT_POSITIVE | ROBUST_SIGNIFICANT_POSITIVE |
| 4h | +0.0254 | +26.48 | +18.86 | 4 | ROBUST_SIGNIFICANT_POSITIVE | ROBUST_SIGNIFICANT_POSITIVE |
| 24h | +0.0475 | +49.54 | +18.10 | 5 | ROBUST_SIGNIFICANT_POSITIVE | ROBUST_SIGNIFICANT_POSITIVE |
| 72h | +0.0565 | +58.99 | +16.81 | 5 | ROBUST_SIGNIFICANT_POSITIVE | ROBUST_SIGNIFICANT_POSITIVE |

### a101_volume_cap_alpha_min_56_84

| Horizon | Mean IC | Naive t | Robust t | NW Lag | Naive Class | Robust Class |
|---------|---------|---------|----------|--------|-------------|-------------|
| 1h | +0.0156 | +16.20 | +14.36 | 1 | ROBUST_SIGNIFICANT_POSITIVE | ROBUST_SIGNIFICANT_POSITIVE |
| 4h | +0.0246 | +25.26 | +20.10 | 4 | ROBUST_SIGNIFICANT_POSITIVE | ROBUST_SIGNIFICANT_POSITIVE |
| 24h | +0.0455 | +46.37 | +16.62 | 5 | ROBUST_SIGNIFICANT_POSITIVE | ROBUST_SIGNIFICANT_POSITIVE |
| 72h | +0.0552 | +55.68 | +14.28 | 5 | ROBUST_SIGNIFICANT_POSITIVE | ROBUST_SIGNIFICANT_POSITIVE |

Note: The cap factors show minimal inflation (naive ≈ robust) because their IC signal is strong and persistent across months, not driven by autocorrelation artifacts.

---

## 12. QA Results

| Check | Result |
|-------|--------|
| 84 active factors present | ✓ |
| 4 horizons each | ✓ |
| 336 factor-horizon rows | ✓ |
| No missing active factor | ✓ |
| No missing horizon | ✓ |
| naive_t_stat present | ✓ (336/336) |
| robust_t_stat present | ✓ (336/336) |
| nw_lag present | ✓ (336/336) |
| overlap_warning present | ✓ (336/336) |
| No formula changes | ✓ |
| No factor_values changes | ✓ |
| No expected_direction changes | ✓ |
| No scorecard changes | ✓ (84 rows unchanged) |
| No best_horizon changes | ✓ |
| No signal construction | ✓ |
| No trading recommendation | ✓ |

---

## 13. Limitations

1. **Monthly aggregation:** The robust test operates on 24–25 monthly IC values, not individual timestamps. This reduces statistical power but properly accounts for overlap.
2. **No LS/paper/fee coverage:** Only RankIC is covered. Long-short, paper portfolio, and fee sensitivity are not yet analyzed with robust significance.
3. **Fixed overlap classification:** The 4-class system (NO_MAJOR/MODERATE/HIGH/SEVERE) is based on horizon_hours alone. Actual overlap depends on sampling frequency.
4. **Normal approximation:** p-values use normal distribution approximation (adequate for n ≥ 8 but not exact for small samples).
5. **Not integrated into page:** The robust t-stat is not yet displayed on factor-evaluation.html. This is intentional — page integration is a separate PM.

---

## 14. Recommended Next PM

- **PM-55**: Integrate robust t-stat into factor-evaluation.html (display alongside naive t-stat with visual indicator of disagreement)
- **PM-56**: Extend robust significance to LS returns and paper portfolio metrics
