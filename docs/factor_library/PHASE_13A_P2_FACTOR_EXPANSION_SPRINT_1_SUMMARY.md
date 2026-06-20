# Phase 13A-P2: Factor Expansion Sprint 1 — Closeout Summary

**Status:** HISTORICAL_CLOSEOUT. Preserved for audit trail only. New factor work now uses `scripts/run_factor_intake.py`; do not reuse the older sprint directory pattern as the default workflow.

**Phase:** 13A-P2
**Date:** 2026-06-20
**Type:** First controlled OHLCV factor expansion. Not production. Not live trading.

---

## New Factors (12)

| # | factor_id | family | expected_direction | required_columns | lookback |
|---|-----------|--------|--------------------|------------------|----------|
| 1 | mom_72h | momentum | positive | close | 72 |
| 2 | mom_120h | momentum | positive | close | 120 |
| 3 | rev_1h | reversal | positive | close | 1 |
| 4 | rev_72h | reversal | positive | close | 72 |
| 5 | vol_ratio_20_80 | volatility | conditional | close | 81 |
| 6 | realized_skew_20h | realized_shape | conditional | close | 21 |
| 7 | realized_kurt_20h | realized_shape | conditional | close | 21 |
| 8 | amihud_illiquidity_20h | liquidity | negative | close, quote_volume | 21 |
| 9 | qvol_ma_ratio_20_80 | quote_volume_liquidity | conditional | quote_volume | 80 |
| 10 | price_volume_corr_20h | volume_price | conditional | close, quote_volume | 21 |
| 11 | trend_efficiency_24h | trend_quality | positive | close | 24 |
| 12 | price_pos_120h | price_position | conditional | high, low, close | 120 |

**Duplicate candidates skipped:** None. All 12 were unique.

## Expected vs Actual Counts

| Metric | Expected | Actual |
|--------|----------|--------|
| Registered factors | 65 | 65 ✓ |
| Computed factors | 59 | 59 ✓ |
| Missing factor_values | 6 | 6 ✓ (taker/funding) |
| Active in signal | 10 | 10 ✓ |

## Changed Files

| File | Action |
|------|--------|
| `scripts/factor_formula_registry.py` | Modified — 12 compute functions + 12 FactorSpec entries + rolling_sum import + terminology fix |
| `scripts/evaluate_factors.py` | Modified — terminology fix (production signal → current research signal panel) |
| `reports/site/factor-library/factor-evaluation.html` | Regenerated (135KB) |
| All canonical evaluation CSVs | Regenerated |

## Commands Run

| Command | Runtime | Result |
|---------|---------|--------|
| `check_factor_registry_integrity.py` | <1s | PASS (65 factors, 12 BUILDABLE) |
| `build_factor_values.py --factor-ids <12 new>` | ~60s | PASS (12/12, coverage ≥ 97%) |
| `evaluate_factors.py --factor-ids <12 new> --output-suffix phase13a_p2_new_factors` | 516s | PASS (12/12 computed) |
| `evaluate_factors.py` (full) | 2581s (43m40s) | PASS (65/59/6/10) |
| `check_factor_ic_parity.py` | ~400s | 10/10 PASS |
| `build_factor_catalog.py` | <10s | PASS (65 factors) |
| `check_factor_catalog_integrity.py` | <5s | PASS |
| `audit_factor_direction_semantics.py` | <5s | PASS |
| `_build_factor_eval_html.py` | <5s | PASS (135KB) |

## Top New Factors by Adjusted IC (1h)

| factor_id | adj_ic | t-stat | direction |
|-----------|--------|--------|-----------|
| rev_1h | +0.036506 | 30.69 | positive |
| rev_72h | +0.015832 | 12.76 | positive |
| price_volume_corr_20h | -0.021736 | -15.26 | conditional |
| mom_72h | -0.015832 | -12.76 | positive |
| price_pos_120h | -0.012662 | -9.04 | conditional |
| realized_skew_20h | -0.011817 | -10.41 | conditional |
| mom_120h | -0.011908 | -9.35 | positive |

## Top New Factors by Adjusted ICIR (1h)

| factor_id | adj_icir | direction |
|-----------|----------|-----------|
| rev_1h | +0.2300 | positive |
| price_volume_corr_20h | -0.1896 | conditional |
| realized_skew_20h | -0.1028 | conditional |
| mom_72h | -0.0958 | positive |
| rev_72h | +0.0958 | positive |
| price_pos_120h | -0.0903 | conditional |

## Long-Short Conflicts

- **mom_72h / mom_120h:** Negative adjusted IC but positive expected direction → direction may need review (momentum reversal at these horizons).
- **rev_1h / rev_72h:** Strong positive adjusted IC, consistent with reversal hypothesis.
- **price_volume_corr_20h:** Strong negative IC — price-volume decorrelation predicts returns.

## Quality Check CSV
`research/factor_runs/crypto_top50_factor_library/factor_expansion_sprint_1/new_factor_quality_checks.csv`
26 checks: **26 PASS, 0 FAIL**

## Known Limitations

1. Full evaluation runtime increased to 43m40s (from 34m with 53 factors).
2. mom_72h/mom_120h show negative adjusted IC — direction conflict with positive expected_direction. Needs review in Phase 13A-P3.
3. No factors added to signal panel. All new factors are DIAGNOSTIC_PROBE status.
4. Candidate review terminology fix applied ("current research signal panel" instead of "production signal").

## Judgment: **PASS**

## Next Recommended Phase

**Phase 13A-P3 — Factor Redundancy and Candidate Selection Review**
