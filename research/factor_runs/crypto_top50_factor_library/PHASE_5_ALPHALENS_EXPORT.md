# Phase 5 — Alphalens-compatible Export Closeout

> Date: 2026-06-13
>
> Status: COMPLETE — READY FOR REVIEW

---

## 1. Goal

Build an Alphalens-compatible export layer so our factor data can be loaded into Alphalens (or similar tools) for cross-check / tear sheet generation, **without** replacing our evaluation kernel.

## 2. Files Generated

### New Scripts

| File | Purpose |
|------|---------|
| `scripts/export_alphalens_factor_data.py` | CLI tool: reads bars + factor_values + labels → exports Alphalens-compatible parquet |

### New Tests

| File | Tests |
|------|-------|
| `tests/unit/test_alphalens_export.py` | 22 tests (9 synthetic + 13 on exported files) |

### New Documentation

| File | Purpose |
|------|---------|
| `docs/ALPHALENS_COMPATIBILITY_DESIGN.md` | Design doc: goals, schema mapping, limitations, anti-patterns |

### Exported Data

```
research/factor_runs/crypto_top50_factor_library/alphalens_exports/
└── crypto_top50_usdt_perp_1h_long_v1/
    ├── mom_20h/
    │   ├── factor_series.parquet        (713,572 rows)
    │   ├── prices_wide.parquet          (17,533 × 50)
    │   ├── forward_returns_long.parquet (713,572 rows)
    │   ├── alphalens_factor_data.parquet (713,572 rows)
    │   └── export_manifest.json
    └── wq101_alpha53/
        ├── factor_series.parquet        (713,572 rows)
        ├── prices_wide.parquet          (17,533 × 50)
        ├── forward_returns_long.parquet (713,572 rows)
        ├── alphalens_factor_data.parquet (713,572 rows)
        └── export_manifest.json
```

## 3. Factors Exported

| factor_id | dataset_id | rows | symbols |
|-----------|-----------|------|---------|
| mom_20h | crypto_top50_usdt_perp_1h_long_v1 | 713,572 | 50 |
| wq101_alpha53 | crypto_top50_usdt_perp_1h_long_v1 | 713,572 | 50 |

## 4. Test Results

- **216 factor-related tests pass** (63 pre-existing + 131 metadata + 22 export)
- 2 pre-existing trendline tests still fail (unrelated)

## 5. Limitations

- Alphalens package is **not** required (exports are plain parquet)
- Quantile labels are computed per-timestamp cross-sectionally (our existing logic)
- No shift(-k) in exporter — forward returns come from pre-computed labels
- Our IC/RankIC/spread metrics are authoritative; Alphalens tear sheets are supplementary

## 6. What Did NOT Change

- `evaluate_factors.py` — unchanged
- `build_factor_values.py` — unchanged
- `build_labels.py` — unchanged
- Factor statuses — unchanged (no upgrade from Alphalens output)
- No new factors added
- No Alphalens package dependency added

## 7. Is Phase 5 Complete?

**Yes.** All deliverables implemented and tested.

## 8. Is Phase 6 Allowed?

**Yes.** Per RESEARCH_PHASE_CONSTITUTION.md, Phase 6 (Dynamic Universe & Survivorship Control) is next.

Phase 6 scope:
- Point-in-time TopN universe
- Avoid survivorship bias
- Rerun selected factor diagnostics on dynamic universe

Phase 6 is **not** triggered automatically — requires human approval.
