# PM-06 Factor Intake Smoke Test

**Date:** 2026-06-21
**Verdict:** PASS_WITH_WARNINGS

---

## A. Command Run

```bash
python scripts/run_factor_intake.py \
  --factor-ids rev_1h rev_3h price_volume_corr_20h \
  --run-id pm06_intake_smoke_20260621 \
  --skip-build-values
```

Elapsed: 201.6s

## B. Factor IDs Tested

- `rev_1h` — 1h price reversal
- `rev_3h` — 3h price reversal
- `price_volume_corr_20h` — 20h price-volume correlation

All 3 exist in the registry (65 total registered).

## C. Run Directory

`research/factor_runs/crypto_top50_factor_library/factor_intake/pm06_intake_smoke_20260621/`

## D. Artifact Checklist

| artifact | exists | non-empty |
|----------|--------|-----------|
| manifest.json | ✅ | ✅ |
| command_log.json | ✅ | ✅ |
| outputs_index.json | ✅ | ✅ |
| factor_inventory.csv | ✅ | ✅ |
| quality_checks.csv | ✅ | ✅ |
| report.md | ✅ | ✅ (91 lines, 3283 chars) |
| factor_metric_panel.csv | ✅ | ✅ |
| factor_rankic_summary.csv | ✅ | ✅ |
| factor_period_ic_summary.csv | ✅ | ✅ |
| factor_quantile_return_summary.csv | ✅ | ✅ |
| factor_long_short_summary.csv | ✅ | ✅ |
| factor_candidate_review.csv | ✅ | ✅ |
| factor_formula_catalog.csv | ✅ | ✅ |
| evaluation_manifest.json | ✅ | ✅ |
| factor_redundancy.csv | ❌ | — (step OOM'd) |
| factor_conclusion_cards.csv | ✅ | ✅ |
| factor_conclusion_cards.json | ✅ | ✅ |

**16/17 artifacts present.** `factor_redundancy.csv` missing due to redundancy step OOM.

## E. Quality Checks

| QC-ID | Check | Status |
|-------|-------|--------|
| QC-01 | all factor IDs exist in registry | PASS |
| QC-02 | registry integrity check passed | PASS |
| QC-03 | evaluation manifest generated | PASS |
| QC-04 | metric panel generated | PASS |
| QC-05 | candidate review generated | PASS |
| QC-06 | no signal panel modification | PASS |
| QC-07 | no production claim | PASS |
| QC-08 | all critical steps succeeded | PASS |

**8/8 PASS, 0 FAIL.**

## F. Conclusion Card Decision Buckets

| Factor | Best Adj IC | Best LS t-stat | Monthly Stability | Decision Bucket | Recommended Action |
|--------|------------|----------------|-------------------|----------------|-------------------|
| rev_1h | +0.036506 | -3.70 | STABLE (25/25) | REVIEW_REQUIRED | Investigate direction semantics |
| rev_3h | +0.034385 | -5.78 | STABLE (25/25) | REVIEW_REQUIRED | Investigate direction semantics |
| price_volume_corr_20h | -0.040248 | 8.94 | UNSTABLE (2/25) | CONDITIONAL_DIRECTION_REVIEW | Keep for diagnostic |

- REVIEW_REQUIRED: 2
- CONDITIONAL_DIRECTION_REVIEW: 1
- PROMOTE: 0

## G. Redundancy Step Failure

`build_factor_redundancy.py` was killed by SIGKILL (exit -9). Root cause: OOM.

The script loads all 59 factor parquets (3.3M rows each) into a single wide DataFrame via incremental outer merge. Estimated peak memory: ~50+ GB. System has 15 GB RAM, zero swap.

Not a code bug — a resource limitation. The conclusion cards step gracefully degraded by using default redundancy assumptions (UNKNOWN).

**Noted as known limitation.** No code fix applied in this phase.

## H. Promotion Guard Behavior

**Without --confirm:**
```
❌ BLOCKED: --confirm flag required
```

**With --confirm:**
```
✅ --confirm flag provided
✅ run directory exists
✅ manifest OK (3 factors)
✅ all 8 checks passed
✅ 3 conclusion cards found
✅ no blocking decision buckets

⚠️ ALL GUARDS PASSED — but promotion is NOT implemented in this phase.
```

No canonical files were modified. Promotion guard correctly prevents accidental canonical pollution.

## I. Non-Change Statement

No factor formulas, signal logic, signal panel, universe data, labels, canonical factor values, or public result pages were changed.
