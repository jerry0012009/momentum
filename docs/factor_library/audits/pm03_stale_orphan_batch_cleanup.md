# PM-03 Stale / Orphan Batch Cleanup

**Date:** 2026-06-21
**Follows:** PM-01, PM-02A, PM-02B

## Summary

Batch cleanup of 9 stale/orphan scripts from `scripts/` and 8 root-level PHASE_12D closeout documents. All deletions are evidence-based: no active code imports or subprocess-calls any deleted file.

## Per-candidate audit

| path | action | reason | active_code_refs | active_doc_refs_before | historical_refs_remaining | risk | validation |
|------|--------|--------|-----------------|----------------------|--------------------------|------|-----------|
| scripts/evaluate_factors_dynamic_universe.py | DELETED | Broken imports, no active code refs | 0 | START_HERE, Control Center, manifest, register | PM-01 audit, PM-03 prompt | LOW | grep scripts/ src/ |
| scripts/compare_static_dynamic_factor_evals.py | DELETED | No active code refs | 0 | START_HERE, manifest, register | PM-01 audit, PM-03 prompt | LOW | grep scripts/ src/ |
| scripts/export_alphalens_factor_data.py | DELETED | No active code refs | 0 | START_HERE, manifest, register | PM-01 audit, PM-03 prompt | LOW | grep scripts/ src/ |
| scripts/run_alphalens_smoke_check.py | DELETED | No active code refs | 0 | START_HERE, manifest, register | PM-01 audit, PM-03 prompt | LOW | grep scripts/ src/ |
| scripts/audit_dynamic_universe_data_coverage.py | DELETED | No active code refs | 0 | manifest | PM-01 audit, PM-03 prompt | LOW | grep scripts/ src/ |
| scripts/audit_dynamic_universe_factor_values.py | DELETED | No active code refs | 0 | manifest | PM-01 audit, PM-03 prompt | LOW | grep scripts/ src/ |
| scripts/audit_dynamic_universe_labels.py | DELETED | No active code refs | 0 | manifest | PM-01 audit, PM-03 prompt | LOW | grep scripts/ src/ |
| scripts/build_crypto_native_factor_values.py | DELETED | No active code refs | 0 | START_HERE, manifest, register | PM-01 audit, PM-03 prompt | LOW | grep scripts/ src/ |
| scripts/build_factor_values_batch.py | DELETED | No active code refs | 0 | manifest | PM-01 audit, PM-03 prompt | LOW | grep scripts/ src/ |
| PHASE_12D_*.md (8 files, root) | MOVED_TO_ARCHIVE | Historical, not in active entry path | 0 | register | register (updated) | LOW | ls root/ |

## Counts

- Total files deleted: 9
- Total files moved: 8
- Governance files updated: 6 (START_HERE, Control Center, manifest, FILE_STATUS_REGISTER, ORPHAN_WORK_AUDIT, this audit note)
- Blocked deletions: 0

## Non-change statement

No factor logic, signal logic, universe data, labels, factor values, evaluation outputs, signal panels, or public result pages were changed.

## Validation commands run

```bash
python -m py_compile scripts/build_dynamic_universe_monthly_volume.py scripts/build_factor_values.py scripts/evaluate_factors.py scripts/run_factor_intake.py scripts/build_phase9b_signal_panel.py scripts/evaluate_signals.py
# All OK

grep -RIn "evaluate_factors_dynamic_universe|compare_static_dynamic|export_alphalens|run_alphalens|build_crypto_native|build_factor_values_batch|audit_dynamic_universe" scripts/ src/
# Only self-references in deleted files (now removed) + comment in evaluate_factors.py docstring (historical, not an import)
```
