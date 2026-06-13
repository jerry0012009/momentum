# Phase 6D-QA — Membership-Aware Bars Coverage Audit

> Date: 2026-06-13
>
> Status: COMPLETE — LABELS BUILD ALLOWED

---

## 1. Goal

Evaluate bars coverage only during months when each symbol is actually selected by the dynamic universe, rather than across the full requested date range.

## 2. Problem with Global Missing Rate

The previous `symbol_availability.parquet` computed missing_bar_rate across the entire requested date range (2024-06-13 → 2026-06-13). For symbols listed mid-period (e.g., 2025-01), this produced artificially high missing rates (~50%+), even though their data coverage during selected months was perfect.

## 3. Membership-Aware Coverage Results

### Per-symbol aggregation

| Metric | Value |
|--------|-------|
| Symbols with membership data | 266 |
| Median member_missing_bar_rate | **0.0%** |
| Symbols with member_missing_bar_rate > 5% | 0 |
| Symbols with zero member bars | 0 |

### Per-symbol-month

| Metric | Value |
|--------|-------|
| Selected symbol-months | 1,250 |
| Symbol-months with zero bars | 0 |
| Symbol-months with >5% missing | 0 |

### Global vs Membership comparison

| Metric | Global | Membership-aware |
|--------|--------|-----------------|
| Symbols with >5% missing | 158 | 0 |
| Median missing_bar_rate | 26.1% | 0.0% |

The high global missing rate is entirely explained by pre-listing months (symbols not yet listed on Binance). During months when each symbol is selected by the dynamic universe, coverage is excellent.

## 4. Actual Data Range

| Field | Value |
|-------|-------|
| Requested start | 2024-06-13 |
| Requested end | 2026-06-13 |
| Actual data start | 2024-06-01 01:00:00 UTC |
| Actual data end | 2026-06-13 00:00:00 UTC |

Note: Actual start is slightly before requested start because June 2024 monthly zip includes data from June 1. This is acceptable — the extra bars are not harmful.

## 5. QA Decision

**Decision: ALLOWED**

- Zero symbol-months with zero bars
- Zero symbol-months with >5% missing
- All 266 symbols have complete coverage during their selected months
- Phase 6E (labels build) is allowed to proceed

## 6. New Outputs

| File | Description |
|------|-------------|
| `membership_availability.parquet` | Per-symbol membership-aware coverage |
| `membership_monthly_coverage.parquet` | Per-symbol-month coverage detail |
| `qa_conclusion.json` | Machine-readable QA decision |

## 7. Manifest Changes

Added to `manifest.json`:
- `requested_start` / `requested_end` — CLI arguments
- `actual_data_start` / `actual_data_end` — derived from bars_1h.parquet
- `universe_first_asof_time` / `universe_last_asof_time` — from universe snapshots

## 8. Tests

22/22 pass:
- 15 existing tests (kline parsing, schema, download handling)
- 7 new membership-aware tests (full month, partial month, high-global-low-member, zero bars blocks, full coverage allows, schema checks)

## 9. Whether Phase 6E Is Allowed

**Yes — Phase 6E labels build is allowed.**
