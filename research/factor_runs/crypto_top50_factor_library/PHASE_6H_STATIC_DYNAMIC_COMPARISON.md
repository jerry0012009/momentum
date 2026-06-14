# Phase 6H — Static-vs-Dynamic Factor Evaluation Comparison (Hardened)

> Date: 2026-06-14 (Phase 6H-QA hardening)
>
> Status: COMPLETE — PHASE 6 CAN BE CLOSED

---

## 1. Goal

Compare factor evaluation results between static current Top50 universe and
dynamic monthly-volume universe. Identify robust vs weakened vs direction-mismatch
factors. Harden interpretation with catalog-expected directions and conservative tags.

## 2. Universe Definitions

| | Static | Dynamic |
|---|---|---|
| Universe | `crypto_top50_usdt_perp_1h_long_v1` | `crypto_usdt_perp_monthly_volume_top50_current_listed_v1` |
| Mode | Fixed current Top50 symbols | Monthly top50 by volume, dynamic membership |
| Symbols | 50 | 266 |
| Period | 2024-06-13 ~ 2026-06-13 | 2024-06-01 ~ 2026-06-13 |

**Period alignment caveat:** The comparison is close but not perfectly period-aligned.
Phase 7 may proceed with this caveat recorded; future strict comparison should align
exact timestamps.

## 3. Major Limitations

- Dynamic universe is still `dynamic_from_current_listed_pool`, **not true point-in-time**.
- It reduces static-current-top50 bias but **does not eliminate delisted-symbol survivorship bias**.
- expected_direction comes from `factor_catalog_v0_1.csv` (authoritative), not from dynamic JSON.
- No factor is alpha. No factor status is upgraded.

## 4. Stability Tag Summary (ret_fwd_1h)

| Tag | Count |
|-----|-------|
| strong_robust_diagnostic_candidate | 5 |
| moderate_stable_diagnostic_candidate | 3 |
| unstable_or_near_zero | 3 |

## 5. Direction Mismatch Factors (ret_fwd_1h)

These factors have stable empirical RankIC signs but **do not match catalog expected_direction**:

| Factor | Expected | Static RankIC | Dynamic RankIC | Notes |
|--------|----------|--------------|---------------|-------|
| mom_20h | positive | -0.0250 | -0.0191 | Both negative; empirical sign contradicts expected |
| reversal_5h | negative | +0.0328 | +0.0282 | Both positive; empirical sign contradicts expected |
| tech_macd | positive | -0.0086 | -0.0065 | Both negative; weak but consistent mismatch |
| wq101_alpha101 | positive | -0.0232 | -0.0176 | Both negative; empirical sign contradicts expected |

**These factors should remain diagnostic only.** Stable empirical sign does not mean
the expected_direction is correct.

## 6. Direction Consistent Factors (ret_fwd_1h)

| Factor | Expected | Static RankIC | Dynamic RankIC | Stability |
|--------|----------|--------------|---------------|-----------|
| volatility_20h | negative | -0.0295 | -0.0428 | strong_robust |
| rsi_14h | negative | -0.0236 | -0.0210 | strong_robust |
| bb_zscore_20h | negative | -0.0253 | -0.0244 | strong_robust |

These 3 factors have empirical signs consistent with expected_direction and
strong stability across both universes.

## 7. Conditional Direction Factors

| Factor | Static RankIC | Dynamic RankIC | Stability |
|--------|--------------|---------------|-----------|
| q158_high_low_range | -0.0272 | -0.0413 | strong_robust |
| wq101_alpha53 | +0.0173 | +0.0127 | moderate_stable |
| tech_atr | +0.0092 | +0.0200 | unstable |
| wq101_alpha12 | +0.0050 | +0.0041 | unstable |

Conditional factors have no expected_direction constraint; stability is assessed
purely on empirical sign consistency.

## 8. What Changed After Universe Correction

- **volatility_20h got stronger** (RankIC -0.030 → -0.043): More mid-cap symbols amplify signal.
- **q158_high_low_range got stronger** (RankIC -0.027 → -0.041): Similar effect.
- **mom_20h got weaker** (RankIC -0.025 → -0.019): Momentum diluted across more symbols.
- **No factors sign-flipped or weakened** (under conservative thresholds).

## 9. Conservative Conclusion

Several factors show stable empirical RankIC signs across static and dynamic universes,
but some do not match catalog expected_direction and should remain diagnostic only.

- **3 factors** are direction-consistent and strong-robust: volatility_20h, rsi_14h, bb_zscore_20h.
- **4 factors** have direction mismatch: mom_20h, reversal_5h, tech_macd, wq101_alpha101.
- **No factor is alpha.** All remain DIAGNOSTIC_PROBE.

## 10. Whether Phase 6 Can Be Closed

**Yes — Phase 6 can be closed after interpretation hardening.**

## 11. Whether Phase 7 Planning Is Allowed

**Yes — Phase 7 (large-scale factor mining infrastructure) may proceed.**
No factor status upgrades. No alpha claims.
