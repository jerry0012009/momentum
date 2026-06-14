# Phase 7I-D — Batch-2 Redundancy Diagnostics

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase: 7I-D
- 9 PM-approved Batch-2 factors only
- Static dataset: crypto_top50_usdt_perp_1h (215,061 rows, 50 symbols)
- Dynamic dataset: crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1 (3,316,259 rows, 266 symbols)
- Pairwise Spearman correlation, redundancy groups via connected components
- No build/evaluation/classification/backtest

---

## B. Pairwise Summary

- Static pairs: 36
- Dynamic pairs: 36

### Redundancy Levels

| Level | Static | Dynamic |
|-------|--------|---------|
| LOW_REDUNDANCY | 31 | 31 |
| MODERATE_REDUNDANCY | 3 | 3 |
| HIGH_REDUNDANCY | 2 | 2 |
| NEAR_DUPLICATE | 0 | 0 |

---

## C. Redundancy Groups

| group_id | factors | families | max_static | max_dynamic | representative | notes |
|----------|---------|----------|------------|-------------|----------------|-------|
| RG_B2_1 | ema_12_26_gap; rsi_28h | technical_indicators | 0.889 | 0.899 | ema_12_26_gap | EMA gap correlated with RSI |
| RG_B2_2 | rsi_7h; williams_r_14h | technical_indicators | 0.918 | 0.913 | rsi_7h | RSI and Williams %R near-inverse |

### Highest Redundancy Pairs

| Pair | Static Spearman | Dynamic Spearman | Level |
|------|----------------|-----------------|-------|
| rsi_7h <-> williams_r_14h | -0.9176 | -0.9134 | HIGH_REDUNDANCY |
| ema_12_26_gap <-> rsi_28h | 0.8890 | 0.8986 | HIGH_REDUNDANCY |
| downside_vol_20h <-> vol_of_vol_20h | 0.8170 | 0.7753 | MODERATE_REDUNDANCY |
| rsi_28h <-> rsi_7h | 0.7550 | 0.7494 | MODERATE_REDUNDANCY |
| rsi_28h <-> ma_gap_20_80 | 0.7056 | 0.7071 | MODERATE_REDUNDANCY |

---

## D. Family-Level Summary

| family | n_factors | n_pairs | max_static | max_dynamic | assessment |
|--------|-----------|---------|------------|-------------|------------|
| realized_skew_kurtosis | 2 | 1 | 0.817 | 0.775 | MODERATE_REDUNDANCY_EXISTS |
| technical_indicators | 4 | 6 | 0.918 | 0.913 | HIGH_REDUNDANCY_EXISTS |

Other families (momentum, quote_volume_liquidity, trend_ma) have 1 factor each — no same-family pairs.

---

## E. Important Observations

1. **rsi_7h <-> williams_r_14h**: HIGH_REDUNDANCY (|Spearman| ~0.91). Both measure overbought/oversold — expected structural similarity. rsi_7h selected as representative (TIER_1 vs TIER_2, lower turnover).
2. **ema_12_26_gap <-> rsi_28h**: HIGH_REDUNDANCY (Spearman ~0.89). EMA gap and RSI both trend-following signals at similar timescales. ema_12_26_gap selected as representative (TIER_2, lower turnover).
3. **downside_vol_20h <-> vol_of_vol_20h**: MODERATE_REDUNDANCY (~0.78-0.82). Both volatility-based, expected partial overlap. Both TIER_1 — worth keeping both for now.
4. **technical_indicators family** has the most redundancy (4 factors, 6 pairs, 2 HIGH_REDUNDANCY pairs). If pruning needed, this family is the primary target.
5. **momentum, quote_volume_liquidity, trend_ma** families: single factors, no redundancy risk.

---

## F. Required Negative Declarations

No factor_values were built.
No static evaluation was run.
No dynamic evaluation was run.
No static-vs-dynamic comparison was rerun.
No diagnostic classification was rerun.
No strategy backtest was run.
No portfolio simulation was run.
No Qlib / VectorBT / Backtrader integration was run.
No Alphalens tear sheet was run.
No factor status was upgraded to CANDIDATE_REVIEW.
No alpha claim was made.
No factor was removed or selected for trading.

---

## G. Phase 7I-E Readiness

- ✓ Static pairwise CSV has 36 rows
- ✓ Dynamic pairwise CSV has 36 rows
- ✓ Redundancy groups file exists (2 groups)
- ✓ Family redundancy summary exists (2 families)
- ✓ No alpha/status promotion occurred
- ✓ No factor removal occurred

Phase 7I-E Batch-2 curated library update is allowed pending PM review.
