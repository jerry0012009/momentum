# PM-21B: Reproducible Paper Portfolio Repair

**Date:** 2026-06-22
**Follows:** PM-21 / PM-22 (original paper diagnostics)

---

## Summary Verdict

**`PAPER_PORTFOLIO_REPAIR_PASS`**

## 1. What Was Wrong in PM-21 / PM-22

### PM-21 Issues:
1. **Monthly fee returns used naive formula**: `monthly_gross_ret - monthly_turnover * fee_bps / 10000 * 24` — this is an approximation that doesn't compound hourly net returns within each month.
2. **No standalone turnover CSV**: turnover data was embedded in nav_curves but never extracted as a reproducible standalone file.
3. **Missing leg_decomposition.csv**: no long/short leg decomposition output.
4. **Missing drawdown_curve.csv**: no monthly NAV + drawdown output.
5. **nav_curves.csv was 1.1GB** (6.28M rows), too large for GitHub, listed in .gitignore.

### PM-22 Issues:
1. **Circular dependency**: `build_single_factor_paper_page_payload.py` read `single_factor_paper_turnover.csv` as timestamp-level input and wrote to the same path as output — a fragile local-artifact dependency.
2. **Missing new data sources**: payload didn't include leg_decomposition or drawdown_series.

## 2. Files Changed

### Scripts:
- `scripts/build_single_factor_paper_portfolio_diagnostics.py` — repaired
- `scripts/build_single_factor_paper_page_payload.py` — repaired

### Outputs (all 9 required):
| File | Rows | Factors | Status |
|---|---|---|---|
| single_factor_paper_summary.csv | 71 | 71 | ✓ |
| single_factor_paper_summary.json | 71 | 71 | ✓ |
| single_factor_paper_monthly_returns.csv | 8,845 | 71 | ✓ |
| single_factor_fee_sensitivity.csv | 355 | 71 | ✓ |
| single_factor_paper_turnover.csv | 1,769 | 71 | ✓ (was 75/3) |
| single_factor_paper_leg_decomposition.csv | 8,845 | 71 | ✓ (new) |
| single_factor_paper_drawdown_curve.csv | 8,845 | 71 | ✓ (new) |
| single_factor_paper_page_payload.json | 71 factors | 71 | ✓ |
| single_factor_paper_manifest.json | — | — | ✓ |

## 3. Schema Verification

### turnover.csv covers all factors: ✓
- 71 factors × ~25 months = 1,769 rows
- Columns: factor_id, month, avg_turnover, median_turnover, max_turnover, n_observations
- No timestamp column (monthly only)

### leg_decomposition.csv covers all factors: ✓
- 71 factors × 25 months × 5 fees = 8,845 rows
- Columns: factor_id, month, fee_bps, long_leg_return, short_leg_return, long_short_return, gross_long_short_return, net_long_short_return

### drawdown_curve.csv covers all factors: ✓
- 71 factors × 25 months × 5 fees = 8,845 rows
- Columns: factor_id, month, fee_bps, nav, drawdown, monthly_return

### Monthly fee returns compound hourly net returns: ✓
- Fixed: `np.prod(1 + net_ret_hourly[mask]) - 1` replaces `monthly_gross_ret - monthly_turnover * fee_bps / 10000 * 24`

### Page payload no longer depends on missing files: ✓
- Reads: summary.csv, monthly_returns.csv, fee_sensitivity.csv, turnover.csv, leg_decomposition.csv, drawdown_curve.csv
- All files are reproducible from committed scripts + committed inputs
- No timestamp-level turnover dependency

## 4. Cost Sensitivity Distribution (unchanged)

| Class | Count |
|---|---|
| COST_COLLAPSED | 48 |
| INSUFFICIENT_DATA | 19 |
| COST_FRAGILE | 2 |
| MODERATELY_COST_SENSITIVE | 2 |

## 5. Top 5 by 10bps Return

| Factor | Gross Sharpe | 10bps Return |
|---|---|---|
| funding_rate_level_20h | 6.22 | +4.84 |
| amihud_illiquidity_20h | 3.59 | +2.47 |
| ema_12_26_gap | 2.16 | +0.56 |
| skewness_20h | 1.23 | +0.39 |
| kurtosis_20h | 0.98 | +0.24 |

## 6. Limitations

1. nav_curves.csv (1.1GB) still not committed — can be regenerated locally.
2. Turnover is a set-change proxy, not execution turnover.
3. 1h horizon limits holding period; no multi-horizon analysis.
4. No order book / slippage modeling.

## 7. Non-Change Statement

- No factors added or modified.
- No factor formulas changed.
- No factor_values changed.
- No signal panel changed.
- No public HTML page changed.

## 8. Recommended Next PM

**PM-22B** — Page repair: update factor-evaluation.html to consume repaired payload.
