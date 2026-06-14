# Phase 7H — PM Review of Batch-2 Selection

> Date: 2026-06-15
>
> Status: PM OVERRIDE APPLIED

---

## A. Review Scope

This document reviews the server-generated Phase 7H Batch-2 selection plan and defines the PM-approved list for Phase 7I implementation.

Inputs reviewed:

- `PHASE_7H_BATCH2_SELECTION_PLAN.md`
- `phase7h_batch2_candidate_selection.csv`
- `phase7h_operator_gap_analysis.csv`
- `phase7g_curated_factor_library_v0_2.csv`
- `phase7g_redundancy_review_queue.csv`

---

## B. Server Output Assessment

The server output is accepted as a candidate inventory and scoring draft, but not accepted as the final Batch-2 selection.

Boundary compliance: PASS

- No new factors were implemented.
- `factor_formula_registry.py` was not modified.
- `factor_ops.py` was not modified.
- No factor_values were built.
- No static/dynamic evaluation was run.
- No backtest or portfolio simulation was run.
- No alpha/status promotion occurred.

Selection quality: NEEDS PM OVERRIDE

Reason: the server selected 18 `SELECT_NOW` candidates, but several were explicitly marked `redundancy_risk_vs_batch1 = HIGH`. This violates the Phase 7H PM principle that Batch-2 should reduce redundancy and prioritize new information structure.

---

## C. Server SELECT_NOW List Is Not Final

The following server-selected candidates are deferred by PM:

| factor_id | PM decision | Reason |
|-----------|-------------|--------|
| mom_80h | DEFER_REDUNDANT | Pure long-lookback momentum; high redundancy vs Batch-1 momentum |
| rev_48h | DEFER_REDUNDANT | Pure reversal lookback; high redundancy vs Batch-1 reversal/momentum |
| vol_ma_ratio_5_20 | DEFER_REDUNDANT | Do not implement both volume and quote-volume MA ratios in the same batch |
| ema_gap_12_26 | DEFER_DUPLICATE | Duplicate of `ema_12_26_gap`; keep only one naming convention |
| range_breakout_20h | DEFER_REDUNDANT | Breakout/price-position family already highly redundant in Batch-1 |
| range_breakdown_20h | DEFER_REDUNDANT | Breakout/price-position family already highly redundant in Batch-1 |
| breakout_dist_72h | DEFER_REDUNDANT | Additional breakout lookback variant; defer until after Batch-2 diagnostics |
| breakout_high_20h | DEFER_DUPLICATE | Formula overlaps with `range_breakout_20h`; defer |
| wq101_alpha23 | DEFER_OPS | WQ `rank(...)` semantics require explicit cross-sectional rank handling before implementation |

---

## D. PM-Approved Batch-2 List for Phase 7I

Only the following 9 factors are approved for Phase 7I implementation:

| factor_id | family | expected_direction | Reason |
|-----------|--------|--------------------|--------|
| ema_12_26_gap | technical_indicators | positive | New technical-indicator family; EMA trend structure not represented in Batch-1 |
| rsi_28h | technical_indicators | negative | Longer-horizon RSI oscillator with clear mean-reversion direction |
| rsi_7h | technical_indicators | negative | Shorter-horizon RSI for controlled horizon contrast with rsi_28h |
| williams_r_14h | technical_indicators | negative | Distinct oscillator using high-low range position |
| downside_vol_20h | realized_skew_kurtosis | negative | New downside-risk structure with clear negative direction |
| vol_of_vol_20h | realized_skew_kurtosis | negative | New second-order volatility structure |
| mom_accel_20h | momentum | positive | Momentum acceleration is less redundant than another pure lookback momentum |
| qvol_ma_ratio_5_20 | quote_volume_liquidity | positive | Smoother quote-volume liquidity variant; choose qvol only, not both volume and quote-volume variants |
| ma_gap_20_80 | trend_ma | positive | One controlled longer-horizon trend extension |

Batch-2 implementation size is intentionally below the earlier 12–18 guideline. Reason: the server's 18-factor list contained too many high-redundancy variants. Quality and novelty are prioritized over batch size.

---

## E. Implementation Guardrails for Phase 7I

Phase 7I may implement only the PM-approved 9 factors above.

Do not implement:

- server-selected candidates not listed in Section D;
- any WQ101 / Alpha158 factor in this batch;
- any extra breakout / price-position lookback variant;
- any extra momentum or reversal pure lookback variant;
- any factor requiring `cross_sectional_rank` unless explicitly approved later.

---

## F. Test Gap Identified

The server's Phase 7H tests checked row counts, legal decisions, status values, and clear direction, but did not check that `SELECT_NOW` excludes high-redundancy candidates.

Future selection tests should include:

- no `SELECT_NOW` candidate with `redundancy_risk_vs_batch1 = HIGH`, unless a PM override file explicitly approves it;
- PM-approved list must be the only source for Phase 7I implementation.

---

## G. Required Negative Declarations

- No new factors were implemented by this PM review.
- No factor registry was modified by this PM review.
- No factor_ops were modified by this PM review.
- No factor_values were built.
- No static evaluation was run.
- No dynamic evaluation was run.
- No redundancy analysis was rerun.
- No strategy backtest was run.
- No portfolio simulation was run.
- No alpha claim was made.
- No factor status was upgraded to CANDIDATE_REVIEW.
- No factor was removed or selected for trading.

---

## H. Phase 7I Readiness

Phase 7I Batch-2 implementation is allowed pending PM review, but only for the 9 factors listed in `phase7h_pm_approved_batch2.csv` with `approved_for_phase7i = YES`.
