# Orphan Work Audit

**Phase:** 12D-H9  
**Generated:** 2026-06-19

---

## HIGH Orphan Risk

### 1. `scripts/evaluate_factors_dynamic_universe.py`

- **Status:** DEPRECATED_STALE / HISTORICAL_REFERENCE
- **Reason:** Imports `evaluate_factors` which did not exist until H8 created a new one. The old import targets a different file with a different API. The script is broken and cannot run.
- **Action:** Keep in place. Do not use as evaluator. Do not move. Do not delete. Do not re-enable. The canonical evaluator is `scripts/evaluate_factors.py` (H8/H8-R). The canonical parity guard is `scripts/check_factor_ic_parity.py` (H8-R).

### 2. `scripts/compare_static_dynamic_factor_evals.py`

- **Status:** ORPHAN_REVIEW_REQUIRED
- **Reason:** Compares old static and dynamic universe evaluations. Both old evaluators are stale. The script may produce misleading results if run against stale outputs.
- **Action:** Review. If the comparison is still useful, update to use `evaluate_factors.py` output. Otherwise archive.

---

## MEDIUM Orphan Risk

### 3. `scripts/export_alphalens_factor_data.py`

- **Status:** HISTORICAL_ARCHIVE
- **Reason:** Exports factor data in Alphalens format. The Alphalens integration was used in Phase 5B and is no longer part of the current pipeline. The exported data exists in `alphalens_exports/` but is not consumed by any active script.
- **Action:** Archive. Keep exported data as historical evidence.

### 4. `scripts/run_alphalens_smoke_check.py`

- **Status:** HISTORICAL_ARCHIVE
- **Reason:** Runs Alphalens smoke check on exported data. Phase 5B artifact. No current pipeline depends on it.
- **Action:** Archive.

### 5. Root-level `PHASE_12D_*.md` files (7 files)

- **Status:** HISTORICAL_ARCHIVE
- **Reason:** Phase closeout documents sitting in the root directory. They are valuable historical evidence but should be in `docs/` not root.
- **Action:** Consider moving to `docs/phase_closeout/` in a future cleanup. Do not delete.

### 6. `scripts/audit_dynamic_universe_*.py` (3 files)

- **Status:** ORPHAN_REVIEW_REQUIRED
- **Reason:** Audit scripts for the dynamic universe pipeline (Phase 6C). The dynamic universe is a secondary pipeline, not the current mainline. These scripts are functional but produce outputs that don't feed into the current main pipeline.
- **Action:** Review. If dynamic universe becomes active again, these are needed. Otherwise archive.

### 7. `scripts/build_crypto_native_factor_values.py`

- **Status:** ORPHAN_REVIEW_REQUIRED
- **Reason:** Builds crypto-native factor values (Phase 7M-B). This is an alternative factor building pipeline. Some factors in the registry may use crypto-native computations.
- **Action:** Review. Check if any of the 53 registered factors depend on this script's outputs.

---

## LOW Orphan Risk (No Action Needed)

- `scripts/analyze_factor_redundancy.py` — Supporting analysis, still useful
- `scripts/audit_crypto_factor_results.py` — Supporting audit, still useful
- `scripts/apply_factor_warning_flags.py` — Warning flag system, still useful
- `scripts/export_alphalens_factor_data.py` — Historical, clearly archived
- `scripts/run_alphalens_smoke_check.py` — Historical, clearly archived
- All `build_rank*.py` scripts — Strategy research artifacts, not factor library

---

## Summary

| Risk Level | Count | Action |
|-----------|-------|--------|
| HIGH | 2 | Archive or review |
| MEDIUM | 5 | Archive or move |
| LOW | 7+ | No action |
