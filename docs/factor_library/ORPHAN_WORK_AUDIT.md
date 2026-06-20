# Orphan Work Audit

**Status:** Active orphan-risk register for factor-library work
**Generated:** 2026-06-19
**Last updated:** 2026-06-21 (PM-03 batch cleanup)

---

## PM-03 Cleanup Summary

The following files were deleted or moved in PM-03. Git history preserves all content.

### Deleted scripts (9 files)

| Former path | Former status | Reason for deletion |
|-------------|---------------|-------------------|
| `scripts/evaluate_factors_dynamic_universe.py` | DEPRECATED_STALE | Broken imports; no active code refs |
| `scripts/compare_static_dynamic_factor_evals.py` | ORPHAN | No active code refs |
| `scripts/export_alphalens_factor_data.py` | HISTORICAL_ARCHIVE | No active code refs |
| `scripts/run_alphalens_smoke_check.py` | HISTORICAL_ARCHIVE | No active code refs |
| `scripts/audit_dynamic_universe_data_coverage.py` | ORPHAN | No active code refs |
| `scripts/audit_dynamic_universe_factor_values.py` | ORPHAN | No active code refs |
| `scripts/audit_dynamic_universe_labels.py` | ORPHAN | No active code refs |
| `scripts/build_crypto_native_factor_values.py` | ORPHAN | No active code refs |
| `scripts/build_factor_values_batch.py` | ORPHAN | No active code refs |

### Moved files (8 files)

| Former path | New path |
|-------------|----------|
| `PHASE_12D_B_R_ACTUAL_CODE_STRUCTURE_REPAIR.md` | `docs/factor_library/archive/phase12d/` |
| `PHASE_12D_C_PIPELINE_DETAIL_AND_FACTOR_SOURCE_MAP.md` | `docs/factor_library/archive/phase12d/` |
| `PHASE_12D_C_R_FACTOR_LINEAGE_REPAIR.md` | `docs/factor_library/archive/phase12d/` |
| `PHASE_12D_D_FACTOR_FORMULA_CARDS.md` | `docs/factor_library/archive/phase12d/` |
| `PHASE_12D_E_R_SIGNAL_WALKTHROUGH_REPAIR.md` | `docs/factor_library/archive/phase12d/` |
| `PHASE_12D_E_SIGNAL_WALKTHROUGH.md` | `docs/factor_library/archive/phase12d/` |
| `PHASE_12D_F_FACTOR_PERFORMANCE_TRUST_METRICS.md` | `docs/factor_library/archive/phase12d/` |
| `PHASE_12D_G_OPERATING_MANUAL_MASTER_REGISTRY.md` | `docs/factor_library/archive/phase12d/` |

---

## Remaining Items

### Old documentation portals

- **Status:** SUPERSEDED / HISTORICAL_REFERENCE
- **Files:** `docs/DOCS_INDEX.md`, `docs/FACTOR_LIBRARY_HOME.md`, `docs/factor_library_transparency/README.md`
- **Reason:** These paths previously looked like current portals but contained old phase framing or stale counts.
- **Action:** Keep as historical. `docs/factor_library_transparency/` classified as HISTORICAL_ARCHIVE in FILE_STATUS_REGISTER.

### docs/PROJECT_TREE.md

- **Status:** STALE_SNAPSHOT
- **Reason:** Old static project tree snapshot. No active governance docs link to it.
- **Action:** Keep as historical reference. Do not rely on it for current structure.
