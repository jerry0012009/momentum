# PM-55: Robust Significance Page Integration

**Date:** 2026-06-24
**Status:** Research diagnostics. NOT production. NOT live trading.
**Verdict:** PM55_ROBUST_SIGNIFICANCE_PAGE_INTEGRATION_PASS

---

## 1. Summary

PM-54 computed Newey-West robust t-statistics for all 84 factors × 4 horizons (336 rows) and saved them to `factor_rankic_robust_significance_summary.csv/json`. PM-55 integrates these diagnostics into the factor-evaluation.html page so users can see naive vs robust t-stat side by side.

**This PM does NOT:**
- Add new factors
- Modify formulas
- Modify expected_direction
- Modify factor_values
- Modify cap data source
- Modify scorecard calculation
- Modify best_horizon selection
- Enter signal construction
- Make trading recommendations
- Overwrite existing rankic_t_stat

---

## 2. Files Changed

### Modified:
- `scripts/_build_factor_eval_html.py` — load robust CSV, add robust_rankic to payload, add robust fields to horizon_metrics, add CSS badges, add JS rendering
- `scripts/check_factor_evaluation_page_completeness.py` — add PM-55 QA checks (5 new checks)
- `reports/site/factor-library/factor-evaluation.html` — rebuilt with robust data

### Not changed:
- `factor_level_rankic_summary.csv` — existing naive t-stat preserved
- `factor_quality_scorecard.csv` — scorecard unchanged
- `compute_rankic_robust_significance.py` — not modified (PM-54)
- No factor formulas, expected_direction, factor_values, cap source, signal construction

---

## 3. Robust Payload Coverage

| Metric | Value |
|--------|-------|
| Factors with robust_rankic | 84/84 |
| Horizons per factor | 4/4 (1h, 4h, 24h, 72h) |
| Total robust entries | 336 |
| Missing entries | 0 |

Each `robust_rankic[horizon]` contains:
- `naive_t_stat`, `robust_t_stat`, `newey_west_se`, `nw_lag`, `n_months`
- `effective_n_proxy`, `tstat_inflation_ratio`
- `significance_class_naive`, `significance_class_robust`, `overlap_warning`

---

## 4. Page UI Changes

### Best Horizon Metrics
- **"IC t-stat"** renamed to **"Naive t-stat"** (value unchanged)
- **"Robust t-stat"** added with:
  - Numeric value
  - Robust class badge (color-coded: green=robust significant, amber=naive-only, gray=not significant)
  - Overlap warning badge (green/amber/red by severity)
  - Inflation ratio badge (>2x amber, >3x red)

### All-Horizon Summary Table
New columns added:
- **Naive t** — existing rankic_t_stat
- **Robust t** — Newey-West robust t-stat
- **Robust Class** — badge showing significance class
- **Inflation** — t-stat inflation ratio badge
- **Overlap** — overlap warning badge

### How to Read Section
New "Robust Significance" section with bilingual (EN/CN) explanation:
- What robust t-stat is and isn't
- Key terms glossary (Naive t-stat, Robust t-stat, Inflation ratio, Overlap warning, Significance classes)
- Explicit disclaimer: does NOT change best_horizon, scorecard, or tradability

### CSS Badges
- `.robust-badge` — color by significance class
- `.overlap-badge` — color by overlap severity
- `.inflation-badge` — color by inflation level

---

## 5. Key Examples

### clv_20h (Close Location Value)

| Horizon | Naive t | Robust t | Class | Inflation | Overlap |
|---------|---------|----------|-------|-----------|---------|
| 1h | -3.53 | -2.10 | ROBUST_SIGNIFICANT_NEGATIVE | ×1.5 | NO_MAJOR_OVERLAP |
| 4h | -0.73 | -0.20 | NOT_SIGNIFICANT | ×3.6 | MODERATE_OVERLAP |
| 24h | +11.64 | +2.02 | ROBUST_SIGNIFICANT_POSITIVE | ×5.8 | HIGH_OVERLAP |
| 72h | +18.45 | +3.73 | ROBUST_SIGNIFICANT_POSITIVE | ×4.9 | SEVERE_OVERLAP |

### rev_2h (2-hour reversal)

