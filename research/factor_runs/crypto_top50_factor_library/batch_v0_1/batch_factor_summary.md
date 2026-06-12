# Batch V0.1 Factor Summary

- universe: crypto_top50_usdt_perp_1h
- evaluation_period: 2025-12-14 ~ 2026-06-12
- total_factors: 24
- new_factors: 19
- all factors: DIAGNOSTIC_PROBE / MONITOR / PARK — none promoted to CANDIDATE

## Factor Ranking (by |RankIC_mean|, best label)

| # | factor_id | family | best_label | RankIC_mean | RankICIR | spread_mean | warnings | severity | recommendation |
|---|---|---|---|---:|---:|---:|---|---|---|
| 1 | close_to_low_20h | technical | ret_fwd_4h | -0.0302 | -0.155 | +0.002703 | DIRECTION_CONFLICT | LOW | KEEP_AS_PROBE |
| 2 | reversal_1h | mean_reversion | ret_fwd_1h | +0.0301 | +0.150 | -0.000141 | DIRECTION_CONFLICT, WEAK_SIGNAL | MEDIUM | MONITOR |
| 3 | mom_72h | momentum | ret_fwd_72h | +0.0294 | +0.149 | +0.017722 | - | LOW | MONITOR |
| 4 | ma_gap_20h | technical | ret_fwd_4h | -0.0258 | -0.125 | +0.001091 | DIRECTION_CONFLICT, WEAK_SIGNAL | MEDIUM | MONITOR |
| 5 | reversal_4h | mean_reversion | ret_fwd_4h | +0.0253 | +0.124 | -0.001286 | DIRECTION_CONFLICT, WEAK_SIGNAL | MEDIUM | MONITOR |
| 6 | reversal_5h | mean_reversion | ret_fwd_1h | +0.0243 | +0.119 | -0.000229 | DIRECTION_CONFLICT, WEAK_SIGNAL | MEDIUM | MONITOR |
| 7 | mom_6h | momentum | ret_fwd_4h | -0.0230 | -0.112 | +0.001316 | DIRECTION_CONFLICT, WEAK_SIGNAL | MEDIUM | MONITOR |
| 8 | atr_14h | technical | ret_fwd_4h | -0.0225 | -0.115 | +0.003099 | DIRECTION_CONFLICT | LOW | MONITOR |
| 9 | hl_range_20h | technical | ret_fwd_4h | -0.0215 | -0.109 | +0.003114 | DIRECTION_CONFLICT | LOW | MONITOR |
| 10 | mom_20h | momentum | ret_fwd_4h | -0.0213 | -0.104 | +0.001252 | DIRECTION_CONFLICT, WEAK_SIGNAL | MEDIUM | MONITOR |
| 11 | volatility_72h | volatility | ret_fwd_4h | -0.0209 | -0.108 | +0.002998 | DIRECTION_CONFLICT | LOW | MONITOR |
| 12 | rsi_14h | technical | ret_fwd_72h | +0.0203 | +0.110 | +0.012402 | DIRECTION_CONFLICT | LOW | MONITOR |
| 13 | bb_zscore_20h | mean_reversion | ret_fwd_4h | -0.0200 | -0.105 | +0.001394 | DIRECTION_CONFLICT, WEAK_SIGNAL | MEDIUM | PARK |
| 14 | volatility_20h | volatility | ret_fwd_4h | -0.0191 | -0.099 | +0.003173 | DIRECTION_CONFLICT | LOW | PARK |
| 15 | mom_24h | momentum | ret_fwd_72h | +0.0189 | +0.093 | +0.010878 | DIRECTION_CONFLICT, WEAK_SIGNAL | MEDIUM | PARK |
| 16 | reversal_24h | mean_reversion | ret_fwd_72h | -0.0189 | -0.093 | -0.017930 | DIRECTION_CONFLICT, WEAK_SIGNAL | MEDIUM | PARK |
| 17 | volatility_24h | volatility | ret_fwd_24h | -0.0188 | -0.094 | +0.016300 | DIRECTION_CONFLICT | LOW | PARK |
| 18 | mom_12h | momentum | ret_fwd_4h | -0.0184 | -0.090 | +0.001487 | DIRECTION_CONFLICT, WEAK_SIGNAL | MEDIUM | PARK |
| 19 | reversal_12h | mean_reversion | ret_fwd_4h | +0.0184 | +0.090 | -0.002009 | DIRECTION_CONFLICT, WEAK_SIGNAL | MEDIUM | PARK |
| 20 | volatility_6h | volatility | ret_fwd_1h | -0.0162 | -0.082 | +0.000723 | DIRECTION_CONFLICT | LOW | PARK |
| 21 | close_to_high_20h | technical | ret_fwd_72h | +0.0156 | +0.084 | -0.023622 | DIRECTION_CONFLICT | LOW | PARK |
| 22 | volume_ratio_20h | volume | ret_fwd_4h | -0.0052 | -0.029 | +0.000595 | DIRECTION_CONFLICT, WEAK_SIGNAL | MEDIUM | PARK |
| 23 | quote_volume_zscore_20h | volume | ret_fwd_4h | -0.0039 | -0.023 | +0.000624 | DIRECTION_CONFLICT, WEAK_SIGNAL | MEDIUM | PARK |
| 24 | volume_zscore_20h | volume | ret_fwd_4h | -0.0033 | -0.019 | +0.000755 | DIRECTION_CONFLICT, WEAK_SIGNAL | MEDIUM | PARK |

