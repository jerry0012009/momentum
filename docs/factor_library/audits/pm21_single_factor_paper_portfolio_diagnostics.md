# PM-21 Single-Factor Paper Portfolio Diagnostics

**Date:** 2026-06-21
**Follows:** PM-20 (regeneration contract)

---

## Summary Verdict

**`SINGLE_FACTOR_PAPER_DIAGNOSTICS_PASS`**

## 1. Files Generated

| File | Rows |
|------|------|
| single_factor_paper_summary.csv | 71 |
| single_factor_paper_summary.json | 71 |
| single_factor_paper_nav_curves.csv | 6,281,415 |
| single_factor_paper_monthly_returns.csv | 8,845 |
| single_factor_fee_sensitivity.csv | 355 |
| single_factor_paper_manifest.json | — |

## 2. Factor Coverage

Expected: 71. Actual: 71. Coverage: 100%.

## 3. Horizon

1h sequential returns. Chosen to avoid overlapping-return complications
that 4h/24h/72h horizons would create for NAV curves.

## 4. Portfolio Construction

- Cross-sectional long/short per timestamp.
- Long top 20% equal-weight.
- Short bottom 20% equal-weight.
- Direction-adjusted using expected_direction from scorecard.
- Turnover computed from symbol set changes between consecutive timestamps.
- NAV compounded from net returns.

## 5. Fee Assumptions

0, 2, 5, 10, 20 bps applied to turnover.

## 6. Viability Distribution

| Class | Count |
|-------|-------|
| PAPER_STRONG | 2 |
| PAPER_PROMISING | 1 |
| PAPER_MIXED | 35 |
| PAPER_WEAK | 14 |
| PAPER_REVIEW_REQUIRED | 19 |

## 7. Cost Sensitivity Distribution

| Class | Count |
|-------|-------|
| ROBUST_TO_COSTS | 0 |
| MODERATELY_COST_SENSITIVE | 2 |
| COST_FRAGILE | 2 |
| COST_COLLAPSED | 48 |
| INSUFFICIENT_DATA | 19 |

## 8. Top 10 by Gross Sharpe

| Factor | Gross Sharpe | 10bps Return |
|--------|-------------|-------------|
| candle_wick_upper | 7.580 | -1.0000 |
| funding_rate_level_20h | 6.224 | 4.8366 |
| amihud_illiquidity_20h | 3.586 | 2.4702 |
| rev_1h | 2.900 | -1.0000 |
| qvol_zscore_48h | 2.585 | -0.9995 |
| mom_20h | 2.350 | -0.7741 |
| qvol_zscore_20h | 2.188 | -0.9998 |
| ema_12_26_gap | 2.157 | 0.5588 |
| ma_gap_5_20 | 2.061 | -0.3660 |
| taker_buy_ratio_20h | 2.055 | -0.7851 |

## 9. Top by Fee-Adjusted (10bps Total Return)

| Factor | 10bps Return | Gross Sharpe |
|--------|-------------|-------------|
| funding_rate_level_20h | 4.8366 | 6.224 |
| amihud_illiquidity_20h | 2.4702 | 3.586 |
| ema_12_26_gap | 0.5588 | 2.157 |
| funding_rate_sensitivity_20h | 0.1555 | 0.311 |
| taker_buy_ratio_72h | 0.0986 | 0.831 |

## 10. Factors That Collapse After Costs

48 of 71 factors are COST_COLLAPSED — gross returns vanish after 10bps
transaction costs. Most momentum/reversal/volatility factors fall into this
category due to high turnover.

Only 2 factors (funding_rate_level_20h, amihud_illiquidity_20h) show
meaningful fee-adjusted returns at 10bps.

## 11. Runtime

853 seconds (14.2 minutes) for 71 factors. ~12s per factor.

## 12. Limitations

- 1h horizon only. Multi-horizon variants deferred to later PMs.
- Equal-weight legs, not market-cap weighted.
- No order book / slippage modeling.
- Not execution-ready. Research diagnostics only.
- Direction-conditional factors marked but not excluded.

## 13. Non-Change Statement

- No factors added or modified.
- No factor formulas changed.
- No factor_values changed.
- No signal panel changed.
- No public HTML pages changed.
- No production/live/tradeability claims.

## 14. Recommended Next PM

**PM-22** — Single-factor paper portfolio page integration
(add NAV curves, fee sensitivity, viability badges to factor-evaluation.html)
