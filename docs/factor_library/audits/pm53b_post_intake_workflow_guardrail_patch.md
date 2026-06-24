# PM-53B: Post-Intake Workflow Guardrail Patch

**Date:** 2026-06-24
**Status:** Research diagnostics. NOT production. NOT live trading.
**Verdict:** PENDING (see QA results below)

---

## 1. Summary

PM-53 audit discovered that the active factor library (84 factors) had 4 non-cap Alpha101 factors missing shape/decile/capacity diagnostics. Root cause: post-intake workflow `--only-missing` only checked pairwise redundancy, not all required downstream outputs. This allowed factors to be registered and visible on the page while missing critical diagnostics.

PM-53A fixes the data gap (computing missing diagnostics for the 4 factors).
PM-53B fixes the workflow guardrail to prevent recurrence.

**This PM does NOT:**
- Add new factors
- Modify formulas
- Modify expected_direction
- Modify factor_values
- Modify cap data source
- Enter signal construction
- Make trading recommendations

---

## 2. Root Cause of PM-53 Failure

The `detect_missing_factors()` function in `run_post_intake_workflow_completion.py` only checked pairwise redundancy:

```python
# OLD — only checks pairwise redundancy
def detect_missing_factors():
    pairwise = pd.read_csv(DIAG_DIR / "factor_pairwise_redundancy.csv")
    has_pairwise = fid in set(pairwise["factor_i"].unique()) | set(pairwise["factor_j"].unique())
```

This missed factors that had pairwise data but lacked shape, decile, or capacity. No active-universe-level consistency check existed — each diagnostic script could silently skip factors without the orchestrator noticing.

---

## 3. Files Changed

### New files:
- `scripts/check_active_factor_workflow_consistency.py` — new active factor universe consistency checker

### Modified files:
- `scripts/run_post_intake_workflow_completion.py` — enhanced `detect_missing_factors()` to check all 11 required outputs + page payload
- `scripts/check_factor_evaluation_page_completeness.py` — added PM-53B active universe consistency checks (count match + per-factor diagnostics presence)
- `scripts/check_post_intake_workflow_integrity.py` — added `--all-active` flag with active-universe consistency table
- `docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md` — added §14 Active Factor Universe Consistency Gate
- `docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md` — added PM-53B consistency gate to PM/AI First Steps
- `docs/factor_library/REGENERATION_CONTRACT.md` — added PM-53B rule #12 to AI Guardrails

### Not changed:
- No factor formulas
- No expected_direction values
- No factor_values
- No cap data source
- No signal construction code
- No trading recommendation code

---

## 4. New Consistency Checker Behavior

`scripts/check_active_factor_workflow_consistency.py` reads `factor_library_state.json` and checks every active factor against 13 required outputs:

| # | Table | Key Column |
|---|-------|-----------|
| 1 | factor_level_rankic_summary.csv | factor_name |
| 2 | factor_level_long_short_summary.csv | factor_name |
| 3 | factor_diagnostics_summary.csv | factor_id |
| 4 | factor_quantile_shape_summary.csv | factor_id |
| 5 | factor_rolling_stability_summary.csv | factor_id |
| 6 | factor_decile_shape_summary.csv | factor_id |
| 7 | factor_capacity_liquidity_summary.csv | factor_id |
| 8 | factor_quality_scorecard.csv | factor_id |
| 9 | factor_redundancy_summary.csv | factor_id |
| 10 | factor_regime_exposure_summary.csv | factor_id |
| 11 | factor_unified_profile_summary.csv | factor_id |
| 12 | factor_bilingual_cards.csv | factor_id |
| 13 | factor-evaluation.html payload | factor_id |

Output: active factor count, per-table count, missing factor IDs, extra factor IDs, PASS/FAIL verdict. Exit code non-zero on FAIL.

---

## 5. Improved `--only-missing` Behavior

Old: only checked pairwise redundancy.
New: checks each active factor against all 11 CSV tables + page payload. Reports which specific tables each factor is missing from.

**Behavior rules:**
- Active factor absent from any required output → included in missing list
- Unavailable-but-accepted optional fields are NOT treated as failure
- cap factors and non-cap factors are treated equally
- Blocked factors in active list would trigger detection

---

## 6. Page QA Additions

New function `check_pm53b_active_universe_consistency()` adds:

1. **Count match:** page visible factor count == active factor count (from state JSON)
2. **Per-factor diagnostics presence:** every visible factor must exist in shape, decile, capacity, scorecard, and profile CSVs
3. **Fail on incomplete:** if any visible factor is missing required downstream diagnostics → page QA FAIL

---

## 7. Integrity QA Additions

New `--all-active` flag for `check_post_intake_workflow_integrity.py`:

- Reads all active factors from state JSON
- Runs full per-factor integrity checks (19 checks per factor)
- Appends active-universe consistency table showing per-table counts vs expected
- Reports PASS/FAIL for each table

---

## 8. QA Result on Current 84-Factor Library

**Note:** QA results depend on PM-53A completing the data computation for the 4 missing factors. Results below reflect the state at PM-53B script creation time.

(PENDING — to be filled after running QA checks)

---

## 9. Remaining Limitations

1. **PM-53A dependency:** The consistency gate will FAIL until PM-53A completes computing capacity diagnostics for the 4 non-cap Alpha101 factors. This is expected and correct — the gate is working as designed.
2. **HTML payload check depends on page rebuild:** If the page is not rebuilt after diagnostics are updated, the HTML payload check will show stale results. Always rebuild page after running diagnostics.
3. **No automated fix:** The checker reports missing factors but does not automatically fix them. Operators must run the appropriate diagnostic scripts.

---

## 10. Recommended Next PM

- PM-54: Automated consistency-triggered diagnostic completion (auto-detect missing factors and auto-run the required diagnostic stages)