## Summary

- **KEEP_AS_PROBE**: 1 factors — close_to_low_20h
- **MONITOR**: 11 factors — reversal_1h, mom_72h, ma_gap_20h, reversal_4h, reversal_5h, mom_6h, atr_14h, hl_range_20h, mom_20h, volatility_72h, rsi_14h
- **PARK**: 12 factors — bb_zscore_20h, volatility_20h, mom_24h, reversal_24h, volatility_24h, mom_12h, reversal_12h, volatility_6h, close_to_high_20h, volume_ratio_20h, quote_volume_zscore_20h, volume_zscore_20h

## Factors Worth Manual Review

These factors have |RankIC_mean| ≥ 0.025 and ≤ 2 warning flags:

- **close_to_low_20h** (technical): RankIC=-0.0302, best=ret_fwd_4h, warnings=1
- **reversal_1h** (mean_reversion): RankIC=+0.0301, best=ret_fwd_1h, warnings=2
- **mom_72h** (momentum): RankIC=+0.0294, best=ret_fwd_72h, warnings=0
- **ma_gap_20h** (technical): RankIC=-0.0258, best=ret_fwd_4h, warnings=2
- **reversal_4h** (mean_reversion): RankIC=+0.0253, best=ret_fwd_4h, warnings=2

## Notable Observations

1. **Momentum reversal at short horizons**: `reversal_1h` RankIC +0.030 on ret_fwd_1h — short-term mean reversion exists but expected_direction conflicts with long-momentum.
2. **Long-momentum works at 72h**: `mom_72h` RankIC +0.029 on ret_fwd_72h with 0 warnings — strongest clean signal in the batch.
3. **Volatility consistently negative**: All volatility factors show negative RankIC (higher vol → lower forward returns), consistent with risk premium.
4. **Volume factors are weak**: volume_zscore_20h, volume_ratio_20h, quote_volume_zscore_20h all |RankIC| < 0.01 — volume alone carries minimal cross-sectional info.
5. **close_to_low_20h surprise**: RankIC -0.030 on ret_fwd_4h — stocks near 20h lows tend to continue falling (trending, not reversing).

## Warning Distribution

| Warning | Count (factor-label pairs) |
|---|---|
| DIRECTION_CONFLICT | 23 / 24 |
| WEAK_SIGNAL | 14 / 24 |

## Methodology Notes

- IC: Pearson correlation of factor_value vs forward return, per cross-section timestamp.
- RankIC: Spearman rank correlation, more robust to outliers.
- spread_mean: Q5 mean return − Q1 mean return (quintile spread).
- DIRECTION_CONFLICT: IC sign ≠ RankIC sign or IC sign ≠ spread sign.
- WEAK_SIGNAL: max |ICIR| across all labels < 0.1.
- All factors are DIAGNOSTIC_PROBE — not used in any strategy.

This is factor evaluation, not strategy PnL. No factor was promoted to CANDIDATE.
