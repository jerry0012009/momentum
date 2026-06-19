# Factor-Level IC Evaluation

**Phase:** 12D-H8  
**Generated:** 2026-06-19  
**Dataset:** crypto_top50_factor_library  
**Method:** RankIC (Spearman) — rank per timestamp, Pearson of ranks

---

## Summary

- **Total registered:** 53 factors
- **Computed IC:** 47 factors (37 COMPUTED + 10 DIRECTION_UNKNOWN)
- **Missing factor_values:** 6 (taker/funding rate factors)
- **Active in current signal:** 10 factors (all computed)
- **Horizons evaluated:** 1h, 4h, 24h, 72h

## Method

Each factor's values are loaded from `factor_values.parquet`, merged with forward return labels, ranked per timestamp using Spearman (rank → Pearson of ranks), and aggregated into per-horizon IC summaries.

Direction adjustment: `positive → raw IC`, `negative → -raw IC`, `conditional → raw IC` (status: DIRECTION_UNKNOWN).

## Top 10 by Direction-Adjusted IC (1h)

1. volatility_20h: +0.0388 (negative, t=-24.05)
2. vol_40h: +0.0384 (negative, ★ signal)
3. vol_5h: +0.0337 (negative, ★ signal)
4. bb_zscore_20h: +0.0305 (negative, t=-29.53)
5. rsi_7h: +0.0305 (negative, ★ signal)
6. vol_of_vol_20h: +0.0303 (negative, ★ signal)
7. downside_vol_20h: +0.0289 (negative, ★ signal)
8. rsi_14h: +0.0280 (negative, t=-26.52)
9. rsi_28h: +0.0253 (negative, ★ signal)
10. qvol_ma_ratio_5_20: -0.0054 (positive, t=-6.22)

## Output Files

- `research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_rankic_summary.csv` — Full factor × horizon IC table
- `research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_rankic_summary.json` — Same as JSON
- `research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_coverage_summary.csv` — Per-factor coverage and status
- `research/factor_runs/crypto_top50_factor_library/factor_level_evaluation/factor_level_evaluation_manifest.json` — Metadata

## Script

- `scripts/evaluate_factors.py` — Canonical factor-level evaluator

## Important

- Factor-level IC ≠ signal-level RankIC
- Low IC factors can combine into effective signals
- Not a tradeable strategy. Paper diagnostic only.
- Phase 13 NOT STARTED.

---

*Part of Phase 12D-H8 deliverables.*
