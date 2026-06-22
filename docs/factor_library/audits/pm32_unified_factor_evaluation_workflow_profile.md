# PM-32: Unified Factor Evaluation Workflow Profile

**Date:** 2026-06-22
**Follows:** PM-31B (cluster language repair)

---

## Summary Verdict

**`UNIFIED_FACTOR_EVALUATION_WORKFLOW_PASS`**

## 1. Why PM-32

PM-32 formalizes a reusable factor evaluation workflow contract and unified per-factor profile layer. It answers:
- **Workflow question:** What exact evaluation stages must run after a new factor is introduced?
- **Interpretation question:** What does the system say about this factor across all diagnostic dimensions?

This is still factor evaluation, not signal construction.

## 2. Files Changed

- `scripts/build_unified_factor_profile.py` (new, 58KB)
- `scripts/run_factor_library_refresh.py` (added 'profile' stage)
- `docs/factor_library/REGENERATION_CONTRACT.md` (added profile pipeline step)
- 8 output files in `factor_diagnostics/`
- `docs/factor_library/audits/pm32_unified_factor_evaluation_workflow_profile.md` (new)

## 3. Workflow Contract

- 21 stages defined
- Covers: registry → values → evaluation → diagnostics → redundancy → cluster → profile → page → state
- Each stage has: stage_id, display_name_zh/en, script, is_expensive, inputs, outputs, must_run_after, what_it_answers_zh/en

## 4. Evidence Matrix

- 71/71 factors: COMPLETE
- Mean evidence completeness: 100%
- All 16 evidence blocks present for all factors

## 5. Factor Coverage

- Expected: 71
- Profile: 71
- Component scores: 71
- Evidence matrix: 71
- Payload: 71
- Missing: 0

## 6. Profile Class Distribution

| Class | Count |
|---|---:|
| BROAD_WATCHLIST | 67 |
| UNIQUE_BUT_WEAK | 4 |

## 7. Research Action Distribution

| Action | Count |
|---|---:|
| LOWER_PRIORITY_REVIEW | 59 |
| WATCH_FOR_STABILITY_RISK | 8 |
| KEEP_AS_DIAGNOSTIC_PROBE | 4 |

## 8. Component Weights

| Component | Weight |
|---|---:|
| standalone_quality | 18% |
| paper | 14% |
| stability | 14% |
| regime | 10% |
| shape | 10% |
| cost | 8% |
| capacity | 8% |
| redundancy | 8% |
| marginal_info | 7% |
| evidence_completeness | 3% |

## 9. Workflow Integration

✅ Stage 'profile' added to `run_factor_library_refresh.py`
✅ `REGENERATION_CONTRACT.md` updated with profile pipeline step
✅ `--stage profile --dry-run` passes

## 10. Forbidden Language Check

All outputs PASS — no trading/deletion/allocation language.

## 11. Validation

- py_compile: ✅
- Script execution: ✅
- Workflow dry-run: ✅
- Forbidden language: ✅

## 12. Limitations

1. Most factors (67/71) classified as BROAD_WATCHLIST — scoring may need refinement
2. Component weights are default, not calibrated
3. Staleness monitor not yet updated for profile outputs (deferred to PM-33)

## 13. Non-Change Statement

No factors, formulas, factor_values, signal panel, public page modified.

## 14. Recommended Next PM

**PM-33:** Unified profile page integration and workflow-readiness presentation.
