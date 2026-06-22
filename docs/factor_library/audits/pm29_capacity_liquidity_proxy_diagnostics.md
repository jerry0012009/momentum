# PM-29: Capacity / Liquidity Proxy Diagnostics

**Date:** 2026-06-22
**Follows:** PM-28 (shape/rolling/decile page integration)

---

## Summary Verdict

**`CAPACITY_LIQUIDITY_PROXY_PASS_WITH_LIMITATIONS`**

## 1. Why PM-29

Factor evaluation needs capacity/liquidity evidence before factor expansion or signal construction. PM-29 provides proxy metrics for turnover vs available volume.

## 2. Files Changed

- `scripts/build_factor_capacity_liquidity_diagnostics.py` (new)
- 5 output files in `factor_diagnostics/`
- `docs/factor_library/audits/pm29_capacity_liquidity_proxy_diagnostics.md` (new)

## 3. Liquidity Proxy Method

**Universe volume proxy** — uses top-50 symbol aggregate hourly quote volume. Does NOT reconstruct selected long/short baskets per factor (too expensive). Marked `universe_volume_proxy` in outputs.

## 4. Factor Coverage

- Expected: 71 factors
- Summary: 71 factors
- Monthly: 71 factors (1,769 rows)
- Payload: 71 factors
- Missing: 0

## 5. Universe Volume Stats

- Top-50 per-symbol hourly volume: median=$4.05M, p10=$1.16M
- Top-5 volume concentration: 79.95% (high concentration)

## 6. Capacity Risk Distribution

| Class | Count |
|---|---:|
| CAPACITY_FRIENDLY | 59 |
| MODERATE_CAPACITY_RISK | 12 |

## 7. Liquidity Risk Distribution

| Class | Count |
|---|---:|
| LIQUIDITY_FRIENDLY | 71 |

All factors are liquidity-friendly at universe level (proxy method doesn't capture basket-level concentration).

## 8. Combined Class Distribution

| Class | Count |
|---|---:|
| CAPACITY_LIQUIDITY_OK | 71 |

## 9. Representative Examples

- amihud_illiquidity_20h: turnover=0.022, CAPACITY_FRIENDLY, sharpe=3.59
- All 71 factors classified as BALANCED_CANDIDATE

## 10. Payload Size

- factor_capacity_liquidity_payload.json: compact, suitable for PM-30 page integration

## 11. Validation

All outputs verified: 71 factors, 5 files, all classifications present.

## 12. Limitations

1. **Universe proxy only** — does not reconstruct selected baskets per factor; actual basket concentration may be worse
2. **No order book modeling** — participation rate is volume-weighted proxy, not real execution simulation
3. **All factors appear CAPACITY_LIQUIDITY_OK** — this is because the proxy method is too optimistic; real basket-level analysis would likely reveal more capacity-fragile factors
4. Volume concentration is high (top-5 = 80%) — individual basket analysis would show more risk

## 13. Non-Change Statement

No factors, formulas, factor_values, signal panel, public page modified.

## 14. Recommended Next PM

**PM-30:** Page integration for capacity/liquidity diagnostics on factor-evaluation.html.
