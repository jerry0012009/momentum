# Cleanup Recommendations

**Status:** ACTIVE cleanup guidance for factor-library portal hygiene
**Generated:** 2026-06-19

---

## Immediate Recommendations

1. **Keep all active mainline scripts as-is.** No changes needed.
2. **Keep the public factor-library nav to 4 pages.** The active pages are `index.html`, `actual-script-map.html`, `factor-evaluation.html`, and `signal-evaluation-summary.html`.
3. **Keep all evaluation outputs as-is.** They are current and valid.
4. **Keep `evaluate_factors_dynamic_universe.py` in scripts/ as DEPRECATED_STALE / HISTORICAL_REFERENCE.** Do not delete, do not move, do not re-enable. It is evidence of the old evaluator design. Canonical evaluator: `scripts/evaluate_factors.py`.

## Deferred Recommendations

1. **Move root-level `PHASE_12D_*.md` files to `docs/phase_closeout/`.** These are phase closeout docs that belong in docs/, not root. Low urgency.
2. **Review `scripts/compare_static_dynamic_factor_evals.py`.** Decide whether to update for new evaluator or archive.
3. **Review `scripts/audit_dynamic_universe_*.py`.** Decide if dynamic universe pipeline is still relevant.
4. **Review `scripts/build_crypto_native_factor_values.py`.** Check if any registered factors depend on it.

## Do NOT Do

1. **Do not delete `archive/legacy_phase_scripts/phase10/`.** These are historical evidence.
2. **Do not delete `reports/site/factor-library/_archive/`.** These are historical site pages.
3. **Do not delete `docs/factor_library_transparency/`.** These are historical transparency docs. Keep them archived/superseded; do not use them as current entry points.
4. **Do not delete `research/.../alphalens_exports/`.** Historical evidence.
5. **Do not move or rename `scripts/evaluate_factors.py`.** It is the canonical evaluator.
6. **Do not modify any research outputs.** Factor values, signal panels, evaluation results are all current.

## Content Safe to Archive (Do Not Delete)

- `scripts/export_alphalens_factor_data.py` → archive
- `scripts/run_alphalens_smoke_check.py` → archive
- `scripts/evaluate_factors_dynamic_universe.py` → DEPRECATED_STALE / HISTORICAL_REFERENCE (keep in place)
- Root `PHASE_12D_*.md` files → move to docs/phase_closeout/
- Old portal docs (`docs/DOCS_INDEX.md`, `docs/FACTOR_LIBRARY_HOME.md`, `docs/factor_library_transparency/`) → keep as redirects/historical archive, not active planning authority

## Needs Human Decision

1. **Dynamic universe pipeline:** Is `scripts/build_dynamic_universe_*.py` still needed? Should it be integrated into mainline or archived?
2. **Crypto-native factors:** Should `scripts/build_crypto_native_factor_values.py` be part of the main factor building pipeline?
3. **Alphalens integration:** Should we revive Alphalens for factor screening, or is it permanently archived?
4. **Root-level phase docs:** Should they be moved to docs/ or left in root?

## Scope Note

This document covers the factor library research pipeline only. It is not a full momentum repository inventory. Strategy research scripts (~440 files), historical experiments, and non-factor-library files are not individually listed here.

## Potential Future Directions (Not Recommendations)

- Factor intake: continue using `scripts/run_factor_intake.py`
- Dynamic universe integration: review only if it becomes active again
- Crypto-native data integration: review only after required data exists
