# PM-58: Core Evaluation Workflow Cleanup — De-scope Paper/Fee, Keep Robust, Define Cap Contract

**Date:** 2026-06-24
**Status:** Workflow boundary cleanup.
**Verdict:** PM58_CORE_WORKFLOW_CLEANUP_PASS

---

## 1. Summary

PM-54/55/56/56A/57 introduced robust diagnostics alongside existing paper/fee modules. PM-58 draws a clear line: robust RankIC/LS are core, paper/fee are optional deep-dive, cap is a conditional input source.

**This PM does NOT:**
- Add new factors
- Modify formulas / expected_direction / factor_values
- Modify cap data
- Modify RankIC / LS calculations
- Modify robust RankIC / LS calculations
- Modify scorecard / best_horizon
- Enter signal construction
- Make trading recommendations
- Run full paper simulation or fee sensitivity
- Delete historical paper/fee files

---

## 2. Decision Rules

```
Paper simulation decision: OPTIONAL_CANDIDATE_ONLY
Fee sensitivity decision:  OPTIONAL_CANDIDATE_ONLY
Cap source decision:       KEEP_AS_CONDITIONAL_CORE_SOURCE
Robust RankIC decision:    KEEP_AS_CORE_SINGLE_FACTOR_EVALUATION
Robust LS decision:        KEEP_AS_CORE_SINGLE_FACTOR_EVALUATION
```

---

## 3. Files Changed

| File | Change |
|------|--------|
| `scripts/_build_factor_eval_html.py` | Paper/fee wrapped in collapsible `<details>`; reading order updated; summary table labeled "opt" |
| `scripts/check_factor_evaluation_page_completeness.py` | 5 new PM-58 checks |
| `reports/site/factor-library/factor-evaluation.html` | Rebuilt |
| `docs/factor_library/FACTOR_LIBRARY_CONTROL_CENTER.md` | Added §15 core vs optional boundary |
| `docs/factor_library/POST_INTAKE_WORKFLOW_RUNBOOK.md` | Added §14.6 |
| `docs/factor_library/REGENERATION_CONTRACT.md` | Added §10.8 |
| `docs/factor_library/CAP_DATA_SOURCE_CONTRACT.md` | New: cap source contract |
| `docs/factor_library/FACTOR_EVALUATION_WORKFLOW_BOUNDARY.md` | New: full workflow boundary spec |
| `docs/factor_library/audits/pm58_core_workflow_cleanup_core_vs_optional.md` | New audit |

---

## 4. Page Cleanup Summary

**Before:**
- Paper Portfolio section in main reading flow (between LS charts and Regime)
- Fee Sensitivity chart in main reading flow
- Summary table columns unlabeled

**After:**
- Paper/fee wrapped in `<details class="optional-deep-dive">` (default collapsed)
- Title: "Optional Deep-dive Evidence / 可选深挖证据" with "NOT CORE" badge
- Summary table columns labeled `<span class="optional-label">opt</span>`
- How to Read: Paper/fee removed from main reading order; note added explaining they're in collapsed section
- Reading order now: RankIC → RankIC Robust → LS → LS Robust → Regime → Shape → Capacity → Redundancy → Scorecard → Profile

---

## 5. Core Full-Universe Required (20 diagnostics)

All 84 factors must have ALL of these. Missing = FAIL.

1. registry / FactorSpec
2. factor_values
3. RankIC summary
4. LS summary
5. diagnostics summary
6. shape
7. rolling stability
8. decile
9. capacity
10. regime
11. redundancy
12. scorecard
13. profile
14. bilingual card
15. page payload
16. RankIC robust significance (84×4)
17. LS robust significance (84×4)
18. active workflow consistency
19. all-active integrity QA
20. page QA

---

## 6. Optional Deep-dive (candidate-only, not required)

| Diagnostic | Coverage | Blocks Reading? | Affects Scorecard? |
|-----------|----------|-----------------|-------------------|
| Paper simulation | 5/84 | NO | NO |
| Paper robust | 5/84 | NO | NO |
| Fee sensitivity | 13/84 | NO | NO |
| Fee cost-collapse | 13/84 | NO | NO |

Absence labeled "Not run — optional", NOT "Missing".

---

## 7. Cap Source Contract

- Source: `CAP_POINT_IN_TIME_APPROXIMATE`
- Construction: CoinGecko supply snapshot × Binance price
- Known limitation: look-ahead bias in supply data
- 2 active cap factors: a101_volume_cap_alpha_min_80_80, a101_volume_cap_alpha_min_56_84
- Full contract: `CAP_DATA_SOURCE_CONTRACT.md`

---

## 8. QA Results

```
Consistency checker: 15/15 PASS
Integrity QA (--all-active): PASS (1764 checks)
Page QA: 48/48 PASS (5 new PM-58 checks)
```

New PM-58 checks:
| Check | Status | Evidence |
|-------|--------|----------|
| pm58_optional_section | PASS | Found |
| pm58_opt_label | PASS | opt label found |
| pm58_paper_not_in_reading_order | PASS | Correctly excluded |
| pm58_robust_in_reading_order | PASS | Both present |
| pm58_optional_css | PASS | Found |

---

## 9. No Unauthorized Changes

- No new factors ✓
- No formula changes ✓
- No expected_direction changes ✓
- No factor_values changes ✓
- No cap data changes ✓
- No RankIC/LS calculation changes ✓
- No robust RankIC/LS calculation changes ✓
- No scorecard changes ✓
- No best_horizon changes ✓
- No signal construction ✓
- No trading recommendations ✓

---

## 10. Current Workflow Closure Status

**Active factors:** 84
**Core diagnostics:** All 20 present and PASS
**Robust RankIC:** 84/84 × 4 horizons = 336 rows ✓
**Robust LS:** 84/84 × 4 horizons = 336 rows ✓
**Paper simulation:** 5/84 (optional subset) ✓
**Fee sensitivity:** 13/84 (optional subset) ✓
**Cap source:** APPROXIMATE (documented) ✓

---

## 11. Remaining Limitations

1. Paper simulation only 5/84 (documented optional subset)
2. Fee sensitivity only 13/84 (documented optional subset)
3. Cap source uses current supply snapshot (look-ahead bias documented)
4. No historical supply data for true point-in-time cap

---

## 12. Recommended Next PM

- **PM-59**: Robust diagnostics trend tracking (track robust class changes over time)
- **PM-60**: Historical supply data for true point-in-time cap
