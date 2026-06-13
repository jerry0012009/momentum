# Phase 4 — Factor Factory v1 Closeout

> Date: 2026-06-13
>
> Status: COMPLETE

---

## 1. What Was Implemented

### New Modules

| Module | Lines | Purpose |
|--------|-------|---------|
| `scripts/factor_ops.py` | 121 | Pure-function building blocks (delay, delta, rolling_mean, rolling_std, rolling_min, rolling_max, rolling_corr, ts_rank, zscore, signed_power, ema, true_range) |
| `scripts/factor_specs.py` | 31 | FactorSpec dataclass: factor_id, family, required_columns, lookback_window, expected_direction, compute_fn, status, notes |
| `scripts/factor_formula_registry.py` | 188 | REGISTRY list of 11 FactorSpec objects + REGISTRY_BY_ID dict |

### Modified Modules

| Module | Change |
|--------|--------|
| `scripts/build_factor_values.py` | Now iterates REGISTRY instead of hand-coded factor logic. Same output schema, same `--dataset-id` support |

### New Tests

| Test File | Tests | Purpose |
|-----------|-------|---------|
| `tests/unit/test_factor_ops.py` | 20 | delay/delta no-future, rolling_corr, ts_rank, zscore, true_range, ema |
| `tests/unit/test_factor_factory_registry.py` | 131 | Registry completeness (11 factors), FactorSpec fields, compute_fn validity, no-future-leak, metadata hardening |

### Test Results

- **194 factor-related tests pass** (63 pre-existing + 131 new)
- 2 pre-existing trendline tests still fail (unrelated)

## 2. Registered Factors (11)

| factor_id | family | lookback | expected_direction | status |
|-----------|--------|----------|--------------------|--------|
| mom_20h | momentum | 20 | positive | DIAGNOSTIC_PROBE |
| reversal_5h | momentum | 5 | negative | DIAGNOSTIC_PROBE |
| volatility_20h | volatility | 21 | negative | DIAGNOSTIC_PROBE |
| rsi_14h | technical | 14 | negative | DIAGNOSTIC_PROBE |
| bb_zscore_20h | technical | 20 | negative | DIAGNOSTIC_PROBE |
| wq101_alpha101 | wq101 | 1 | conditional | DIAGNOSTIC_PROBE |
| wq101_alpha12 | wq101 | 2 | conditional | DIAGNOSTIC_PROBE |
| wq101_alpha53 | wq101 | 10 | conditional | DIAGNOSTIC_PROBE |
| q158_high_low_range | alpha158 | 1 | conditional | DIAGNOSTIC_PROBE |
| tech_macd | technical | 26 | positive | DIAGNOSTIC_PROBE |
| tech_atr | technical | 15 | conditional | DIAGNOSTIC_PROBE |

## 3. What Did NOT Change

- Output schema: `timestamp, symbol, factor_name, factor_value, known_at, source_timeframe, computed_at`
- `--dataset-id` support (180d and long_v1)
- `evaluate_factors.py` — unchanged
- `build_labels.py` — unchanged
- `crypto_factor_functions.py` — kept for reference (legacy)
- No new factors added
- No Qlib / Alphalens / VectorBT integration

## 4. Metadata Fixes Applied

| Fix | Before | After | Rationale |
|-----|--------|-------|-----------|
| `wq101_alpha101` direction | negative | conditional | Must not be fitted from evaluation results (post-hoc avoidance) |
| `wq101_alpha12` lookback | 1 | 2 | delta(1) needs t and t-1 |
| `wq101_alpha53` lookback | 9 | 10 | diff(9) needs t and t-9 |
| `true_range` first row | high-low (NaN skipped) | NaN (strict) | prev_close unavailable for first bar |
| `FactorSpec.lookback_window` docstring | "max bars of history" | "bars_required_including_current" | Clarified definition |
| `FactorSpec.expected_direction` docstring | no constraint | "must not be fitted from evaluation results" | Anti post-hoc rule |

## 4. Is Batch 2 Ready?

**Yes.** The registry pattern makes adding new factors trivial:

1. Write compute function in `factor_formula_registry.py` (or compose from `factor_ops`)
2. Add FactorSpec to REGISTRY
3. Run `build_factor_values.py` → `evaluate_factors.py`

No changes needed to build/eval scripts. The registry auto-discovers new factors.

## 5. Design Doc

See `docs/FACTOR_FACTORY_V1_DESIGN.md` for full architecture rationale.
