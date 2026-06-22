# PM-24B: Refresh Regime Page After Paper Repair

**Date:** 2026-06-22
**Follows:** PM-21B / PM-22B / PM-23B

---

## Summary Verdict

**`REGIME_PAGE_REFRESH_AFTER_PAPER_REPAIR_PASS`**

## 1. Files Changed

- `reports/site/factor-library/factor-evaluation.html` — rebuilt (2,084,279 bytes)
- `scripts/_build_factor_eval_html.py` — no changes needed (already reads correct files)

## 2. No New Public Page Created: ✓

Confirmed. Only existing `factor-evaluation.html` was rebuilt.

## 3. Page Consumes PM-23B Refreshed Regime Payload: ✓

Regime distribution in page payload:
```
REGIME_ROBUST:      29
VOL_DEPENDENT:      17
BEAR_DEPENDENT:     12
BULL_DEPENDENT:     11
DRAWDOWN_FRAGILE:    2
```

Exact match with PM-23B expected distribution. All 71 factors have `regime_dependency_class`, `paper_return_btc_beta`, and `regime_detail` from PM-23B refreshed outputs.

## 4. PM-22B Paper Charts Preserved: ✓

- `turnover_series`: present
- `leg_decomposition_series`: present
- `drawdown_series`: present
- `monthly_nav_series_compact`: present
- `fee_sensitivity_series`: present
- `monthly_return_series`: present

## 5. HTML Size

- Before (PM-22B): 2,084,808 bytes
- After (PM-24B): 2,084,279 bytes (slightly smaller due to regime distribution shift)
- Limit: 3,500,000 bytes

## 6. Validation Results

| Check | Status |
|---|---|
| BTC / Market Regime Diagnostics | ✓ |
| BTC / 市场状态诊断 | ✓ |
| REGIME_ROBUST | ✓ |
| BULL_DEPENDENT | ✓ |
| BEAR_DEPENDENT | ✓ |
| VOL_DEPENDENT | ✓ |
| DRAWDOWN_FRAGILE | ✓ |
| Single-Factor Paper Portfolio | ✓ |
| leg_decomposition_series | ✓ |
| drawdown_series | ✓ |
| turnover_series | ✓ |
| 不是交易策略 | ✓ |
| Regime distribution matches PM-23B | ✓ |
| PM-22B paper charts preserved | ✓ |

## 7. Limitations

1. Regime charts in the detail panel render from `regime_detail` data in the factor payload. No separate chart canvas IDs were found — charts are rendered by the JS renderer.
2. No script changes were needed, so no `git diff` on the builder script.

## 8. Non-Change Statement

- No factors added or modified.
- No factor formulas changed.
- No factor_values changed.
- No signal panel changed.
- No regime diagnostics recomputed.
- No paper portfolio diagnostics recomputed.

## 9. Recommended Next PM

**PM-25** — Reusable staleness / workflow monitor.
