# Direction Semantics Audit Summary

**Phase:** 12D-H12-A  
**Date:** 2026-06-20  
**Status:** AUDIT ONLY — no metadata modified, no signal modified

---

## What Was Checked

- Factor formula sign vs FactorSpec expected_direction vs raw/adjusted IC
- Phase 6H historical direction mismatch records
- Phase 10A-R signal-level RankIC/spread sign inconsistency diagnostics
- Current signal construction transforms (NEGATIVE, OVERLAY, LIQUIDITY_GATE)
- 53 registered factors; 10 active signal factors

## Historical Assets

- **Phase 6H** (PHASE_6H_STATIC_DYNAMIC_COMPARISON.md): Found and read.
  - 4 direction mismatch: mom_20h, reversal_5h, tech_macd, wq101_alpha101
  - 3 direction consistent: volatility_20h, rsi_14h, bb_zscore_20h
  - 4 conditional: q158_high_low_range, wq101_alpha53, tech_atr, wq101_alpha12
- **Phase 10A-R** (6 CSVs + script + test): All found and read.
  - All signal×horizon show RankIC positive / spread negative
  - Root cause: non_monotonic_tail_behavior (bucket 0 extreme positive returns)
  - Inversion resolves spread but flips RankIC negative
  - Phase 10A-R was diagnostic only, did NOT modify signal

## Current Catalog Findings

- **6 MISSING_INPUT_DATA**: taker/funding factors (raw bars lack columns)
- **10 ACTIVE_IN_SIGNAL**: all have IC across 4 horizons
- **27 CANDIDATE**: non-signal factors with computed IC
- **10 DIAGNOSTIC_ONLY**: conditional direction factors

## Key Findings

### A. reversal_5h — Possible Double Inversion

Formula: `-(close / close_5h_ago - 1)` — already negated in formula.
expected_direction: `negative` — but formula already expresses reversal hypothesis.
Raw IC 1h: **+0.028** (positive) — higher factor_value = past losers outperform.
Adjusted IC: `adj = -raw` (because expected=negative) → **-0.028**.
**Risk**: If expected_direction should be `positive` (formula already inverted), the
adjustment double-inverts, flipping the IC sign. This is a **POSSIBLE_DOUBLE_INVERSION**.
**Verdict**: Needs H12-B review. Most likely expected_direction should be `positive`.

### B. mom_20h — Historical Direction Mismatch

Formula: `close / close_20h_ago - 1` — standard momentum.
expected_direction: `positive`.
Raw IC 1h: **-0.023** (negative) — contradicts expected.
Phase 6H recorded this mismatch. Empirical sign is stable across static/dynamic.
**Verdict**: Not a bug — this is a factor that empirically behaves as reversal in
this market/period. Keep as DIAGNOSTIC_PROBE. Do NOT change expected_direction
without careful study (could be regime-dependent). No H12-B action needed.

### C. Conditional Factors in Signal

4 factors with conditional expected_direction are used in signal:
- **xs_rank_vol**: Used as liquidity gate (rank percentile, no direction assumption). Justified.
- **range_1h, range_4h**: Used in OVERLAY with `* -1` transform (mean-reversion hypothesis). Justified.
- **price_pos_24h**: Used in OVERLAY with `* -1` transform. Justified.

Signal construction explicitly handles direction via transforms. The `conditional`
expected_direction at factor level does NOT create a signal bug, because signal
construction applies its own direction policy.

### D. Phase 10A-R vs H12-A Distinction

- Phase 10A-R: Signal-level RankIC/spread sign inconsistency → bucket 0 tail behavior.
  This is a **signal-level** issue about non-monotonic returns, not a factor direction issue.
- H12-A: Factor-level direction semantics (formula sign vs expected_direction vs IC).
  This is a **metadata** issue about whether FactorSpec correctly represents the factor.
- They are related but distinct. H12-A does NOT re-analyze bucket tails.

## Signal Transform Summary

| Factor | Expected Dir | Signal Role | Transform | Match? |
|--------|-------------|-------------|-----------|--------|
| vol_5h | negative | risk_pressure | *-1 | YES |
| vol_40h | negative | risk_pressure | *-1 | YES |
| downside_vol_20h | negative | risk_pressure | *-1 | YES |
| vol_of_vol_20h | negative | risk_pressure | *-1 | YES |
| rsi_7h | negative | oscillator | *-1 | YES |
| rsi_28h | negative | oscillator | *-1 | YES |
| xs_rank_vol | conditional | liquidity_gate | rank_pct | CONDITIONAL |
| range_1h | conditional | overlay | *-1 | CONDITIONAL |
| range_4h | conditional | overlay | *-1 | CONDITIONAL |
| price_pos_24h | conditional | overlay | *-1 | CONDITIONAL |

## Repair Recommendation (H12-B)

**Recommended for H12-B metadata repair:**
- reversal_5h: Change expected_direction from `negative` to `positive`

**Not recommended for change:**
- mom_20h: Keep as DIAGNOSTIC_PROBE; empirical mismatch is regime-dependent
- Conditional signal factors: Signal transforms are justified; no metadata change needed

**No signal modification recommended.**
