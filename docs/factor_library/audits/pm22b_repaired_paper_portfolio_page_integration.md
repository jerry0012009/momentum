# PM-22B: Repaired Paper Portfolio Page Integration

**Date:** 2026-06-22
**Follows:** PM-21B (repaired data layer) / PM-22 (original page integration)

---

## Summary Verdict

**`REPAIRED_PAPER_PAGE_INTEGRATION_PASS`**

## 1. Files Changed

- `scripts/_build_factor_eval_html.py` — 3 new chart sections added
- `reports/site/factor-library/factor-evaluation.html` — rebuilt (2,084,808 bytes)

## 2. No New Public Page Created

Confirmed. Only the existing `factor-evaluation.html` was updated.

## 3. Payload Fields Consumed

From `single_factor_paper_page_payload.json`:
- `turnover_series` — monthly avg/median turnover (25 months per factor)
- `leg_decomposition_series` — monthly long/short/net returns at 10bps
- `drawdown_series` — monthly NAV, drawdown, return at 10bps
- `monthly_nav_series_compact` — 0bps vs 10bps NAV (existing, updated)
- `fee_sensitivity_series` — total return / Sharpe by fee level (existing)
- `monthly_return_series` — monthly returns at 10bps (existing)

## 4. New Charts Added

1. **Monthly Turnover** — line chart of `avg_turnover` per month (amber/gold)
2. **Leg Decomposition** — 3-line chart: Long (green), Short (red), Net L/S (blue)
3. **Paper Portfolio NAV & Drawdown** — dual-axis: NAV curve (blue) + drawdown shading (red)

## 5. Existing Sections Preserved

- ✅ Factor metadata / formula / bilingual cards
- ✅ Scorecard
- ✅ Redundancy & novelty
- ✅ BTC / Market Regime Diagnostics (BTC / 市场状态诊断)
- ✅ Original factor diagnostics charts
- ✅ Paper portfolio metrics grid

## 6. Validation Results

| Check | Status |
|---|---|
| Single-Factor Paper Portfolio | ✓ |
| 单因子纸面组合 | ✓ |
| leg_decomposition_series | ✓ |
| drawdown_series | ✓ |
| turnover_series | ✓ |
| Drawdown | ✓ |
| Turnover | ✓ |
| Fee Sensitivity | ✓ |
| BTC / Market Regime Diagnostics | ✓ |
| BTC / 市场状态诊断 | ✓ |
| research diagnostic | ✓ |
| 不是交易策略 | ✓ |

## 7. HTML Size

- Before: ~1,650,000 bytes (PM-24 version)
- After: 2,084,808 bytes
- Limit: 3,500,000 bytes
- Status: ✓ Under limit

## 8. Limitations

1. Regime diagnostics (PM-23/PM-24) were built before PM-21B paper recalculation. Current regime section uses pre-repair paper returns. PM-23B should refresh regime diagnostics using repaired PM-21B paper monthly returns.
2. Leg decomposition chart shows 10bps fee level only (not all 5 fee levels).
3. Drawdown chart shows 10bps fee level only.

## 9. Non-Change Statement

- No factors added or modified.
- No factor formulas changed.
- No factor_values changed.
- No signal panel changed.
- No new public page created.

## 10. Recommended Next PM

**PM-23B** — Regime diagnostics refresh using repaired PM-21B paper monthly returns.
