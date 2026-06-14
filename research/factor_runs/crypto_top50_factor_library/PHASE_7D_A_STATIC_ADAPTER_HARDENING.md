# Phase 7D-A — Static Evaluation Adapter Hardening

> Date: 2026-06-14
>
> Status: COMPLETE

---

## 1. What Was Modified

| File | Change |
|------|--------|
| `scripts/evaluate_factors.py` | Added `--factor-ids`, `--candidate-csv`, `--status` args; added `load_selected_factor_ids()`, `load_candidate_directions()`, `validate_factor_ids()`; direction lookup: candidate CSV → old catalog → fallback positive (with fail-fast in explicit mode); summary CSV output |
| `tests/unit/test_phase7d_static_adapter.py` | NEW: 14 tests |

---

## 2. Factor Subset Support

Static evaluator now supports:

```bash
# Evaluate only 27 selected_for_7B factors
--candidate-csv research/factor_runs/crypto_top50_factor_library/factor_mining_candidates_v0_1.csv
--status selected_for_7B

# Or explicit list
--factor-ids mom_5h,mom_10h,...
```

Default behavior (no args) unchanged: evaluate IMPLEMENTED factors from old catalog.

---

## 3. selected_for_7B Resolution

- ✓ Resolves to exactly 27 factors
- ✓ All 27 in REGISTRY
- ✓ All 27 have candidate CSV direction
- ✓ qvol factors: family = `quote_volume_liquidity`
- ✓ xs_rank factors: family = `cross_sectional_normalized`

---

## 4. Direction Source

Priority: candidate CSV → old catalog → fallback positive.

In explicit/candidate mode: fallback positive raises `ValueError`.

All 27 selected_for_7B: direction_source = `candidate_csv`, zero fallback.

---

## 5. Fail-Fast

In explicit/candidate mode:

- Missing factor_values → `FileNotFoundError`
- Count ≠ 27 for selected_for_7B → `ValueError`
- Fallback positive → `ValueError`

---

## 6. Summary CSV Output

Static evaluator now writes:

- `reports/artifacts/factor_eval/<dataset_id>/factor_eval_static_summary.csv` (ret_fwd_1h only)
- `reports/artifacts/factor_eval/<dataset_id>/factor_eval_static_summary_all_labels.csv` (all 4 labels)

Both include `direction_source` field.

---

## 7. Tests

```
87 passed in 0.95s
```

- `test_phase7d_static_adapter.py`: 14/14 pass
- `test_phase7c_dynamic_adapter.py`: 21/21 pass
- `test_crypto_factor_batch7b.py`: 37/37 pass
- `test_factor_mining_candidates.py`: 15/15 pass

---

## 8. Assertions

- No new factor_values were built.
- No static evaluation was run.
- No static-vs-dynamic comparison was run.
- No strategy backtest was run.
- No factor status was upgraded.
- No alpha claim was made.
