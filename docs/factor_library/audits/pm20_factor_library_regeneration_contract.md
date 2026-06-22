# PM-20 Audit — Factor Library Regeneration Contract

**Date:** 2026-06-22
**Verdict:** `REGENERATION_CONTRACT_PASS`

---

## 1. Summary Verdict

**REGENERATION_CONTRACT_PASS**

All required deliverables created. The regeneration contract is complete and the orchestration script passes dry-run validation.

---

## 2. Files Changed/Created

### Created:
- `scripts/run_factor_library_refresh.py` — Orchestration script
- `docs/factor_library/REGENERATION_CONTRACT.md` — Canonical regeneration contract
- `docs/factor_library/audits/pm20_factor_library_regeneration_contract.md` — This audit

### Updated (stale count cleanup):
- `docs/factor_library/START_HERE.md` — Removed stale "6 missing" hard-coded count
- `docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md` — Removed stale "6 taker/funding factors missing" hard-coded count
- `docs/factor_library/factor_library_manifest.json` — Updated stale counts (65→71 registered, 59→71 computed, 6→0 missing)

---

## 3. Canonical Pipeline Stages Documented

The REGENERATION_CONTRACT.md documents the full 12-stage pipeline:

1. **registry-integrity** — `check_factor_registry_integrity.py` (cheap)
2. **catalog** — `build_factor_catalog.py` + `check_factor_catalog_integrity.py` (cheap)
3. **values** — `build_factor_values.py` (cheap if cached)
4. **direction-audit** — `audit_factor_direction_semantics.py` (cheap)
5. **evaluate** — `evaluate_factors.py` (EXPENSIVE)
6. **diagnostics** — `build_factor_diagnostics_metrics.py` (cheap)
7. **metadata** — `build_factor_bilingual_cards.py` (cheap)
8. **scorecard** — `build_factor_quality_scorecard.py` (cheap)
9. **redundancy** — `build_factor_pairwise_redundancy_matrix.py` (EXPENSIVE)
10. **page** — `_build_factor_eval_html.py` (cheap)
11. **state** — `build_factor_library_state.py` (cheap)

---

## 4. Orchestration Script Features

`scripts/run_factor_library_refresh.py`:

- `--stage <name|preset>` — Run a single stage or named preset
- `--dry-run` — Print commands without executing
- `--expensive-ok` — Required guard for expensive stages
- Stdout logging of every command with timing
- Fail-fast: aborts on first non-zero exit code
- 7 presets: `all`, `cheap`, `page-only`, `scorecard-only`, `metadata-only`, `diagnostics-only`, `redundancy-only`
- 11 individual stages available

---

## 5. Expensive Step Guard Behavior

- `evaluate` and `redundancy` stages are marked as expensive
- Without `--expensive-ok`, these stages print an error and exit
- `--dry-run` always works regardless of expensive flag
- Preset `cheap` excludes all expensive stages automatically

---

## 6. Entry Docs Cleanup Summary

### START_HERE.md
- Removed: hard-coded "Missing factor_values: **6**" line
- Replaced with: reference to `factor_library_state.json` as single source of truth

### FACTOR_LIBRARY_CONTROL_CENTER.md
- Removed: "**6** taker/funding factors missing `factor_values` (not yet computed)"
- Replaced with: reference to `factor_library_state.md` (auto-generated)
- Added: link to `REGENERATION_CONTRACT.md` in Extension Points and PM/AI Audit sections

### factor_library_manifest.json
- Updated stale counts to match `factor_library_state.json`:
  - `total_registered`: 65 → 71
  - `with_factor_values`: 59 → 71
  - `missing_factor_values`: 6 → 0
  - `missing_list`: cleared (no longer missing)
  - `computed_factors` in `factor_level_evaluation`: 59 → 71
  - `missing_fv` in `factor_level_evaluation`: 6 → 0
- Added `active_supporting_scripts`: `run_factor_library_refresh.py`
- Added `extension_points.factor_library_refresh`

---

## 7. Validation Results

### Compilation check
```
python -m py_compile scripts/run_factor_library_refresh.py → OK (exit 0)
```

### Dry-run validation
```
python scripts/run_factor_library_refresh.py --dry-run → OK (prints all stages)
python scripts/run_factor_library_refresh.py --stage page --dry-run → OK
python scripts/run_factor_library_refresh.py --stage scorecard --dry-run → OK
python scripts/run_factor_library_refresh.py --stage cheap --dry-run → OK
python scripts/run_factor_library_refresh.py --stage all --dry-run → OK
```

### Expensive guard validation
```
python scripts/run_factor_library_refresh.py --stage all → BLOCKED (requires --expensive-ok)
python scripts/run_factor_library_refresh.py --stage evaluate → BLOCKED
python scripts/run_factor_library_refresh.py --stage redundancy → BLOCKED
```

### Stale doc check
```
"6 taker/funding factors missing" in START_HERE.md → False
"6 taker/funding factors missing" in FACTOR_LIBRARY_CONTROL_CENTER.md → False
"Missing factor_values: **6**" in START_HERE.md → False
```

---

## 8. Remaining Limitations

1. **Orchestration script runs scripts sequentially.** No parallel execution of independent stages (e.g., catalog + direction-audit could run in parallel). Sequential is correct and safe for a first version.

2. **No retry logic.** If a stage fails, the script aborts. The user must fix the issue and re-run from the failed stage. This is intentional — silent retries would mask errors.

3. **State JSON counts may drift** if someone runs a partial pipeline without running the state stage last. The contract documents that state must always be regenerated last.

4. **No CI/CD integration.** The script is designed for manual/agent use. CI integration is a future enhancement.

---

## 9. Non-Change Statement

PM-20 did NOT:

- Add new factors
- Modify factor formulas
- Modify factor_values manually
- Modify `scripts/factor_formula_registry.py` (except stale count references in docs)
- Modify `scripts/factor_ops.py`
- Modify signal panel construction
- Rebuild signal panel
- Create a new public page
- Make production/live/tradeability/alpha claims
- Run the full expensive evaluation/redundancy pipeline

---

## 10. Recommended Next PM

**PM-21: Factor library health monitoring and automated staleness detection.**

Rationale: With the regeneration contract in place, the next step is automated detection of when outputs become stale (e.g., a cron job or heartbeat check that compares file timestamps against the dependency graph to flag when re-computation is needed). This would close the loop between the contract and operational practice.
