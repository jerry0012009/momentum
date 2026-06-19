# Cleanup Recommendations

**Phase:** 12D-H9  
**Generated:** 2026-06-19

---

## Immediate Recommendations

1. **Keep all active mainline scripts as-is.** No changes needed.
2. **Keep all public pages as-is.** The 4-page public nav is correct and minimal.
3. **Keep all evaluation outputs as-is.** They are current and valid.
4. **Keep `evaluate_factors_dynamic_universe.py` in scripts/ but mark as stale.** Do not delete — it is evidence of the old evaluator design.

## Deferred Recommendations

1. **Move root-level `PHASE_12D_*.md` files to `docs/phase_closeout/`.** These are phase closeout docs that belong in docs/, not root. Low urgency.
2. **Review `scripts/compare_static_dynamic_factor_evals.py`.** Decide whether to update for new evaluator or archive.
3. **Review `scripts/audit_dynamic_universe_*.py`.** Decide if dynamic universe pipeline is still relevant.
4. **Review `scripts/build_crypto_native_factor_values.py`.** Check if any registered factors depend on it.

## Do NOT Do

1. **Do not delete `archive/legacy_phase_scripts/phase10/`.** These are historical evidence.
2. **Do not delete `reports/site/factor-library/_archive/`.** These are historical site pages.
3. **Do not delete `docs/factor_library_transparency/`.** These are active supporting docs.
4. **Do not delete `research/.../alphalens_exports/`.** Historical evidence.
5. **Do not move or rename `scripts/evaluate_factors.py`.** It is the canonical evaluator.
6. **Do not modify any research outputs.** Factor values, signal panels, evaluation results are all current.

## Content Safe to Archive (Do Not Delete)

- `scripts/export_alphalens_factor_data.py` → archive
- `scripts/run_alphalens_smoke_check.py` → archive
- `scripts/evaluate_factors_dynamic_universe.py` → archive (mark as stale)
- Root `PHASE_12D_*.md` files → move to docs/phase_closeout/

## Needs Human Decision

1. **Dynamic universe pipeline:** Is `scripts/build_dynamic_universe_*.py` still needed? Should it be integrated into mainline or archived?
2. **Crypto-native factors:** Should `scripts/build_crypto_native_factor_values.py` be part of the main factor building pipeline?
3. **Alphalens integration:** Should we revive Alphalens for factor screening, or is it permanently archived?
4. **Root-level phase docs:** Should they be moved to docs/ or left in root?

## Potential Future Directions (Not Recommendations)

- **H10:** Signal composition review (how 10 factors combine into signals)
- **H11:** Dynamic universe integration (if needed)
- **H12:** Crypto-native factor integration (taker + funding)
- **H13:** Phase 13 readiness assessment
