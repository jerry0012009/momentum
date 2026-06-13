# Phase 2E1-A Closeout — Batch 1 Factor Implementation

> Date: 2026-06-13
>
> Status: COMPLETE
>
> Previous: Phase 2E0 COMPLETE, Spec Correction COMPLETE

---

## 1. Implemented Functions

**File:** `scripts/crypto_factor_functions.py` (new module, 100 lines)

| Function | Source | Lookback | Warmup NaN |
|----------|--------|----------|------------|
| `compute_wq101_alpha101` | WQ101 Alpha#101 | 1 bar | None |
| `compute_wq101_alpha12` | WQ101 Alpha#12 | 2 bars | 1 bar |
| `compute_wq101_alpha53` | WQ101 Alpha#53 | 10 bars | 9 bars |
| `compute_q158_high_low_range` | Alpha158 | 1 bar | None |
| `compute_tech_macd` | MACD | 35 bars | EMA warmup (~52 bars for stability) |
| `compute_tech_atr` | ATR | 15 bars | 14 bars |

All functions:
- Accept single-symbol DataFrame, return pd.Series with same index
- Use only current and past data (no shift(-k))
- Handle NaN warmup correctly
- Do not read labels or future returns

## 2. Integration

**Modified:** `scripts/build_factor_values.py`

- Imports functions from `scripts/crypto_factor_functions.py`
- `BATCH1` dict maps factor_id → compute function
- `calc_group()` now computes batch1 factors per-symbol
- `main()` writes all factors (V0 + batch1) to `data/features/`

## 3. Test Files

**New:** `tests/unit/test_crypto_factor_batch1.py` — 30 tests

| Test Class | Tests | Coverage |
|------------|-------|----------|
| TestAlpha101 | 5 | formula, no-warmup, index, no-future-leak, cross-symbol |
| TestAlpha12 | 4 | formula, first-row-NaN, index, cross-symbol |
| TestAlpha53 | 3 | warmup-NaN, index, cross-symbol |
| TestHighLowRange | 4 | formula, no-warmup, non-negative, cross-symbol |
| TestMACD | 5 | constant=0, rising>0, index, no-future-leak, cross-symbol |
| TestATR | 5 | warmup-NaN, non-negative, constant, index, cross-symbol |
| TestSymbolGrouping | 4 | diff-no-bleed, rolling-no-bleed, ema-no-bleed, raw-bleeds |

## 4. Test Results

```
tests/unit/test_crypto_factor_batch1.py     30 passed
tests/unit/test_crypto_factor_values.py      8 passed
tests/unit/test_crypto_labels.py             9 passed
tests/unit/test_crypto_factor_eval_smoke.py 16 passed
─────────────────────────────────────────────────────
Total                                        63 passed
```

## 5. Key Design Decisions

1. **Option B chosen:** Separate module `crypto_factor_functions.py` rather than extending `build_factor_values.py` — cleaner, more testable, lower coupling.

2. **`_group_apply` helper in tests:** Functions expect per-symbol input. Tests use `_group_apply(df, func)` to simulate how `build_factor_values.py` calls them via `groupby("symbol")`.

3. **`test_raw_combined_bleeds` included:** Deliberately proves that calling functions on a combined DataFrame without groupby DOES bleed — documenting why the caller must group.

4. **EMA uses `adjust=False`:** Matches TA-Lib convention for EMA.

5. **ATR uses SMA (not Wilder's smoothing):** Simpler implementation. Documented in spec; can switch to Wilder's later if needed.

## 6. Known Limitations

- **MACD EMA warmup:** EMA has no exact warmup cutoff (unlike rolling). First ~52 bars are technically unstable but not NaN. This is standard EMA behavior.
- **ATR uses SMA:** Not Wilder's smoothing. Difference is minor for 14-bar window.
- **No real-data test:** All tests use synthetic data. Real-data validation will happen in Phase 2E1-B.

## 7. What's Next

**Phase 2E1-B: NOT ALLOWED YET** (requires human approval)

Phase 2E1-B would:
1. Run `python scripts/build_factor_values.py` to generate batch1 factor_values.parquet
2. Run `python scripts/evaluate_factors.py` to compute IC, RankIC, spread metrics
3. Write evaluation results and closeout report
4. Recommend DIAGNOSTIC_PROBE status for factors that pass evaluation criteria

**This implementation does NOT:**
- Run evaluation
- Generate IC / RankIC / spread
- Upgrade any factor status
- Run full pipeline
