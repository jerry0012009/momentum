# PM-49: Factor Interpretation / Research Review — Audit

**Date**: 2026-06-23
**PM**: PM-49
**Verdict**: `PM49_FACTOR_INTERPRETATION_REVIEW_PASS`

---

## Summary

对 7 个近期新增因子进行了基于 Factor Evaluation Layer v0.1 证据的完整研究解释和质量判断。
无公式、factor_values、signal panel、expected_direction 修改。
无交易建议。仅研究诊断。

---

## Research Decision Table

| Factor | Decision | Direction Status | Score | Key Finding |
|--------|----------|-----------------|-------|-------------|
| rev_2h | LOWER_PRIORITY_REVIEW | DIRECTION_ALIGNED | 49.85 | IC强但LS薄，成本敏感 |
| mom_vol_adjusted_20h | FORMULA_REVIEW_REQUIRED | EXPECTED_DIRECTION_CONFLICT | 44.64 | IC全部为负 |
| range_breakout_vol_confirm_20h | FORMULA_REVIEW_REQUIRED | EXPECTED_DIRECTION_CONFLICT | 37.53 | IC全部为负，BTC beta敏感 |
| volume_pressure_20h | DIRECTION_REVIEW_REQUIRED | EXPECTED_DIRECTION_CONFLICT | 47.69 | IC全部为负 |
| xs_rank_mom_accel | DIRECTION_REVIEW_REQUIRED | EXPECTED_DIRECTION_CONFLICT | 47.99 | IC全部为负 |
| up_down_vol_ratio_20h | DIRECTION_REVIEW_REQUIRED | EXPECTED_DIRECTION_CONFLICT | 44.64 | IC全部为负 |
| clv_20h | CANDIDATE_POOL_WATCHLIST | SHORT_HORIZON_REVERSAL | 51.90 | 72h IC对齐，信息独特 |

---

## Direction Review Table

| Factor | Expected | Empirical (best h) | Status | Severity |
|--------|----------|-------------------|--------|----------|
| rev_2h | positive | positive (1h) | ALIGNED | NONE |
| mom_vol_adjusted_20h | positive | negative (4h) | CONFLICT | HIGH |
| range_breakout_vol_confirm_20h | positive | negative (24h) | CONFLICT | HIGH |
| volume_pressure_20h | positive | negative (24h) | CONFLICT | MEDIUM |
| xs_rank_mom_accel | positive | negative (4h) | CONFLICT | HIGH |
| up_down_vol_ratio_20h | positive | negative (4h) | CONFLICT | HIGH |
| clv_20h | positive | positive (72h) | REVERSAL | LOW |

---

## 最值得保留的因子

- **clv_20h**: CANDIDATE_POOL_WATCHLIST。72h RankIC = +0.018 (t=18.5)，机制清晰，信息独特。
- **rev_2h**: LOWER_PRIORITY_REVIEW。IC 方向完全对齐（1h t=29.8），但 LS 薄且成本敏感。

## 需要方向/公式复核的因子

- mom_vol_adjusted_20h: IC 全部为负，需复核 expected_direction 或公式
- range_breakout_vol_confirm_20h: IC 全部为负，突破信号在 crypto 中可能是 exhaustion
- volume_pressure_20h: IC 全部为负，expected_direction 可能需要反转
- xs_rank_mom_accel: IC 全部为负，deceleration 可能才是预测信号
- up_down_vol_ratio_20h: IC 全部为负，bear dependent

## 只是 Diagnostic 的因子

- rev_2h: COST_COLLAPSED，不适合独立使用，可作 baseline 对比

## 可能进入 Future Candidate Pool 的因子

- clv_20h: 唯一方向对齐的因子，需进一步验证 regime stability

---

## Output Files

| File | Description |
|------|-------------|
| `docs/factor_library/reviews/PM49_RECENT_FACTOR_INTERPRETATION_REVIEW.md` | 完整研究解释报告 |
| `factor_diagnostics/recent_factor_interpretation_review.csv` | 7 因子评价汇总 CSV |
| `factor_diagnostics/recent_factor_interpretation_review.json` | 7 因子评价汇总 JSON |
| `factor_diagnostics/factor_direction_semantics_review.csv` | 方向语义复核 CSV |
| `factor_diagnostics/factor_direction_semantics_review.json` | 方向语义复核 JSON |

---

## No Out-of-Scope Changes

| Check | Status |
|-------|--------|
| No formula changes | ✅ |
| No expected_direction changes | ✅ |
| No factor_values changes | ✅ |
| No signal panel changes | ✅ |
| No trading recommendations | ✅ |

---

## Remaining Limitations

1. LS 聚合字段（Sharpe, Ann Return, Max DD）在 canonical 文件中大部分为 NaN，限制了 LS 层面的深入分析
2. Rolling stability 和 capacity 数据不足（INSUFFICIENT_HISTORY）
3. 无 paper portfolio 详细诊断（大部分因子 PAPER_MIXED）
4. 方向复核基于 RankIC，未考虑 regime conditional effects

---

## Recommended Next PM

**PM-50**: 方向复核实施
- 对 5 个 EXPECTED_DIRECTION_CONFLICT 因子进行 expected_direction 修正
- 或公式调整（如改为 negative expected_direction）
- 或公式修正（如修改公式逻辑使其与 positive expected_direction 对齐）

**Alternative**: PM-50 — v0.1 tag + deployment hardening
