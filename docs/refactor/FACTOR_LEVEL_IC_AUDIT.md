# Factor-Level IC Audit

**Phase:** 12D-H8  
**Date:** 2026-06-19  
**Auditor:** automated  

---

## 1. Old Factor Evaluator Audit

### evaluate_factors_dynamic_universe.py

- **Exists:** YES (`scripts/evaluate_factors_dynamic_universe.py`)
- **Status:** STALE / BROKEN
- **Reason:** Imports `evaluate_factors.py` which does NOT exist (`from evaluate_factors import evaluate_one_label`). Cannot run.
- **Historical outputs location:** `reports/artifacts/factor_eval_dynamic/`
- **Historical outputs exist:** YES — `factor_eval_dynamic_summary.csv` with 9 factors only
- **Historical outputs usable:** NO
  - Only covers 9 factors (ema_12_26_gap, rsi_28h, rsi_7h, williams_r_14h, + 5 others)
  - Does not align with current 53-factor registry
  - Uses stale universe (unknown which list)
  - Uses stale labels (unknown provenance)
  - Missing module dependency makes it non-reproducible

### evaluate_factors.py (canonical)

- **Existed before H8:** NO
- **Created in H8:** YES (`scripts/evaluate_factors.py`, 291 lines)
- **Approach:** Uses factor_formula_registry.py for metadata, direct RankIC computation (Spearman) per factor × horizon
- **API alignment:** Does NOT use `momentum.signal_evaluation.compute_rank_ic` directly (too slow due to pivot_table on 3.3M rows). Instead uses equivalent boundary-based Spearman computation: rank per timestamp group → Pearson of ranks = Spearman
- **Direction adjustment:** positive→raw, negative→-raw, conditional→raw (DIRECTION_UNKNOWN)

### evaluate_factors.py vs evaluate_signals.py

| Aspect | evaluate_factors.py | evaluate_signals.py |
|--------|---------------------|---------------------|
| Level | Single-factor IC | Signal-level (combined) RankIC |
| Input | factor_values.parquet per factor | signal_panel.parquet (composite) |
| API | Direct Spearman | momentum.signal_evaluation.compute_rank_ic |
| Output | factor_level_rankic_summary.csv | signal_eval_rankic_summary.csv |
| Horizons | 1h, 4h, 24h, 72h | 1h, 4h, 24h, 72h |

---

## 2. Factor-Level Evaluation Results

- **Total registered factors:** 53
- **Factors with factor_values.parquet:** 47
- **Factors computed (IC):** 47 (37 COMPUTED + 10 DIRECTION_UNKNOWN)
- **Missing factor_values:** 6 (taker_buy_ratio_20h, taker_buy_zscore_20h, taker_buy_delta_5h, funding_rate_level_20h, funding_rate_zscore_80h, funding_rate_change_24h)
- **Active in current signal:** 10 factors (all computed)

### Top 10 by Direction-Adjusted IC (1h)

| Rank | Factor | Adj IC (1h) | t-stat | Direction | In Signal |
|------|--------|-------------|--------|-----------|-----------|
| 1 | volatility_20h | +0.038757 | -24.05 | negative | no |
| 2 | vol_40h | +0.038413 | -23.57 | negative | ★ |
| 3 | vol_5h | +0.033743 | -23.37 | negative | ★ |
| 4 | bb_zscore_20h | +0.030498 | -29.53 | negative | no |
| 5 | rsi_7h | +0.030476 | -29.24 | negative | ★ |
| 6 | vol_of_vol_20h | +0.030274 | -22.22 | negative | ★ |
| 7 | downside_vol_20h | +0.028863 | -18.16 | negative | ★ |
| 8 | rsi_14h | +0.027985 | -26.52 | negative | no |
| 9 | rsi_28h | +0.025330 | -23.82 | negative | ★ |
| 10 | qvol_ma_ratio_5_20 | -0.005393 | -6.22 | positive | no |

All 10 signal factors have computed IC. The current signal panel is predominantly negative-direction volatility/RSI factors.

---

## 3. Recommended Actions

1. **Keep the new evaluator as canonical.** The old `evaluate_factors_dynamic_universe.py` should be treated as legacy/reference only.
2. **Do NOT use old outputs.** The 9-factor dynamic summary is stale and non-reproducible.
3. **Factor-level IC is NOT signal-level IC.** Low-IC factors can combine into effective signals; high-IC factors can fail in combination.
4. **Missing FV factors need Phase 9B data pipeline extension** to generate taker_buy_ratio, taker_buy_zscore, taker_buy_delta, and funding_rate factor values.
5. **Continue paper diagnostic.** No tradeable alpha claim.

---

*This audit is part of Phase 12D-H8 deliverables.*
