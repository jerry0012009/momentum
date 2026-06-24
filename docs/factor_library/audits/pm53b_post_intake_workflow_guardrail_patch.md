# PM-53B: Post-Intake Workflow Guardrail Patch

**Date:** 2026-06-24
**Status:** Research diagnostics. NOT production. NOT live trading.
**Verdict:** PM53B_WORKFLOW_GUARDRAIL_PASS

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

### 8.1 Consistency Checker (`check_active_factor_workflow_consistency.py`)

```
Active factor count: 84
Tables checked: 13
PASS: 13  |  FAIL: 0
Verdict: PASS
```

All 13 required tables (rankic, long_short, diagnostics_summary, shape, rolling_stability, decile, capacity, scorecard, redundancy_summary, regime_exposure, profile, bilingual_cards, html_payload) contain exactly 84/84 active factors.

### 8.2 `--only-missing` Result

```
All factors have complete workflow. Nothing to do.
```

Returns empty list — no factors with incomplete workflow.

### 8.3 Page QA (`check_factor_evaluation_page_completeness.py`)

```
Total: 28  |  PASS: 28  |  FAIL: 0
```

Including PM-53B checks:
- `pm53b_count_match`: PASS — page 84 factors == active 84 factors
- `pm53b_factor_diagnostics`: PASS — all 84 factors have shape/decile/capacity/scorecard/profile

### 8.4 Integrity QA (`check_post_intake_workflow_integrity.py --all-active`)

```
Factors: 84
Total checks: 1596
PASS: 1596
FAIL: 0
WARN: 0

Active-Universe Count Consistency (PM-53B):
  All 12 tables: 84/84 PASS
  Active count consistency: PASS
```

### 8.5 Active Factor Count Consistency

| Table | Count | Expected | Status |
|-------|-------|----------|--------|
| rankic | 84 | 84 | PASS |
| long_short | 84 | 84 | PASS |
| diagnostics_summary | 84 | 84 | PASS |
| shape | 84 | 84 | PASS |
| rolling_stability | 84 | 84 | PASS |
| decile | 84 | 84 | PASS |
| capacity | 84 | 84 | PASS |
| scorecard | 84 | 84 | PASS |
| redundancy_summary | 84 | 84 | PASS |
| regime_exposure | 84 | 84 | PASS |
| profile | 84 | 84 | PASS |
| bilingual_cards | 84 | 84 | PASS |
| html_payload | 84 | 84 | PASS |

---

## 9. Remaining Limitations

1. **HTML payload check depends on page rebuild:** If the page is not rebuilt after diagnostics are updated, the HTML payload check will show stale results. Always rebuild page after running diagnostics.
2. **No automated fix:** The checker reports missing factors but does not automatically fix them. Operators must run the appropriate diagnostic scripts.
3. **Consistency check is structural, not semantic:** The checker verifies factor IDs are present in tables but does not validate data quality (NaN rates, value ranges, etc.).

---

## 10. PM-53B Closure Verification (2026-06-24)

All acceptance criteria verified:

| Check | Result |
|-------|--------|
| `check_active_factor_workflow_consistency.py` | PASS — 13/13 tables, 84/84, exit 0 |
| `--only-missing --dry-run` | "All factors have complete workflow. Nothing to do." — exit 0 |
| `check_factor_evaluation_page_completeness.py` | PASS — 28/28, exit 0 |
| `check_post_intake_workflow_integrity.py --all-active` | PASS — 1596/1596, 12/12 consistency, exit 0 |
| Active factor count | 84 |
| All required output counts | 84/84 across all 13 tables |
| PM-53B verdict | PM53B_WORKFLOW_GUARDRAIL_PASS |
| No formula/direction/factor_values/cap/signal changes | ✓ |
| No trading recommendation | ✓ |

**PM-53B is CLOSED.**

---

## 11. Recommended Next PM

- PM-54: Automated consistency-triggered diagnostic completion (auto-detect missing factors and auto-run the required diagnostic stages)
