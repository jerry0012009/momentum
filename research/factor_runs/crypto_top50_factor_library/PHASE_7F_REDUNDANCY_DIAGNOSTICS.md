# Phase 7F — Factor Redundancy / Correlation Diagnostics

> Date: 2026-06-14
>
> Status: COMPLETE

---

## A. Scope

- Phase: 7F
- Factors: 27 selected_for_7B only
- Static dataset: `crypto_top50_usdt_perp_1h` (215,061 rows, full timestamps)
- Dynamic dataset: `crypto_usdt_perp_monthly_volume_top50_current_listed_1h_v1` (552,644 rows, sampled every 6th timestamp — 2,968/17,808 timestamps)
- Method: pairwise Spearman + Pearson correlation on wide factor value tables
- No new evaluation was run. No backtest. No alpha promotion.

---

## B. Pairwise Correlation Summary

| Metric | Static | Dynamic |
|--------|--------|---------|
| Pairs computed | 351/351 | 351/351 |
| NEAR_DUPLICATE (≥0.95) | 4 | 4 |
| HIGH_REDUNDANCY (0.85-0.95) | 7 | 6 |
| MODERATE_REDUNDANCY (0.70-0.85) | 32 | 26 |
| LOW_REDUNDANCY (<0.70) | 308 | 315 |

---

## C. Redundancy Groups

6 groups identified (connected by abs_spearman ≥ 0.85 in static or dynamic):

| group_id | factors | families | max_abs_corr_static | max_abs_corr_dynamic | representative_candidate | notes |
|----------|---------|----------|--------------------|--------------------|--------------------------|-------|
| RG1 | breakout_dist_20h; price_pos_24h | breakout; price_position | 0.9665 | 0.9507 | price_pos_24h | NEAR_DUPLICATE cross-family |
| RG2 | breakout_dist_48h; price_pos_72h | breakout; price_position | 0.9119 | 0.8912 | breakout_dist_48h | HIGH_REDUNDANCY cross-family |
| RG3 | ma_gap_10_40; rev_24h | trend_ma; reversal | 0.8503 | 0.8590 | rev_24h | Cross-family |
| RG4 | mom_10h; rev_10h | momentum; reversal | 1.0000 | 1.0000 | mom_10h | NEAR_DUPLICATE (opposite sign — rev is neg of mom) |
| RG5 | qvol_zscore_20h; qvol_zscore_48h; vol_zscore_20h; vol_zscore_48h | quote_volume_liquidity; volatility | 0.9983 | 0.9982 | qvol_zscore_20h | 4-way NEAR_DUPLICATE cluster |
| RG6 | range_24h; vol_40h | range_position; volatility | 0.8591 | 0.8180 | range_24h | Cross-family |

**Notable:** RG4 (mom_10h ↔ rev_10h) has spearman = -1.0 — perfect anti-correlation. This means rev_10h is mathematically equivalent to -mom_10h.

**Notable:** RG5 is a 4-way cluster of volume/quote-volume z-scores across 20h/48h windows — essentially the same signal with different lookbacks.

---

## D. Family-Level Summary (Same-Family Pairs Only)

| Family | N factors | N pairs | max abs_spearman static | max abs_spearman dynamic | Assessment |
|--------|-----------|---------|------------------------|------------------------|------------|
| breakout | 2 | 1 | 0.7760 | 0.7698 | MODERATE |
| cross_sectional_normalized | 2 | 1 | 0.0111 | 0.0164 | LOW |
| intraday_candle | 3 | 3 | 0.2064 | 0.1782 | LOW |
| momentum | 3 | 3 | 0.6351 | 0.6373 | LOW |
| price_position | 2 | 1 | 0.7121 | 0.7048 | MODERATE |
| quote_volume_liquidity | 2 | 1 | 0.8879 | 0.8727 | HIGH |
| range_position | 3 | 3 | 0.8416 | 0.7945 | MODERATE |
| reversal | 3 | 3 | 0.5685 | 0.5784 | LOW |
| trend_ma | 2 | 1 | 0.6618 | 0.6660 | LOW |
| volatility | 3 | 3 | 0.7222 | 0.6546 | MODERATE |
| volume_liquidity | 2 | 1 | 0.8897 | 0.8744 | HIGH |

**Highest within-family redundancy:** quote_volume_liquidity (qvol_zscore_20h ↔ qvol_zscore_48h = 0.888) and volume_liquidity (vol_zscore_20h ↔ vol_zscore_48h = 0.890).

**Cross-family redundancy is higher than within-family** for several groups — particularly breakout ↔ price_position and momentum ↔ reversal pairs.

---

## E. Highest Redundancy Pairs (Top 10)

| factor_i | factor_j | spearman | level |
|----------|----------|----------|-------|
| mom_10h | rev_10h | -1.0000 | NEAR_DUPLICATE |
| vol_zscore_20h | qvol_zscore_20h | 0.9983 | NEAR_DUPLICATE |
| vol_zscore_48h | qvol_zscore_48h | 0.9967 | NEAR_DUPLICATE |
| price_pos_24h | breakout_dist_20h | 0.9665 | NEAR_DUPLICATE |
| price_pos_72h | breakout_dist_48h | 0.9119 | HIGH_REDUNDANCY |
| vol_zscore_48h | qvol_zscore_20h | 0.8899 | HIGH_REDUNDANCY |
| vol_zscore_20h | vol_zscore_48h | 0.8897 | HIGH_REDUNDANCY |
| qvol_zscore_20h | qvol_zscore_48h | 0.8879 | HIGH_REDUNDANCY |
| vol_zscore_20h | qvol_zscore_48h | 0.8846 | HIGH_REDUNDANCY |
| vol_40h | range_24h | 0.8591 | HIGH_REDUNDANCY |

---

## F. Required Negative Declarations

- No new factor_values were built.
- No static evaluation was run.
- No dynamic evaluation was run.
- No static-vs-dynamic comparison was rerun.
- No strategy backtest was run.
- No portfolio simulation was run.
- No Qlib / VectorBT integration was run.
- No Alphalens tear sheet was run.
- No factor status was upgraded.
- No alpha claim was made.
- No factor was removed or selected for trading.

---

## G. Phase 7G Readiness

- ✓ 351 static pairs computed
- ✓ 351 dynamic pairs computed
- ✓ 6 redundancy groups generated
- ✓ No alpha promotion
- ✓ No factor removal or status upgrade

Phase 7G factor library curation / documentation consolidation is allowed pending PM review.
