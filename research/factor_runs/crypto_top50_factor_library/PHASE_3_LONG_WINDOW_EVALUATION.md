# Phase 3 Long-Window Evaluation

> Date: 2026-06-13
>
> Status: COMPLETE
>
> Commit: `665dbe1` (data), current (evaluation)

---

## 1. Dataset

| Field | 180d (Phase 2E) | 2yr (Phase 3) |
|-------|------------------|----------------|
| **dataset_id** | `crypto_top50_usdt_perp_1h` | `crypto_top50_usdt_perp_1h_long_v1` |
| **date range** | 2025-12-15 ~ 2026-06-13 | 2024-06-13 ~ 2026-06-13 |
| **n_rows** | 215,061 | 713,572 |
| **n_symbols** | 50 | 50 |
| **evaluation symbols** | 49 (SPACEUSDT excluded) | 32 (18 excluded) |
| **n_timestamps** | ~4,300 | ~17,500 |

## 2. Excluded Symbols

18 symbols excluded from long-window evaluation (missing_bar_rate > 5%):

| Symbol | Missing Rate | Reason |
|--------|-------------|--------|
| SPACEUSDT | 80.7% | Listed ~2025-09 |
| BEATUSDT | 70.8% | Listed ~2025-06 |
| ALLOUSDT | 70.7% | Listed ~2025-06 |
| LABUSDT | 67.3% | Listed ~2025-05 |
| XPLUSDT | 59.6% | Listed ~2025-03 |
| AIOUSDT | 58.4% | Listed ~2025-03 |
| PLAYUSDT | 56.6% | Listed ~2025-03 |
| ESPORTSUSDT | 56.3% | Listed ~2025-03 |
| VELVETUSDT | 54.4% | Listed ~2025-02 |
| HUSDT | 51.7% | Listed ~2025-02 |
| HOMEUSDT | 49.6% | Listed ~2025-01 |
| HYPEUSDT | 48.1% | Listed ~2025-01 |
| SKYAIUSDT | 45.8% | Listed ~2025-01 |
| PAXGUSDT | 39.3% | Listed ~2024-11 |
| SIRENUSDT | 38.7% | Listed ~2024-11 |
| EPICUSDT | 37.4% | Listed ~2024-11 |
| TRUMPUSDT | 30.1% | Listed ~2024-10 |
| HMSTRUSDT | 14.4% | Listed ~2024-09 |

**Note:** These are all newer tokens that didn't exist for the full 2-year window. Not data quality errors.

## 3. Factor Evaluation: 180d vs 2yr (ret_fwd_1h)

| Factor | IC (180d) | IC (2yr) | RankIC (180d) | RankIC (2yr) | Raw Spread (180d) | Raw Spread (2yr) | Stable? |
|--------|-----------|----------|---------------|--------------|-------------------|-------------------|---------|
| mom_20h | +0.0045 | -0.0118 | -0.0152 | -0.0250 | +0.035bp | +0.002bp | ❌ flip |
| reversal_5h | -0.0076 | +0.0220 | +0.0238 | +0.0328 | -0.029bp | +0.007bp | ⚠️ mixed |
| volatility_20h | +0.0048 | -0.0126 | -0.0167 | -0.0295 | +0.071bp | +0.008bp | ❌ flip |
| rsi_14h | +0.0094 | -0.0094 | -0.0136 | -0.0236 | +0.050bp | +0.007bp | ❌ flip |
| bb_zscore_20h | +0.0045 | -0.0119 | -0.0187 | -0.0253 | +0.042bp | +0.004bp | ❌ flip |
| wq101_alpha101 | -0.0053 | -0.0156 | -0.0255 | -0.0232 | +0.007bp | -0.005bp | ⚠️ consistent IC |
| wq101_alpha12 | +0.0003 | -0.0004 | +0.0030 | +0.0050 | -0.016bp | -0.002bp | ⚠️ near-zero |
| wq101_alpha53 | +0.0029 | +0.0090 | +0.0156 | +0.0173 | -0.013bp | +0.011bp | ⚠️ signs ok |
| q158_high_low_range | +0.0065 | -0.0110 | -0.0161 | -0.0272 | +0.071bp | +0.009bp | ❌ flip |
| tech_macd | -0.0000 | -0.0001 | -0.0064 | -0.0086 | +0.023bp | +0.001bp | ✅ consistent (zero) |
| tech_atr | -0.0010 | +0.0051 | +0.0092 | +0.0092 | -0.008bp | +0.004bp | ⚠️ RankIC stable |

## 4. Key Observations

### Signal Stability

**No factor shows stable, actionable signal across both windows.**

- **IC signs flip** for 5/11 factors between 180d and 2yr (mom_20h, volatility_20h, rsi_14h, bb_zscore_20h, q158_high_low_range)
- **IC magnitudes** remain < 0.03 everywhere — well below any practical threshold
- **RankIC** is slightly more stable than IC (tech_atr RankIC = 0.0092 in both), but still very weak
- **Raw spreads** shrink dramatically in the 2yr window for most factors

### What Changed

The 2yr window adds ~13,200 timestamps (~4x). If signals were real, we'd expect:
- More precise IC estimates (tighter confidence intervals)
- More stable RankIC
- Clearer quintile separation

Instead we see:
- IC signs inconsistent — suggests noise, not signal
- Raw spreads compressed — suggests the 180d results were sample-specific
- Only tech_macd remains consistently near-zero (no signal in either window)

### Conditional Factors

For `wq101_alpha12`, `wq101_alpha53`, `q158_high_low_range`, `tech_atr`:
- direction_adjusted_spread = null (correctly handled)
- IC / RankIC / raw_spread used as diagnostics only
- None show directional signal worth investigating

## 5. Conclusion

**Phase 3 long-window evaluation is complete.**

The 2-year evaluation confirms that the current 11-factor library has no actionable signal. IC signs are inconsistent across time windows, magnitudes are negligible, and raw spreads are near zero. The extended window provides more statistical power but does not rescue any factor.

**No factor promoted to CANDIDATE_REVIEW.**
**No factor promoted to ALPHA.**

## 6. Next Phase Decision

**Phase 4: NOT ALLOWED**

Before Phase 4 can start:
- Need a fundamentally different factor generation approach (not just more windows of the same formulas)
- Consider: cross-sectional momentum with volatility scaling, funding rate factors, liquidation cascade factors
- Or: accept that static Top50 + simple OHLCV factors is insufficient for crypto alpha discovery
