# Phase 7C-A — Dynamic Evaluation Adapter Hardening

> Date: 2026-06-14
>
> Status: COMPLETE

---

## 1. What Was Modified

| File | Change |
|------|--------|
| `scripts/build_factor_values.py` | Added `--factor-ids`, `--candidate-csv`, `--status` args; added `load_selected_factor_ids()`, `validate_factor_ids()`; `calc_group()` now accepts optional factor subset |
| `scripts/evaluate_factors_dynamic_universe.py` | Added `--factor-ids`, `--candidate-csv`, `--status` args; added `load_candidate_directions()`; direction lookup: candidate CSV → old catalog → fallback positive (with warning); fail-fast on missing factor_values / count / direction in explicit mode |
| `tests/unit/test_phase7c_dynamic_adapter.py` | NEW: 21 tests covering loading, directions, subset filtering, consistency, fail-fast |

---

## 2. Factor Subset Support

Both scripts support:

```bash
# Build/evaluate only 27 selected_for_7B factors
--candidate-csv research/factor_runs/crypto_top50_factor_library/factor_mining_candidates_v0_1.csv
--status selected_for_7B

# Or explicit list
--factor-ids mom_5h,mom_10h,...
```

Default behavior (no args) unchanged: build/evaluate all REGISTRY / auto-discovered factors.

---

## 3. Fail-Fast Guarantees (New)

When explicit `--factor-ids` or `--candidate-csv` is used:

1. **Missing factor_values → FileNotFoundError.** If any requested factor lacks `data/features/<dataset_id>/<factor_id>/factor_values.parquet`, evaluation raises immediately. No silent skip.

2. **Wrong count → ValueError.** When `--candidate-csv --status selected_for_7B` is used, exactly 27 factors must be resolved. Otherwise raises `ValueError`.

3. **Fallback positive → ValueError.** If any requested factor has no `expected_direction` in candidate CSV or catalog, evaluation raises immediately. No silent fallback to positive.

These guards only apply in explicit/candidate mode. Auto-discover mode (no args) retains the original lenient behavior.

---

## 4. expected_direction Source

Priority order:

1. **candidate CSV** (`factor_mining_candidates_v0_1.csv`) — primary for Phase 7C
2. **old catalog** (`factor_catalog_v0_1.csv`) — fallback for legacy factors
3. **positive** — last resort, raises error in explicit mode

For the 27 `selected_for_7B` factors, **all 27 have explicit direction in candidate CSV** — zero fallback to positive.

---

## 5. Cross-Sectional Rank Preserved

`apply_cross_sectional_postprocess()` still called after concat in `build_factor_values.py`.
Works correctly when building a subset.

---

## 6. Tests

```
73 passed in 0.91s
```

- `test_phase7c_dynamic_adapter.py`: 21/21 pass
- `test_crypto_factor_batch7b.py`: 37/37 pass
- `test_factor_mining_candidates.py`: 15/15 pass

---

## 7. Assertions

- No factor_values were built.
- No dynamic evaluation was run.
- No strategy backtest was run.
- No factor status was upgraded.
- No alpha claim was made.
- All 27 selected_for_7B factors have explicit expected_direction from candidate CSV.
- Missing factor_values in explicit mode will raise FileNotFoundError.
- Fallback positive in explicit mode will raise ValueError.
