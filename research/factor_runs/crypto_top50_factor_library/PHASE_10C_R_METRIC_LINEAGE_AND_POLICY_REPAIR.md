# Phase 10C-R Closeout — Metric Lineage & Direction Policy Repair

> Date: 2026-06-15
> Previous: Phase 10C COMPLETE
> Scope: Metric lineage reconciliation, direction policy repair

---

## Status

Phase 10C-R: COMPLETE, pending PM review.
Phase 10D: NOT STARTED (requires PM approval).
Phase 11: NOT STARTED. Phase 12: NOT STARTED. Phase 13: NOT STARTED.

---

## 1. Root Cause of Inconsistency

Phase 10C horizon direction policy incorrectly labeled some 24h/72h rows as `NEGATIVE` for rankic_direction.

**Canonical Phase 10A RankIC is POSITIVE for ALL 3 signals × ALL 4 horizons** (range: 0.025 to 0.042, all t-stats > 14).

The error originated from conflating Phase 10A-R's *diagnostic* RankIC computation (which uses different NaN handling and yields different values) with the canonical Phase 10A RankIC summary. Phase 10A-R's per-timestamp RankIC for 24h/72h was slightly negative due to stricter NaN filtering, but the canonical Phase 10A RankIC remains positive.

**No metric value was changed.** The repair is purely in labeling and documentation.

---

## 2. Metric Lineage

All metrics are now explicitly mapped in `phase10c_r_metric_lineage.csv` with:
- Source file (which CSV/parquet)
- Source phase (10A, 10A-R, 10B)
- Direction label
- Whether used for policy

Key distinction:
- **Canonical RankIC** (from `phase10a_signal_rankic_summary.csv`): POSITIVE for all 12 combos
- **10A-R diagnostic RankIC** (from `phase10a_r_inverted_signal_diagnostic.csv`): different values due to different NaN handling; used for inversion diagnostic only
- **Robust spreads** (from `phase10b_robust_spread_addendum.csv`): median, winsorized, tail-trim

---

## 3. Repaired Horizon Direction Policy

All 12 rows in `phase10c_r_horizon_direction_policy_repaired.csv` now have:
- `original_rankic_direction = POSITIVE` (matching canonical Phase 10A)
- Correct separation of original vs inverted metrics
- `phase10d_inversion_allowed = TRUE` for 24h/72h (inversion review still valid)
- `phase10d_inversion_allowed = FALSE` for 1h/4h (original direction preferred)
- All rows `final_policy_status = REVIEW_PHASE10D` (no pre-selection)

---

## 4. Repaired Phase 10D Protocol

48 variant evaluations defined in `phase10c_r_phase10d_protocol_repaired.csv`:
- 3 signals × 4 horizons × 4 variants (original/inverted × no_guard/bucket0_guard)
- 10 required metrics per evaluation
- Priority 1: original variants (baseline + guard)
- Priority 2: inverted variants for 24h/72h (inversion review)
- Priority 3: inverted variants for 1h/4h (diagnostic)

Pass criteria: RankIC > 0 AND median_spread > 0.
Mean spread is secondary, not primary.
No cost/slippage/capacity. No weight optimization. No alpha claim.

---

## 5. Phase 10C Language Repair

Phase 10C closeout language corrected:
- "the evaluation framework was wrong" → "mean spread alone is insufficient under nonlinear tail behavior"
- "the correct response is NOT to flip the signal" → "Phase 10D must evaluate tail-aware variants before Phase 11"
- No claim that signal construction is proven sound
- No claim that bucket 0 guard will solve the problem
- Only claim: signal has evidence of median-cross-section information; tail behavior requires modified evaluation protocol

---

## 6. Negative Declarations

- No metric value was changed.
- No signal v1 was implemented.
- No backtest was run.
- No variant was promoted.
- No direction was pre-selected.
- No Phase 10A/10A-R/10B results were modified.
- No alpha claim. No cost/slippage/capacity.
- Phase 11/12/13 NOT STARTED.
