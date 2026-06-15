# Phase 11B Closeout — Canonical Liquidity Data & Capacity Analysis

> Date: 2026-06-15
> Previous: Phase 11A COMPLETE
> Scope: Rebuild liquidity data and evaluate capacity for 4 variants

---

## Status

Phase 11B: COMPLETE, pending PM review.

---

## 1. Was canonical liquidity data found or rebuilt?

**Rebuilt successfully.** Kline 1h files were found in `data/cache/dynamic_universe_build/.../kline_1h/`. Previous Phase 11A read them as empty because the glob pattern was wrong (matched 0-row files for delisted symbols like 0GUSDT). Phase 11B correctly filters for non-empty files and covers all 43 panel symbols.

- Panel: 634,888 rows, 43 symbols
- Columns: timestamp, symbol, close, volume, quote_volume, taker_base, taker_quote, trade_count, notional_volume
- Timestamp range overlaps with Phase 9B/10D signal panel
- Zero duplicate timestamp-symbol pairs

## 2. Is capacity analysis now possible?

**Yes.** 43/43 panel symbols have volume data. Notional volume = quote_volume (USD-denominated).

## 3. What is the realistic notional capacity for core_only 1h no_guard?

At 1% participation rate:

| Notional | Median Capacity | P10 Capacity | P5 Capacity | Min Capacity |
|----------|----------------|-------------|-------------|-------------|
| Per timestamp | $660,490 | — | — | — |

This means a $10k portfolio can be executed at 1% participation without capacity constraints. A $100k portfolio also fits under most scenarios. A $500k+ portfolio would need lower participation rates.

## 4. Does the candidate survive cost + capacity assumptions?

**Only core_only 1h no_guard survives** as COST_CAPACITY_SENSITIVE:
- Survives low cost (fee=2bps + slip=5bps) + $10k notional @ 1% participation
- Does NOT survive mid cost (fee=5bps + slip=10bps) + $10k notional
- Does NOT survive $100k notional at mid cost

The other 3 variants all fail because their net spread is negative under cost assumptions (they have lower gross spread than core_only).

## 5. Is it only viable at tiny size?

**No — capacity is not the bottleneck.** Median capacity at 1% participation is $660k. The bottleneck is cost, not capacity:
- At fee=2bps + slip=5bps: net spread is slightly positive
- At fee=5bps + slip=10bps: net spread turns negative

The strategy can handle $10k–$100k portfolios from a capacity perspective, but the gross spread (+0.015%) is too thin to absorb typical trading costs.

## 6. Is Phase 12 paper signal generation allowed?

**PM decision required.** Two paths:

**Path A — Proceed to Phase 12 with core_only 1h no_guard:**
- Only viable under low-cost assumptions
- Requires PM acceptance that real execution costs will be ≤ 7bps total
- Capacity is sufficient ($660k median @ 1%)

**Path B — Return to signal design (Phase 9/10 redesign):**
- Current signal has too-thin spread (+0.015% gross median)
- Need higher-spread signal that survives mid-cost scenarios
- Consider: longer horizons, fewer rebalances, different signal construction

## 7. Should the project return to Phase 9/10 signal redesign?

**Likely yes**, unless PM accepts low-cost-only viability. The fundamental issue is:
- Gross median spread: +0.015% (15 bps)
- Conservative cost: 15 bps (fee=5 + slip=10)
- Cost drag: ~50% of gross spread
- Need either: lower costs (exchange rebates, better execution) or higher spread (different signal)

## Capacity by Variant (1% participation)

| Variant | Median Cap | Status |
|---------|-----------|--------|
| core_only 1h no_guard | $660,490 | COST_CAPACITY_SENSITIVE |
| core_only 1h guard | $457,356 | RETURN_TO_SIGNAL_DESIGN |
| pm_full 1h no_guard | $578,435 | RETURN_TO_SIGNAL_DESIGN |
| family_balanced 1h no_guard | $587,650 | RETURN_TO_SIGNAL_DESIGN |

## Bottleneck Symbols

The lowest-volume symbols in the cross-section vary by variant and timestamp. PAXGUSDT and XMRUSDT are common bottleneck symbols due to lower trading volume on some exchanges.

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
| `phase11b_liquidity_data_inventory.csv` | 43 | Per-symbol volume data status |
| `phase11b_canonical_liquidity_panel.parquet` | 634,888 | Rebuilt liquidity panel |
| `phase11b_liquidity_data_quality.csv` | 17 | Data quality metrics |
| `phase11b_capacity_summary.csv` | 4 | Per-variant capacity summary |
| `phase11b_capacity_by_variant.csv` | 20 | Capacity × participation rate |
| `phase11b_bottleneck_symbols.csv` | 4 | Bottleneck symbols per variant |
| `phase11b_cost_capacity_matrix.csv` | 1200 | Cost × capacity combined grid |
| `phase11b_pm_decision_matrix.csv` | 4 | PM decision statuses |
| `phase11b_quality_checks.csv` | 12 | All PASS |
| `PHASE_11B_LIQUIDITY_CAPACITY_DIAGNOSTIC.md` | — | This closeout |
| `scripts/run_phase11b_liquidity_capacity.py` | — | Script |
| `tests/unit/test_phase11b_liquidity_capacity.py` | — | Tests |
