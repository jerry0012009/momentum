# Phase 11A Closeout — Cost / Slippage / Turnover / Capacity Diagnostic v0

> Date: 2026-06-15
> Previous: Phase 10D-R COMPLETE
> Scope: Diagnostic cost evaluation of 9 eligible variants

---

## Status

Phase 11A: COMPLETE, pending PM review.

---

## 1. Which Phase 10D-R variants survive simple cost assumptions?

**1/9 survives:**
- `signal_v0_core_only__1h__original_no_guard`: COST_SENSITIVE_CANDIDATE (survives low cost: fee≤2bps + slip≤5bps)

**8/9 FAILS_COST_DIAGNOSTIC:**
- All 6 bucket0_guard variants fail (1h and 4h)
- pm_full and family_balanced no_guard variants fail

## 2. Does bucket0_guard remain useful after cost?

**No.** The bucket0_guard improves gross median spread (from +0.015% to +0.015% for core_only 1h), but increases turnover significantly:
- no_guard 1h: median turnover 18.8%
- bucket0_guard 1h: median turnover 28.6%

The higher turnover erases the spread improvement. The guard creates more position changes than the spread improvement justifies.

## 3. Is 1h too turnover-heavy?

**For bucket0_guard variants, yes.** 28.6% median turnover per rebalance at 1h frequency generates enough cost to wipe out the small median spread.

**For no_guard variants, the turnover is manageable** (18.8% median), but the spread is thin.

## 4. Does 4h become more attractive after turnover adjustment?

**No.** Counter-intuitively, 4h has HIGHER per-rebalance turnover (median 50% vs 28.6% for 1h bucket0_guard). This is because 4 hours of signal evolution accumulates between rebalances, causing larger position changes. The fewer rebalances don't compensate for the larger per-rebalance turnover.

## 5. Does pm_full_structured outperform core_only after costs?

**No.** core_only consistently has the highest gross median spread:
- core_only 1h no_guard: +0.0153% gross median
- pm_full 1h no_guard: +0.0102% gross median
- family_balanced 1h no_guard: +0.0042% gross median

After costs, core_only remains the only variant that survives low-cost scenarios.

## 6. Are liquidity / capacity data sufficient?

**No.** Kline volume data files are empty (0 rows). Capacity analysis is not possible. Phase 11B must add canonical liquidity data before true capacity analysis.

## 7. Is Phase 11B needed before Phase 12?

**Yes.** Without volume data, capacity cannot be assessed. Even if a variant survives cost diagnostic, we cannot determine if the strategy can be executed at meaningful size.

## 8. Is any variant eligible for Phase 12 paper signal generation?

**Conditionally, yes** — but only `signal_v0_core_only__1h__original_no_guard`, and only under low-cost assumptions (fee≤2bps + slip≤5bps). Under conservative assumptions (fee=5bps + slip=10bps), this variant also fails.

**Phase 12 remains blocked** pending:
1. PM decision on whether low-cost survival is sufficient
2. Phase 11B capacity analysis (requires volume data)

---

## Turnover Summary

| Variant | Median Turnover | P95 Turnover | Convention |
|---------|----------------|-------------|------------|
| core_only 1h guard | 28.6% | 50.0% | one-way |
| pm_full 1h guard | 28.6% | 50.0% | one-way |
| family_balanced 1h guard | 30.0% | 57.1% | one-way |
| core_only 4h guard | 50.0% | 70.0% | one-way |
| pm_full 4h guard | 50.0% | 70.0% | one-way |
| family_balanced 4h guard | 50.0% | 75.0% | one-way |
| core_only 1h no_guard | 18.8% | 35.7% | one-way |
| pm_full 1h no_guard | 18.8% | 35.7% | one-way |
| family_balanced 1h no_guard | 20.0% | 41.7% | one-way |

## Cost Scenario Grid Summary

12 scenarios per variant (3 fee × 4 slippage levels):
- fee_bps: 2, 5, 10
- slippage_bps: 1, 5, 10, 25
- total_cost_bps: 3, 6, 7, 10, 11, 15, 20, 30, 12, 15, 25, 35

## Negative Declarations

- No final model selected
- No alpha claim
- No paper execution
- No live execution
- No deployment
- No weight optimization
- Phase 12 NOT STARTED
- Phase 13 NOT STARTED

---

## Artifacts

| File | Rows | Description |
|------|------|-------------|
| `phase11a_variant_cost_summary.csv` | 9 | Per-variant summary |
| `phase11a_turnover_summary.csv` | 9 | Turnover metrics |
| `phase11a_cost_scenario_grid.csv` | 108 | 9 variants × 12 scenarios |
| `phase11a_net_spread_summary.csv` | 9 | Net spread after costs |
| `phase11a_capacity_summary.csv` | 9 | All NEEDS_LIQUIDITY_DATA |
| `phase11a_liquidity_coverage_audit.csv` | 1 | DATA_MISSING |
| `phase11a_quality_checks.csv` | 11 | All PASS |
| `PHASE_11A_COST_SLIPPAGE_CAPACITY_V0.md` | — | This closeout |
| `scripts/run_phase11a_cost_slippage_capacity.py` | — | Script |
| `tests/unit/test_phase11a_cost_slippage_capacity.py` | — | Tests |
