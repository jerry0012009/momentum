# Phase 12D-A-R: Repository Map & Entry Document Repair

**Phase:** 12D-A-R
**Date:** 2026-06-17
**Status:** COMPLETE
**Predecessor:** Phase 12D-A (Repository Map & File Ownership Audit)

---

## Purpose

Repair minor but important entry-document issues in Phase 12D-A deliverables:

1. Conflating "the current crypto_top50 research run" with "the entire factor library framework"
2. Treating the old Phase 0–10 roadmap as the current authoritative document
3. Outdated Phase 12C/13 status language
4. Missing disclaimers (no real execution, no alpha claim, no production claim)

---

## Repairs Applied

### 1. Framework vs Current Run Distinction

**Problem:** Phase 12D-A documents implied `research/factor_runs/crypto_top50_factor_library/` IS the factor library, rather than being ONE run's audit archive.

**Fix:** All entry documents now clearly state:
- **Factor Library Framework** = reusable pipeline (`src/momentum/`, `scripts/`, `config/`)
- **Current Research Run** = `crypto_top50_usdt_perp_1h` — first complete execution of the framework
- `research/factor_runs/crypto_top50_factor_library/` = this run's audit dossier, not the framework itself
- Future runs on different universes will produce their own dossiers

**Files changed:**
- `docs/FACTOR_LIBRARY_HOME.md` — new "What Is This?" section with two-layer explanation
- `docs/PROJECT_TREE_UPDATED.md` — header note + research section clarification
- `reports/site/factor-library/repository-map.html` — source-of-truth rule 1 updated
- `reports/site/factor-library/file-ownership.html` — research row description + top-of-page note
- `reports/site/factor-library/assets/repo_map.json` — meta.run_id, meta.note, folder descriptions

### 2. FACTOR_LIBRARY_ROADMAP.md Authority Correction

**Problem:** Documents said "Phase 0–10 roadmap (authoritative)" — implying it's the current authority.

**Fix:** Changed to "early-to-mid phase roadmap / REFERENCE" with note that current Phase 12+ status should be read from FACTOR_LIBRARY_HOME.md, PROJECT_TREE_UPDATED.md, and latest Phase closeouts.

**Files changed:**
- `docs/FACTOR_LIBRARY_HOME.md` — Quick Navigation table + explicit note
- `docs/PROJECT_TREE_UPDATED.md` — tree comment updated
- `reports/site/factor-library/file-ownership.html` — table row updated

### 3. Phase 12C / Phase 13 Status Correction

**Problem:** Some documents had "PM decision required: Phase 12C transparency closeout or Phase 13 paper execution" — Phase 12C is already complete.

**Fix:** Changed to "Phase 12C COMPLETE. Phase 13 NOT STARTED. Next steps: transparency portal, repository structure, workflow map, documentation governance, Phase 13A decision preparation."

**Files changed:**
- `docs/FACTOR_LIBRARY_HOME.md` — Current Status section rewritten

### 4. Disclaimers Added

**Problem:** No explicit statements about what this project is NOT.

**Fix:** Added to all entry documents:
- **No real execution.** No exchange connection, no order placement.
- **No alpha claim.** Research metrics are in-sample/backtest results.
- **No production claim.** This is a research pipeline, not a live trading system.

**Files changed:**
- `docs/FACTOR_LIBRARY_HOME.md` — Current Status section
- `reports/site/factor-library/repository-map.html` — new disclaimers card
- `reports/site/factor-library/assets/repo_map.json` — disclaimers array
- `research/factor_runs/crypto_top50_factor_library/PHASE_12D_A_REPOSITORY_MAP_AUDIT.md` — Purpose section

### 5. Document Status Labels Introduced

**Problem:** No way to tell which docs are current vs historical.

**Fix:** Defined 6 labels: CURRENT, REFERENCE, GENERATED, SUPERSEDED, LEGACY, DO_NOT_EDIT. Taxonomy defined in FACTOR_LIBRARY_HOME.md and PROJECT_TREE_UPDATED.md. Per-document tagging deferred.

---

## Constraints Observed

- ✅ No files moved
- ✅ No files deleted
- ✅ No research results changed
- ✅ No Phase 13 started
- ✅ No trading/execution/API logic added
- ✅ No factors/signals/backtests re-run

---

## Deliverables

| # | File | Type |
|---|------|------|
| 1 | `docs/FACTOR_LIBRARY_HOME.md` | Revised |
| 2 | `docs/PROJECT_TREE_UPDATED.md` | Revised |
| 3 | `reports/site/factor-library/repository-map.html` | Revised |
| 4 | `reports/site/factor-library/file-ownership.html` | Revised |
| 5 | `reports/site/factor-library/assets/repo_map.json` | Revised |
| 6 | `research/.../PHASE_12D_A_REPOSITORY_MAP_AUDIT.md` | Supplemented |
| 7 | `PHASE_12D_A_R_REPOSITORY_MAP_REPAIR.md` | New (this file) |
| 8 | `phase12d_a_r_quality_checks.csv` | New |
| 9 | `tests/unit/test_phase12d_a_r_repository_map_repair.py` | New |
