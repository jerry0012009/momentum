# Phase 13A-P1: Factor Evaluation Schema Upgrade — Closeout Summary

**Status:** HISTORICAL_CLOSEOUT. Preserved for audit trail only. Counts and next-step notes may be stale. Use `docs/factor_library/START_HERE.md` and `factor_library_state.md`.

**Phase:** 13A-P1
**Date:** 2026-06-20
**Type:** Evaluator schema upgrade + public page rebuild. No factor expansion. No signal modification.

---

## Changed Files

| File | Action |
|------|--------|
| `scripts/evaluate_factors.py` | Modified — added metric panel, period IC, quantile returns, long-short, formula catalog outputs; fixed `computed_factors` count (37→47); upgraded `rank_ic_from_boundaries` to return valid timestamp indices |
| `scripts/_build_factor_eval_html.py` | **Full rewrite** — reads new metric panel CSV; adds ICIR, win rate, long-short, period stability, missing factors, active-in-signal sections |
| `reports/site/factor-library/factor-evaluation.html` | Regenerated — 89KB, bilingual methodology, correct counts (53/47/6/10), diagnostic sections |
| `reports/site/factor-library/actual-script-map.html` | Modified — updated Phase 13 disclaimer wording |

## New Output Files (under `factor_level_evaluation/`)

| File | Rows | Description |
|------|------|-------------|
| `factor_level_metric_panel.csv` | 212 (53×4) | Per-factor × horizon: IC, ICIR, t-stat, win rates, coverage, long-short |
| `factor_level_metric_panel.json` | — | JSON version of above |
| `factor_level_period_ic_summary.csv` | 4700 | Monthly period IC: stability per factor × horizon × month |
| `factor_level_quantile_return_summary.csv` | 940 | 5-bucket quantile returns per factor × horizon |
| `factor_level_long_short_summary.csv` | 188 | Direction-adjusted long-short spread per factor × horizon |
| `factor_level_formula_catalog.csv` | 53 | One row per registered factor with metadata |

## Metrics Added

- **ICIR** (IC Information Ratio): mean(raw RankIC) / std(raw RankIC)
- **IC Win Rate** (raw + adjusted): share of timestamps where IC > 0
- **Long-Short Spread**: top bucket - bottom bucket return, with t-stat and win rate
- **Period Stability**: monthly IC aggregation for temporal consistency assessment
- **Quantile Bucket Returns**: 5-bucket diagnostic return profile
- **Coverage / Missing Rate**: factor value availability

## Validation Commands Run

| Command | Result |
|---------|--------|
| `python scripts/evaluate_factors.py --factor-ids rev_3h --output-suffix phase13a_p1_smoke` | PASS (52s) |
| `python scripts/evaluate_factors.py` (full run) | PASS (33min 20s) |
| `python scripts/check_factor_ic_parity.py` | 10/10 PASS, max diff=0.00e+00 |
| `python scripts/build_factor_catalog.py` | PASS (53 factors) |
| `python scripts/check_factor_catalog_integrity.py` | PASS |
| `python scripts/audit_factor_direction_semantics.py` | PASS (53 factors) |
| `python scripts/_build_factor_eval_html.py` | PASS (89KB output) |
| `grep "37 computed"` | NO MATCH (stale count removed) |
| `grep "47 computed"` | Line 38 confirmed |
| `grep "ICIR"` | Lines 58, 76, 105 confirmed |
| `grep "win rate"` | Line 163 confirmed |
| `grep "long-short"` | Line 163 confirmed |
| `grep "production ready\|tradeable alpha\|live trading"` | Only disclaimers (NOT production) |

## Known Limitations

1. **Runtime:** Full evaluation now takes ~33 min (was ~15 min). Vectorized quantile computation adds overhead per factor × horizon.
2. **Period IC uses raw timestamps:** Month grouping relies on `pd.Timestamp(ts).strftime("%Y-%m")` which assumes timestamp format compatibility.
3. **formula_proxy is notes-based:** Uses `FactorSpec.notes` as formula proxy, not canonical DSL. This is explicitly documented.
4. **Long-short is diagnostic only:** Direction-adjusted sorting for long-short spread does not account for transaction costs, slippage, or position sizing.

## Intentionally Not Changed

- `scripts/factor_formula_registry.py` — read-only inspection only
- `scripts/build_phase9b_signal_panel.py` — not touched
- `scripts/evaluate_signals.py` — not touched
- `data/cache/` — not touched
- `data/features/*.parquet` — not modified (only read)
- No new factors added
- No signal construction modified
- No labels modified
- No raw data modified

## Next Recommended Phase

**Phase 13A-P2 — Factor Expansion Sprint 1**
