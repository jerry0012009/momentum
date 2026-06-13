# Phase 4 — Factor Factory v1 Closeout

> Date: 2026-06-13
>
> Status: COMPLETE

---

## 1. What Was Implemented

### New Modules

| Module | Lines | Purpose |
|--------|-------|---------|
| `scripts/factor_ops.py` | 114 | Pure-function building blocks (delay, delta, rolling_mean, rolling_std, rolling_min, rolling_max, rolling_corr, ts_rank, zscore, signed_power, ema, true_range) |
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
| `tests/unit/test_factor_factory_registry.py` | 104 | Registry completeness (11 factors), FactorSpec fields, compute_fn validity, no-future-leak |

### Test Results

- **187 factor-related tests pass** (63 pre-existing + 124 new)
- 2 pre-existing trendline tests still fail (unrelated)

## 2. Registered Factors (11)

| factor_id | family | lookback | expected_direction | status |
|-----------|--------|----------|--------------------|--------|
| mom_20h | momentum | 20 | positive | DIAGNOSTIC_PROBE |
| reversal_5h | momentum | 5 | negative | DIAGNOSTIC_PROBE |
| volatility_20h | volatility | 21 | negative | DIAGNOSTIC_PROBE |
| rsi_14h | technical | 14 | negative | DIAGNOSTIC_PROBE |
| bb_zscore_20h | technical | 20 | negative | DIAGNOSTIC_PROBE |
| wq101_alpha101 | wq101 | 1 | negative | DIAGNOSTIC_PROBE |
| wq101_alpha12 | wq101 | 1 | conditional | DIAGNOSTIC_PROBE |
| wq101_alpha53 | wq101 | 9 | conditional | DIAGNOSTIC_PROBE |
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

## 4. Is Batch 2 Ready?

**Yes.** The registry pattern makes adding new factors trivial:

1. Write compute function in `factor_formula_registry.py` (or compose from `factor_ops`)
2. Add FactorSpec to REGISTRY
3. Run `build_factor_values.py` → `evaluate_factors.py`

No changes needed to build/eval scripts. The registry auto-discovers new factors.

## 5. Design Doc

See `docs/FACTOR_FACTORY_V1_DESIGN.md` for full architecture rationale.
