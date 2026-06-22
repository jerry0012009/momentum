# PM-26: Quantile Shape & Rolling Stability Diagnostics — Audit

**Generated:** 2026-06-22  
**Script:** `scripts/build_factor_shape_stability_diagnostics.py`  
**Ticket:** PM-26

---

## Verdict

**PASS** — Script produces 7 output files covering all 71 registered factors across 4 horizons (1h, 4h, 24h, 72h). Quantile shape and rolling stability diagnostics are computed from monthly IC and long-short return series, with monotonicity classification, tail concentration analysis, and stability scoring. Payload is compact (303 KB) and ready for page integration.

---

## Factor / Horizon Coverage

| Metric | Value |
|--------|-------|
| Registered factors (state file) | 71 |
| Shape diagnostics factors | 71 |
| Stability diagnostics factors | 71 |
| Timeseries rows | 7,076 (71 factors × 4 horizons × ~25 months) |
| Payload factors | 71 |
| Horizons | 1h, 4h, 24h, 72h |
| Months covered | 2024-06 to 2026-06 (25 months) |
| Quantile buckets per factor | 5 (Q1–Q5) |

**Coverage: 100%** — All 71 registered factors × 4 horizons = 284 factor-horizon pairs.

---

## Shape Class Distribution

| Quantile Shape Class | Count | % |
|---------------------|------:|--:|
| NO_CLEAR_SHAPE | 193 | 67.9% |
| WEAK_MONOTONIC | 61 | 21.5% |
| MIXED_SHAPE | 23 | 8.1% |
| EXCELLENT_MONOTONIC | 7 | 2.5% |
| **Total** | **284** | **100%** |

**Interpretation:** Most factors (68%) show no clear quantile monotonicity pattern. Only 7 factor-horizon pairs achieve EXCELLENT_MONOTONIC classification (monotonicity_score=1.0, |Spearman|=1.0). This is consistent with crypto markets being noisy and many factors having weak or inconsistent cross-sectional return separation.

### Monotonicity Class Distribution

| Monotonicity Class | Count |
|-------------------|------:|
| FLAT_NO_SHAPE | 193 |
| MONOTONIC_STRONG | 28 |
| MONOTONIC_WEAK | 35 |
| U_SHAPED_OR_REVERSAL | 28 |

---

## Stability Class Distribution

| Stability Class | Count | % |
|----------------|------:|--:|
| STABLE_WEAK | 194 | 68.3% |
| STABLE_POSITIVE | 48 | 16.9% |
| UNSTABLE_SIGN_FLIP | 27 | 9.5% |
| REGIME_OR_PERIOD_DEPENDENT | 15 | 5.3% |
| **Total** | **284** | **100%** |

**Interpretation:** 48 factor-horizon pairs (17%) show stable positive performance suitable for portfolio inclusion. 194 pairs show stability but weak signals. 27 pairs have unstable sign flips, and 15 are regime-dependent.

---

## Examples of Strong Factors (EXCELLENT_MONOTONIC + STABLE_POSITIVE)

| Factor | Horizon | Monotonicity | Spearman | Spread | Pos Spread Rate | Stability | IC Pos Rate |
|--------|---------|:-----------:|:--------:|:------:|:--------------:|:---------:|:-----------:|
| amihud_illiquidity_20h | 1h | 1.0 | -1.0 | -9.3e-5 | 76.0% | STABLE_POSITIVE | 72.0% |
| amihud_illiquidity_20h | 4h | 1.0 | -1.0 | -4.0e-4 | 80.0% | STABLE_POSITIVE | 80.0% |
| funding_rate_level_20h | 4h | 1.0 | -1.0 | -3.4e-4 | 79.2% | STABLE_POSITIVE | 91.7% |
| funding_rate_level_20h | 72h | 1.0 | -1.0 | -1.2e-2 | 75.0% | STABLE_POSITIVE | 95.8% |
| funding_rate_level_20h | 24h | — | — | — | — | STABLE_POSITIVE | 95.8% |
| candle_wick_upper | 1h | 1.0 | -1.0 | -1.6e-4 | 80.0% | STABLE_POSITIVE | 84.0% |

**Top factors by stability_score:** funding_rate_level_20h (83–85 across horizons), funding_rate_change_24h/24h (82.5), candle_wick_upper (79.2).

---

## Examples of Weak / Unstable Factors

| Factor | Horizon | Stability Class | IC Pos Rate | Recent Δ IC |
|--------|---------|----------------|:-----------:|:-----------:|
| bb_zscore_20h | 1h | UNSTABLE_SIGN_FLIP | 0.0% | +0.0007 |
| bb_zscore_20h | 24h | UNSTABLE_SIGN_FLIP | 16.0% | -0.0049 |
| candle_body | 1h | UNSTABLE_SIGN_FLIP | 0.0% | -0.0040 |
| intraday_ret | 1h | UNSTABLE_SIGN_FLIP | 0.0% | +0.0002 |
| klow_close | 1h | UNSTABLE_SIGN_FLIP | 0.0% | +0.0043 |

These factors show IC positive rates below 40% across both IC and LS, indicating fundamentally inconsistent directional signals.

---

## Payload & File Sizes

| File | Size |
|------|------|
| factor_quantile_shape_summary.csv | 69.3 KB |
| factor_quantile_shape_summary.json | 205.9 KB |
| factor_rolling_stability_summary.csv | 88.8 KB |
| factor_rolling_stability_summary.json | 281.8 KB |
| factor_shape_stability_timeseries.csv | 604.3 KB |
| factor_shape_stability_payload.json | 303.0 KB |
| factor_shape_stability_manifest.json | 1.5 KB |

**Total output:** ~1.56 MB. Payload JSON (303 KB) is suitable for page integration.

---

## Limitations

1. **5 quantile buckets only** — Finer granularity (10 deciles) would better detect tail concentration and non-linear effects. Current Q1–Q5 resolution limits shape discrimination.
2. **No cross-factor shape correlation** — Shape diagnostics are computed independently per factor; redundant factors may show similar shapes.
3. **Stability score is heuristic** — Composite scoring weights are calibrated empirically, not optimized. Different weighting could shift classifications.
4. **No regime-conditional shape** — Quantile shape is computed over the full period. Factors may show strong monotonicity in some regimes but not others.
5. **IC direction ambiguity** — For factors with expected_direction=positive but negative IC, the monotonicity direction uses expected_direction, which may not match observed data direction.
6. **25 months of history** — Limited for robust rolling stability assessment, especially for 6-month windows.

---

## Technical Notes

- Quantile data sourced from `factor_level_evaluation/factor_level_period_quantile_return_summary.csv` (5 buckets per factor/horizon/month)
- Monthly IC and LS data from `factor_diagnostics/factor_monthly_ic_series.csv` and `factor_monthly_long_short_series.csv`
- Rolling windows default: 3 and 6 months
- Minimum months for classification: 6
- Monotonicity scoring: share of adjacent bucket steps in expected direction
- Spearman correlation: bucket index vs mean return across all months

---

## Recommended Next PM

**PM-27: Decile-level quantile return analysis** — Extend to 10 quantile buckets for finer shape discrimination and better tail detection. This would improve differentiation between EXCELLENT_MONOTONIC and WEAK_MONOTONIC factors, and enable better tail concentration analysis.
