# Phase 13A-P0: Control Surface Repair — Closeout Summary

**Status:** HISTORICAL_CLOSEOUT. Preserved for audit trail only. Do not use for current counts, current entry points, or new-factor workflow. Use `docs/factor_library/START_HERE.md` and `factor_library_state.md`.

**Phase:** 13A-P0
**Date:** 2026-06-20
**Type:** Documentation / governance only. No scripts modified. No data modified.

---

## Changed Files

| File | Change |
|------|--------|
| `README.md` | Added "Current Mainline" section at top with key numbers, document links, and public site links. Demoted old M1/Xiaomi/Backtrader content under "Historical / Adjacent Research". |
| `docs/factor_library/START_HERE.md` | **Created.** Bilingual (CN+EN) entry document. Pipeline map, canonical files, do-not-use files, how-to-extend guides. ~120 lines. |
| `reports/site/factor-library/actual-script-map.html` | **Full rewrite.** SVG diagram expanded from 8 to 12 nodes. Factor-Level Evaluation is now a separate explicit node (#6). Added Factor Registry & Ops (#4), Catalog & Direction Audit (#7), Archive/Orphans (#12). Fixed malformed HTML/JS corruption in evaluation node data. All nodes bilingual. Interactive JS detail panel working. |
| `docs/factor_library/FILE_STATUS_REGISTER.csv` | Added `docs/factor_library/START_HERE.md` entry (ACTIVE_MAINLINE). |
| `research/factor_runs/crypto_top50_factor_library/phase13a_p0_control_surface_quality_checks.csv` | **Created.** 23 quality checks, all PASS. |
| `docs/factor_library/PHASE_13A_P0_CONTROL_SURFACE_REPAIR_SUMMARY.md` | **Created.** This file. |

---

## What Was Fixed

1. **README.md** — New reader immediately sees the current mainline (factor library), not the old M1 project.
2. **START_HERE.md** — Concise bilingual entry point for the factor library project.
3. **actual-script-map.html** — 12-node pipeline diagram (was 8). Factor-Level Evaluation is its own node, not buried inside Signal Evaluation. Fixed JS corruption (HTML fragments in string literals). Added Archive/Orphans section with FILE_STATUS_REGISTER.csv and ORPHAN_WORK_AUDIT.md references.
4. **FILE_STATUS_REGISTER.csv** — START_HERE.md registered.

---

## Intentionally Not Changed

- `scripts/factor_formula_registry.py` — forbidden
- `scripts/build_factor_values.py` — forbidden
- `scripts/evaluate_factors.py` — forbidden
- `scripts/build_phase9b_signal_panel.py` — forbidden
- `scripts/evaluate_signals.py` — forbidden
- `data/cache/` — no parquet data touched
- `data/features/` — no parquet data touched
- No factor formulas, signal construction, labels, or raw data modified
- Historical files preserved (not deleted, not moved)
- Archive pages not added back to public navigation
- `index.html`, `factor-evaluation.html`, `signal-evaluation-summary.html` — not modified (no changes needed)

---

## Quality Check Summary

**23 checks: 23 PASS, 0 FAIL.**

See: `research/factor_runs/crypto_top50_factor_library/phase13a_p0_control_surface_quality_checks.csv`

Key verifications:
- No production/alpha/live trading claims
- Factor-Level Evaluation as separate node in actual-script-map.html
- All required scripts mentioned (evaluate_factors.py, check_factor_registry_integrity.py, build_factor_catalog.py, check_factor_catalog_integrity.py, audit_factor_direction_semantics.py)
- FILE_STATUS_REGISTER.csv and ORPHAN_WORK_AUDIT.md referenced in archive section
- No malformed HTML/JS fragments
- No forbidden files modified

---

## Next Recommended Phase

**Phase 13A-P1 — Factor Evaluation Schema Upgrade**

Upgrade the factor-level evaluation output schema to include additional metrics (e.g., coverage %, direction consistency, horizon correlation matrix) and update the public factor-evaluation.html page accordingly.
