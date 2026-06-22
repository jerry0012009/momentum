# PM-40C: Scorecard / Redundancy / Metric-Source Consistency Repair

**Date:** 2026-06-22
**Verdict:** `PM40C_CONSISTENCY_PASS`
**Commit:** `5ade041`

---

## Summary

PM-40B 修复了核心指标空白，但页面仍有三个一致性问题：scorecard 显示过期评估、redundancy section 内部冲突、Best Horizon 空字段缺解释。PM-40C 全部修复。

---

## 问题 1：Quality Scorecard 与新数据不一致

**根因：** `factor_quality_scorecard.csv` 中 rev_2h 的 scorecard 是在 factor-level evaluation 之前计算的，所有底层指标都是 0（rankic_mean=0, coverage_rate=0），导致 quality_score=28.03, class=REVIEW_REQUIRED。

**修复：** 在 HTML builder 中检测 scorecard 是否过期（rankic_mean=0 且 coverage_rate=0），如果是，用 unified profile 数据覆盖：
- `final_quality_score` ← `profile_score`
- `final_quality_class` ← `profile_class`
- `recommended_next_action` ← `recommended_research_action`
- `review_notes` ← `profile_summary`
- `main_strengths/weaknesses` ← `primary_strength/risk`

**rev_2h 修复前后：**
| 字段 | 修复前 | 修复后 |
|------|--------|--------|
| final_quality_class | REVIEW_REQUIRED | PROMISING_BUT_REGIME_DEPENDENT |
| final_quality_score | 28.03 | 39.65 |
| recommended_next_action | REVIEW_FORMULA_OR_METADATA | WATCH_FOR_REGIME_DEPENDENCE |
| review_notes | "冗余数据不完整，无法充分评估新颖性" | "Profile score 40/100. Promising overall but regime-dependent." |

---

## 问题 2：Redundancy section 内部冲突

**根因：** 旧 `factor_redundancy_summary.csv` 的 pairwise 计算结果（Valid Pairs 0/75, Nearest abs Spearman 0.0000）与 PM-37 unified profile 的 cluster 评估（NOVEL_DISTINCT, Cluster #45）并存。

**修复：** 当 `redundancy_source == "unified_profile"` 时：
- 隐藏旧的 pairwise 字段（Valid Pairs, Nearest Factor, Nearest abs Spearman, Insufficient Overlap）
- 显示 profile 字段（Marginal Info, Cluster Role）
- 保留 Cluster ID 和 Strongest Redundancy（来自 profile）

**rev_2h 修复前后：**
| 字段 | 修复前 | 修复后 |
|------|--------|--------|
| Valid Pairs | 0 / 75 | (隐藏) |
| Valid Pair Coverage | 0.0% | (隐藏) |
| Nearest abs Spearman | 0.0000 | (隐藏) |
| Novelty Assessment | NOVEL_DISTINCT ✓ | NOVEL_DISTINCT ✓ |
| Cluster | #45 ✓ | #45 ✓ |
| Marginal Info | — | DISTINCT_SINGLETON |
| Cluster Role | — | DISTINCT_SINGLETON |

---

## 问题 3：Best Horizon Metrics 空字段缺解释

**根因：** `long_short_std`, `long_short_annualized_return`, `long_short_annualized_vol`, `long_short_max_drawdown` 在 `factor_diagnostics_summary.csv` 中为 None，factor-level evaluation 也没有这些字段。

**修复：** 添加 `ls_metrics_unavailable_reason` 字段，当这些指标为空时显示："not available from factor-level summary; see paper portfolio diagnostics"

---

## PM-35 五因子 Consistency QA

| 因子 | scorecard_class | score | action | redundancy_source | novelty | cluster | ls_unavail |
|------|----------------|-------|--------|-------------------|---------|---------|------------|
| rev_2h | PROMISING_BUT_REGIME_DEPENDENT | 39.65 | WATCH_FOR_REGIME_DEPENDENCE | unified_profile | NOVEL_DISTINCT | #45 | ✓ |
| mom_vol_adjusted_20h | PROMISING_BUT_REGIME_DEPENDENT | 39.85 | WATCH_FOR_REGIME_DEPENDENCE | unified_profile | REDUNDANT_NOVELTY_DERIVED | #4 | ✓ |
| range_breakout_vol_confirm_20h | LOW_PRIORITY_DIAGNOSTIC | 34.49 | LOWER_PRIORITY_REVIEW | unified_profile | REDUNDANT_NOVELTY_DERIVED | #32 | ✓ |
| volume_pressure_20h | PROMISING_BUT_REGIME_DEPENDENT | 44.39 | WATCH_FOR_REGIME_DEPENDENCE | unified_profile | NOVEL_DISTINCT | #44 | ✓ |
| xs_rank_mom_accel | PROMISING_BUT_REGIME_DEPENDENT | 39.25 | WATCH_FOR_REGIME_DEPENDENCE | unified_profile | NOVEL_DISTINCT | #46 | ✓ |

---

## Files Changed

- `scripts/_build_factor_eval_html.py` — scorecard stale detection + override, redundancy cleanup, unavailable reasons
- `scripts/check_factor_evaluation_page_completeness.py` — new `pm40c_consistency` check
- `reports/site/factor-library/factor-evaluation.html` — rebuilt

---

## No Formula / Factor Values / Signal Changes

- No `factor_formula_registry.py` changes
- No `factor_ops.py` changes
- No `build_factor_values.py` changes
- No `expected_direction` changes
- No signal panel changes

---

## Lessons

1. **Scorecard stale detection:** scorecard 数据可能在 factor-level evaluation 之前计算，导致所有底层指标为 0。需要检测 `rankic_mean=0 且 coverage_rate=0` 并用 profile 数据覆盖。
2. **Redundancy 数据来源冲突：** 旧 pairwise 计算和新 PM-37 cluster 评估可能并存。页面需要统一数据来源，避免语义冲突。
3. **空字段需要解释：** 当指标不可用时，不能只显示 `—`，需要说明原因。

---

## Recommended Next PM

**PM-41: Post-intake factor interpretation and direction-semantics review**
