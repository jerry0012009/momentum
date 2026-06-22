# PM-25 Audit: Reusable Factor Library Staleness Monitor

**Date:** 2026-06-22
**Status:** COMPLETE
**NOT production. NOT live trading. Research diagnostics only.

---

## 1. Summary

Created a reusable, non-hardcoded factor library staleness monitor that checks artifact
coverage, pairwise redundancy completeness, timestamp staleness, and page content. Updated
the orchestrator with new pipeline stages and documented the full paper→regime→page pipeline.

## 2. Files Created

- `scripts/check_factor_library_staleness.py` — staleness monitor (reusable, no hardcoded counts)
- `docs/factor_library/audits/pm25_reusable_staleness_workflow_monitor.md` — this file

## 3. Files Modified

- `scripts/run_factor_library_refresh.py` — added stages: paper-diagnostics, paper-page-payload, staleness
- `docs/factor_library/REGENERATION_CONTRACT.md` — documented paper→regime→page pipeline

## 4. Staleness Monitor Design

### 4.1 Expected Factor Count Resolution

1. **Primary:** `factor_library_state.json` → `registered_factors` field
2. **Fallback:** `factor_formula_registry.py` → count `FactorSpec(` entries via regex

No hardcoded counts. The monitor adapts when factors are added/removed.

### 4.2 Check Groups

| Group | Checks | What it verifies |
|-------|--------|-----------------|
| coverage | 10 artifact checks | Each key CSV/JSON has expected factor count |
| redundancy | 1 check | Pairwise redundancy row count = n*(n-1)/2 |
| staleness | 5 mtime checks | Upstream files not newer than state; page not stale |
| page | 5 content checks | Page HTML contains key sections (diagnostics, redundancy, etc.) |

### 4.3 Output Format

**CSV columns:** check_id, check_group, status, severity, artifact_path, expected, actual,
message, recommended_stage, recommended_command

**JSON fields:** summary_status, generated_at, expected_factor_count, expected_pair_count,
source_of_expected_count, n_pass, n_warn, n_fail, n_skip, recommended_next_commands, checks

**Statuses:** PASS / WARN / FAIL / SKIP
**Severities:** INFO / LOW / MEDIUM / HIGH / BLOCKER
**Summary:** STALENESS_PASS / STALENESS_PASS_WITH_WARNINGS / STALENESS_FAIL

### 4.4 CLI

```bash
python scripts/check_factor_library_staleness.py           # console output
python scripts/check_factor_library_staleness.py --json     # + JSON to stdout
python scripts/check_factor_library_staleness.py --strict   # WARN → exit 1
```

## 5. Orchestrator Changes

### 5.1 New Stages

| Stage | Description | Expensive |
|-------|-------------|-----------|
| paper-diagnostics | Single-factor paper portfolio diagnostics | YES |
| paper-page-payload | Build single-factor paper page payload | no |
| staleness | Check factor library staleness | no |

### 5.2 Pipeline Order (updated)

```
... redundancy → paper-diagnostics → paper-page-payload → regime → staleness → page → state
```

### 5.3 'all' Preset

The `all` preset uses `STAGE_NAMES` which automatically includes all stages in order.

## 6. Contract Updates

- Documented paper diagnostics → paper page payload → regime diagnostics → page pipeline
- Added regime dependency on PM-21B paper monthly returns (`single_factor_paper_monthly_returns.csv`)
- Added new scripts to cost table
- Updated available stages list

## 7. Paper → Regime → Page Pipeline

```
paper-diagnostics (EXPENSIVE)
  ↓ produces single_factor_paper_monthly_returns.csv
paper-page-payload (cheap)
  ↓ produces single_factor_paper_page_payload.json
regime (cheap)
  ↓ depends on paper monthly returns (PM-21B)
page (cheap)
  ↓ consumes all upstream artifacts
state (cheap)
```

## 8. Validation Results

- `py_compile` on both scripts: PASS
- `check_factor_library_staleness.py` (console): runs, produces reports
- `check_factor_library_staleness.py --json`: runs, outputs JSON summary
- `run_factor_library_refresh.py --stage staleness --dry-run`: PASS
- `run_factor_library_refresh.py --stage paper-page-payload --dry-run`: PASS
- `run_factor_library_refresh.py --stage paper-diagnostics --dry-run`: PASS

## 9. Limitations

1. Page content checks are soft (keyword presence only, not structural validation)
2. The staleness monitor reads mtime, not content hashes — a file could be overwritten with
   identical content and still show as "newer"
3. `_count_unique_factor_ids_in_csv` uses pandas at runtime — if pandas is unavailable,
   falls back gracefully (returns None → SKIP/FAIL)
4. The monitor does not check raw data freshness (bars parquet mtime)
5. Pairwise redundancy check only verifies row count, not data quality

## 10. Recommended Next PM

**PM-26:** Factor library CI/CD integration — wire staleness check into pre-commit or CI
pipeline; add automated alerting on STALENESS_FAIL; consider content-hash-based staleness
for key artifacts.
