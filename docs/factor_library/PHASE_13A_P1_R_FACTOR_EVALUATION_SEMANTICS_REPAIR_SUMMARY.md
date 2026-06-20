# Phase 13A-P1-R: Factor Evaluation Semantics Repair — Closeout Summary

**Status:** HISTORICAL_CLOSEOUT. Preserved for audit trail only. Use current generated artifacts and `START_HERE.md` for active workflow.

**Phase:** 13A-P1-R
**Date:** 2026-06-20
**Type:** Semantics repair — ICIR split, metadata fill, candidate review.

---

## What Was Repaired

1. **ICIR split:** Added `raw_icir` and `direction_adjusted_icir` columns. For negative-direction factors, raw ICIR is negative while adjusted ICIR is positive (matching adjusted IC). The public page now displays adjusted ICIR by default.

2. **Metadata fill:** `required_columns` and `lookback_window` now populated from `FactorSpec` via `factor_formula_registry.py`. Previously empty.

3. **Candidate review:** New `factor_level_candidate_review.csv` — one row per factor, bucketed into ACTIVE_IN_SIGNAL_REVIEW, STRONG_DIAGNOSTIC_CANDIDATE, RANKIC_STRONG_LONGSHORT_WEAK, CONDITIONAL_DIRECTION_REVIEW, MISSING_INPUT, WEAK_OR_NOISY, etc.

## Changed Files

| File | Action |
|------|--------|
| `scripts/evaluate_factors.py` | Modified — added raw_icir/adjusted_icir, required_columns, lookback_window, candidate review output |
| `scripts/_build_factor_eval_html.py` | Modified — displays adjusted ICIR by default, Candidate Review section, ICIR methodology note |
| `reports/site/factor-library/factor-evaluation.html` | Regenerated (113KB) |

## New/Updated Output Files

| File | Rows | Description |
|------|------|-------------|
| `factor_level_metric_panel.csv` | 212 | +4 new columns: raw_icir, direction_adjusted_icir, raw_rank_ic_std, direction_adjusted_rank_ic_std, required_columns, lookback_window |
| `factor_level_period_ic_summary.csv` | 4700 | +raw_icir, direction_adjusted_icir, raw_rank_ic_std, direction_adjusted_rank_ic_std |
| `factor_level_candidate_review.csv` | 53 | New: one row per factor with review_bucket classification |
| `factor_level_evaluation_manifest.json` | — | +ICIR definitions, candidate_review_output, metadata sources |

## Validation Commands

| Command | Result |
|---------|--------|
| `evaluate_factors.py` (full) | PASS — 34min 20s |
| `check_factor_ic_parity.py` | 10/10 PASS |
| `build_factor_catalog.py` | PASS |
| `check_factor_catalog_integrity.py` | PASS |
| `audit_factor_direction_semantics.py` | PASS |
| `_build_factor_eval_html.py` | PASS (113KB) |
| `grep "direction-adjusted ICIR"` | Lines 239-240 |
| `grep "Candidate Review"` | Line 163 |
| `grep "production ready\|tradeable alpha\|live trading"` | Only disclaimers |

## Quality Check CSV
`research/factor_runs/crypto_top50_factor_library/phase13a_p1_r_factor_eval_semantics_quality_checks.csv`
23 checks: **23 PASS, 0 FAIL**

## Known Limitations

1. Full evaluation runtime ~34 min (slight increase from P1's 33 min due to candidate review computation).
2. `rank_ic_std` column renamed to `raw_rank_ic_std` — backward-incompatible column rename.
3. Candidate review bucketing uses simple thresholds (|IC| >= 0.02, |LS t| >= 2.0) — not optimized.

## Intentionally Not Changed

- No factor formulas modified
- No signal construction modified
- No labels/raw data/parquet modified
- No new factors added
- No evaluator vectorization

## Judgment: **PASS**

## Next Recommended Phase

**Phase 13A-P2 — Factor Expansion Sprint 1**
