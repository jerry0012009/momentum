# Phase 7A — Large-Scale Factor Mining Protocol & Candidate Backlog (Hardened)

> Date: 2026-06-14 (Phase 7A-QA hardening)
>
> Status: COMPLETE — PHASE 7B IMPLEMENTATION ALLOWED

---

## 1. Goal

Establish the factor mining protocol, candidate backlog, batching design, and
anti-snooping engineering constraints before implementing any new factors.

## 2. New Files

| File | Description |
|------|-------------|
| `docs/LARGE_SCALE_FACTOR_MINING_PROTOCOL.md` | Mining protocol, anti-snooping controls |
| `docs/PHASE_7_BATCHING_DESIGN.md` | Batch structure and completion gates |
| `research/.../factor_mining_candidates_v0_1.csv` | 86 candidate factors |

## 3. Candidate Factor Count

**86 candidates** across **15 families**.

## 4. Family Coverage Table

| Family | Total | 7B | 7C | 7D |
|--------|-------|-----|-----|-----|
| momentum | 5 | 3 | 0 | 2 |
| reversal | 4 | 3 | 0 | 1 |
| volatility | 4 | 3 | 0 | 1 |
| range_position | 3 | 3 | 0 | 0 |
| price_position | 3 | 2 | 0 | 1 |
| volume_liquidity | 3 | 2 | 0 | 1 |
| quote_volume_liquidity | 3 | 2 | 0 | 1 |
| trend_ma | 5 | 2 | 0 | 3 |
| breakout | 7 | 2 | 2 | 3 |
| intraday_candle | 6 | 3 | 0 | 3 |
| cross_sectional_normalized | 6 | 2 | 0 | 4 |
| technical_indicators | 7 | 0 | 7 | 0 |
| wq101_expansion | 18 | 0 | 18 | 0 |
| alpha158_expansion | 5 | 0 | 5 | 0 |
| realized_skew_kurtosis | 7 | 0 | 6 | 1 |
| **Total** | **86** | **27** | **36** | **18** |

## 5. 7B Selected Factor Count

**27 factors** across **11 families**.

Per-family breakdown:
- momentum: 3 (mom_5h, mom_10h, mom_40h)
- reversal: 3 (rev_3h, rev_10h, rev_24h)
- volatility: 3 (vol_5h, vol_40h, vol_ratio_5_20)
- range_position: 3 (range_1h, range_4h, range_24h)
- price_position: 2 (price_pos_24h, price_pos_72h)
- volume_liquidity: 2 (vol_zscore_20h, vol_zscore_48h)
- quote_volume_liquidity: 2 (qvol_zscore_20h, qvol_zscore_48h)
- trend_ma: 2 (ma_gap_5_20, ma_gap_10_40)
- breakout: 2 (breakout_dist_20h, breakout_dist_48h)
- intraday_candle: 3 (candle_body, candle_wick_upper, candle_wick_lower)
- cross_sectional_normalized: 2 (xs_rank_ret_1h, xs_rank_vol)

## 6. Data-Snooping Controls

- expected_direction set before evaluation (theory_prior or structural_prior)
- No PnL-based selection
- Phase 7 does not use p-value based alpha promotion.
  Batch discipline, out-of-sample checks, static-vs-dynamic comparison,
  and external validation are required before any stronger claim.
- No factor status upgrade in Phase 7
- No re-evaluation of dropped factors

## 7. expected_direction Policy

| Policy | Count |
|--------|-------|
| theory_prior | 54 |
| structural_prior | 24 |
| conditional_by_design | 8 |

No direction is set from evaluation results.

## 8. Test Enforcement

Tests strictly enforce:
- `20 <= selected_for_7B <= 30` (currently 27 ✓)
- All 15 required families present
- Each family has >= 3 candidates
- No evaluation-driven direction_policy
- No alpha status

## 9. Whether Phase 7B Is Allowed

**No — Phase 7B implementation is BLOCKED pending PM re-review.**

- 27 selected_for_7B (within 20-30 range) ✓
- All 15 families have >= 3 candidates ✓
- Tests strictly enforce above ✓
- All docs consistent with CSV ✓