| Horizon | Naive t | Robust t | Class | Inflation | Overlap |
|---------|---------|----------|-------|-----------|---------|
| 1h | +29.82 | +10.43 | ROBUST_SIGNIFICANT_POSITIVE | ×2.9 | NO_MAJOR_OVERLAP |
| 4h | +26.16 | +13.62 | ROBUST_SIGNIFICANT_POSITIVE | ×1.9 | MODERATE_OVERLAP |
| 24h | +13.10 | +6.90 | ROBUST_SIGNIFICANT_POSITIVE | ×1.9 | HIGH_OVERLAP |
| 72h | +6.03 | +2.70 | ROBUST_SIGNIFICANT_POSITIVE | ×2.2 | SEVERE_OVERLAP |

### funding_rate_zscore_80h (extreme naive-only example)

| Horizon | Naive t | Robust t | Class | Inflation | Overlap |
|---------|---------|----------|-------|-----------|---------|
| 1h | +6.31 | -0.18 | NAIVE_ONLY_SIGNIFICANT | ×34.9 | NO_MAJOR_OVERLAP |
| 4h | +10.66 | +0.02 | NAIVE_ONLY_SIGNIFICANT | ×611.2 | MODERATE_OVERLAP |
| 24h | — | — | (not checked) | — | HIGH_OVERLAP |
| 72h | +8.07 | +0.03 | NAIVE_ONLY_SIGNIFICANT | ×283.5 | SEVERE_OVERLAP |

### a101_volume_cap_alpha_min_80_80 (robust cap factor)

| Horizon | Naive t | Robust t | Class | Inflation | Overlap |
|---------|---------|----------|-------|-----------|---------|
| 1h | +16.67 | +17.11 | ROBUST_SIGNIFICANT_POSITIVE | ×1.0 | NO_MAJOR_OVERLAP |
| 4h | +26.48 | +18.86 | ROBUST_SIGNIFICANT_POSITIVE | ×1.4 | MODERATE_OVERLAP |
| 24h | +49.54 | +18.10 | ROBUST_SIGNIFICANT_POSITIVE | ×2.7 | HIGH_OVERLAP |
| 72h | +58.99 | +16.81 | ROBUST_SIGNIFICANT_POSITIVE | ×3.5 | SEVERE_OVERLAP |

### a101_volume_cap_alpha_min_56_84 (robust cap factor)

| Horizon | Naive t | Robust t | Class | Inflation | Overlap |
|---------|---------|----------|-------|-----------|---------|
| 1h | +16.20 | +14.36 | ROBUST_SIGNIFICANT_POSITIVE | ×1.1 | NO_MAJOR_OVERLAP |
| 4h | +25.26 | +20.10 | ROBUST_SIGNIFICANT_POSITIVE | ×1.3 | MODERATE_OVERLAP |
| 24h | +46.37 | +16.62 | ROBUST_SIGNIFICANT_POSITIVE | ×2.8 | HIGH_OVERLAP |
| 72h | +55.68 | +14.28 | ROBUST_SIGNIFICANT_POSITIVE | ×3.9 | SEVERE_OVERLAP |

---

## 6. QA Results

| Check | Result |
|-------|--------|
| pm55_robust_payload: 84/84 factors have robust_rankic | ✓ PASS |
| pm55_horizon_coverage: all 4 horizons present | ✓ PASS |
| pm55_all_horizon_table: robust columns present | ✓ PASS |
| pm55_best_horizon_robust: robust t-stat label present | ✓ PASS |
| pm55_naive_only_example: funding_rate_zscore_80h NAIVE_ONLY | ✓ PASS |
| Page QA total | 33/33 PASS |
| Active workflow consistency | 13/13 PASS |
| No formula changes | ✓ |
| No factor_values changes | ✓ |
| No expected_direction changes | ✓ |
| No scorecard changes | ✓ |
| No best_horizon changes | ✓ |
| No signal construction | ✓ |
| No trading recommendation | ✓ |

---

## 7. Limitations

1. **Glossary not in separate JSON file:** Glossary entries are embedded in the How to Read section HTML, not in `factor_metric_glossary.json`. A future PM could extract them.
2. **No per-factor robust summary card:** The robust significance data is in the All-Horizon Table and Best Horizon Metrics, but there's no standalone "Robust Significance Card" section per factor.
3. **Robust t-stat not in Factor Scoreboard table:** The main scoreboard table doesn't have a robust t-stat column (only the per-factor detail view does). Could be added in a future PM.
4. **No filtering by robust class:** The page filters don't include a "Robust Class" filter option.

---

## 8. Recommended Next PM

- **PM-56**: Extend robust significance to LS returns and paper portfolio metrics
- **PM-57**: Add robust class filter to Factor Scoreboard
