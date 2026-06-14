# Phase 7H — Batch-2 Factor Mining Preparation

> Date: 2026-06-14
>
> Status: COMPLETE AS SERVER DRAFT; SUPERSEDED BY PM REVIEW

> PM note: this server-generated plan is accepted as candidate inventory and scoring draft only. The final Batch-2 implementation list is defined by `PHASE_7H_PM_REVIEW.md` and `phase7h_pm_approved_batch2.csv`. Do not use the 18 server `SELECT_NOW` rows below as the Phase 7I implementation list.

---

## A. Scope

- Phase: 7H
- Batch-2 candidate selection only
- No implementation, no build, no evaluation, no backtest
- 59 remaining candidates reviewed (86 total - 27 Batch-1)

---

## B. Candidate Pool Summary

| Category | Count |
|----------|-------|
| Total candidates reviewed | 59 |
| Already in Batch-1 | 27 |
| Server SELECT_NOW draft | 18 |
| PM-approved for 7I | 9 |
| DEFER_REDUNDANT | 22 |
| DEFER_DIRECTION_UNCLEAR | 19 |
| DEFER_DATA | 0 |
| DEFER_OPS | 0 |
| DEFER_LEAKAGE_RISK | 0 |
| REJECT_FOR_NOW | 0 |

### Scoring methodology (0-12 scale)

| Dimension | Range | Criteria |
|-----------|-------|----------|
| data_ready | 0-3 | 3 = OHLCV/quote_volume only |
| ops_supported | 0-3 | 3 = current factor_ops, 2 = WQ/a158 formulaic |
| novelty_vs_batch1 | 0-3 | 3 = new family, 1 = same family as Batch-1 |
| risk_control | 0-3 | 3 = clear direction + low leakage, 1 = conditional |

**Decision rules used by server draft:**
- SELECT_NOW: score >= 10, no conditional direction
- Formulaic alpha (WQ/a158): requires >= 11 (higher bar for less interpretable formulas)
- DEFER_REDUNDANT: score 7-9 or formulaic alpha below threshold
- DEFER_DIRECTION_UNCLEAR: conditional expected_direction
- DEFER_DATA: requires data source not currently available

PM review found this rule set insufficient because it allowed high-redundancy candidates into server SELECT_NOW.

---

## C. Server Draft Selected Candidates (18; not final)

The following table is preserved for audit history only. Phase 7I must not implement this full list.

| factor_id | family | score | direction | required_ops | risk_flags |
|-----------|--------|-------|-----------|-------------|------------|
| mom_80h | momentum | 10 | positive | rolling_mean;rolling_std | redundancy=Moderate |
| mom_accel_20h | momentum | 10 | positive | delta;rolling_mean | redundancy=Moderate |
| rev_48h | reversal | 10 | negative | rolling_mean;rolling_std | redundancy=Moderate |
| vol_ma_ratio_5_20 | volume_liquidity | 10 | positive | rolling_mean;rolling_std;zscore | redundancy=Moderate |
| qvol_ma_ratio_5_20 | quote_volume_liquidity | 10 | positive | rolling_mean;rolling_std;zscore | redundancy=Moderate |
| ma_gap_20_80 | trend_ma | 10 | positive | rolling_mean;ema | redundancy=Moderate |
| ema_12_26_gap | technical_indicators | 12 | positive | ema;rolling_mean | NEW_FAMILY |
| rsi_7h | technical_indicators | 11 | negative | rolling_mean;delta | NEW_FAMILY |
| rsi_28h | technical_indicators | 12 | negative | rolling_mean;delta | NEW_FAMILY |
| williams_r_14h | technical_indicators | 11 | negative | rolling_min;rolling_max | NEW_FAMILY |
| wq101_alpha23 | wq101_expansion | 11 | positive | rolling_mean;rolling_std;zscore;signed_power;ts_rank | FORMULAIC |
| downside_vol_20h | realized_skew_kurtosis | 12 | negative | rolling_std;rolling_mean | NEW_FAMILY |
| vol_of_vol_20h | realized_skew_kurtosis | 12 | negative | rolling_std;rolling_mean | NEW_FAMILY |
| ema_gap_12_26 | trend_ma | 10 | positive | ema;rolling_mean | redundancy=Moderate |
| range_breakout_20h | breakout | 10 | positive | rolling_max;rolling_min | redundancy=Moderate |
| range_breakdown_20h | breakout | 10 | negative | rolling_max;rolling_min | redundancy=Moderate |
| breakout_dist_72h | breakout | 10 | positive | rolling_max;rolling_min | redundancy=Moderate |
| breakout_high_20h | breakout | 10 | positive | rolling_max;rolling_min | redundancy=Moderate |

---

## D. Deferred Candidates

### DEFER_REDUNDANT (22)

Formulaic alphas (WQ/a158) scored < 11 threshold due to conditional direction or lower novelty signal:
- **wq101_expansion** (17): alpha01-09, alpha15, alpha18, alpha21, alpha24, alpha26, alpha28, alpha33, alpha34, alpha41, alpha44, alpha45
- **alpha158_expansion** (5): kbdr, kcrd, krs, kurt, ksew

### DEFER_DIRECTION_UNCLEAR (19)

Expected direction = "conditional" — direction mechanism not clear enough from theory:
- **realized_skew_kurtosis** (5): skew_24h, kurt_24h, skew_72h, kurt_72h, upside_vol_20h
- **technical_indicators** (3): stoch_k_14h, cci_20h, adx_14h
- **cross_sectional_normalized** (4): xs_rank_range, xs_rank_mom_20h, xs_rank_bb, xs_rank_rsi
- **intraday_candle** (3): body_ratio_ma_20h, wick_ratio_ma_20h, gap_up_ratio
- **breakout** (1): consolidation_20h
- **volatility** (1): vol_ratio_10_40
- **trend_ma** (1): trend_strength_20h
- **price_position** (1): price_pos_12h

---

## E. Lessons from Batch-1

Phase 7G identified these issues that inform Batch-2 selection:

1. **Direction mismatch**: 16/27 Batch-1 factors had direction mismatch between static and dynamic evaluation. Batch-2 prioritizes factors with clear theoretical direction.
2. **High turnover**: 8/27 Batch-1 factors flagged for high/extreme turnover. Batch-2 avoids short-lookback candle/volume factors.
3. **Redundancy**: 6 redundancy groups found in Batch-1. Batch-2 should prioritize new families and avoid many same-family lookback variants.
4. **Weak diagnostic**: 3/27 Batch-1 factors had weak RankIC. Batch-2 requires stronger rationale.
5. **Dynamic universe not true PIT**: Known limitation carried forward — all evaluations use dynamic_from_current_listed_pool.

---

## F. Required Negative Declarations

- No new factors were implemented.
- No factor registry was modified.
- No factor_ops were modified.
- No factor_values were built.
- No static evaluation was run.
- No dynamic evaluation was run.
- No redundancy analysis was rerun.
- No strategy backtest was run.
- No portfolio simulation was run.
- No Qlib / VectorBT / Backtrader integration was run.
- No Alphalens tear sheet was run.
- No factor status was upgraded to CANDIDATE_REVIEW.
- No alpha claim was made.
- No factor was removed or selected for trading.

---

## G. Phase 7I Readiness

Phase 7I Batch-2 implementation is allowed pending PM review, but only for the 9 factors listed in `phase7h_pm_approved_batch2.csv` with `approved_for_phase7i = YES`.
