# Phase 7M-F — Crypto-native Curated Library Update

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase 7M-F: curation only
- Integrate 6 crypto-native diagnostic factors into curated library v0.4
- No alpha promotion, no CANDIDATE_REVIEW, no backtest, no factor removal

---

## B. Results

### Library Update

| Item | Count |
|------|-------|
| v0.3 factors | 36 |
| Crypto-native added | 6 |
| v0.4 factors | 42 |
| v0.4 families | 15 (was 13) |
| New families | taker_imbalance, funding_rate |

### Crypto-native Curated Factors

| factor_id | family | tier | recommended_research_use |
|-----------|--------|------|--------------------------|
| taker_buy_ratio_20h | taker_imbalance | TIER_2 | REVIEW_DIRECTION_OR_FORMULA |
| taker_buy_zscore_20h | taker_imbalance | TIER_2 | REVIEW_DIRECTION_OR_FORMULA |
| taker_buy_delta_5h | taker_imbalance | TIER_3 | WEAK_DIAGNOSTIC_ONLY |
| funding_rate_level_20h | funding_rate | TIER_3 | REVIEW_DIRECTION_OR_FORMULA |
| funding_rate_zscore_80h | funding_rate | TIER_3 | WEAK_DIAGNOSTIC_ONLY |
| funding_rate_change_24h | funding_rate | TIER_4 | LOW_PRIORITY_RESEARCH |

### Redundancy Review Queue v0.4

- 8 existing v0.3 redundancy groups carried forward
- 2 new medium review pairs added:
  - taker_buy_delta_5h / taker_buy_zscore_20h (dynamic abs_corr=0.694)
  - funding_rate_change_24h / funding_rate_zscore_80h (dynamic abs_corr=0.668)
- All crypto-native pairs are MEDIUM_REVIEW only, not deletion

### Redundancy Status

- No redundancy pairs at abs(corr) >= 0.80
- Cross-family taker vs funding: essentially orthogonal (max 0.091)
- Crypto-native factors add non-redundant data-native dimensions

---

## C. Phase 7M-F Status

Phase 7M-F is curation only.
6 crypto-native factors were integrated into curated library v0.4.
No factor was removed.
No factor was promoted.
No alpha claim was made.
No backtest was run.
Dynamic universe remains diagnostic and not true PIT.
Crypto-native factors add non-redundant data-native dimensions but remain diagnostic probes.

---

## D. Negative Declarations

No factor_values were built.
No labels were rebuilt.
No strategy backtest was run.
No portfolio simulation was run.
No factor status was upgraded to CANDIDATE_REVIEW.
No alpha claim was made.
No factor was removed or selected for trading.
