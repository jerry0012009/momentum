# PM-40B: Factor Page Display Consistency — Full 6-Layer Fix

**Date:** 2026-06-22
**Verdict:** `PM40B_DISPLAY_CONSISTENCY_PASS`
**Commits:** `e1d225d`, `e55f41b`, `d995fbe`, `d3af847`

---

## 三层根因

### 根因 1: 数据层 — period IC 数据未合并
`factor_level_period_ic_summary.csv` 有 71 个因子，但 5 个 PM-35 新因子的 period IC 数据在 `factor_level_period_ic_summary_batch01.csv` 中，从未合并到 canonical CSV。导致 Monthly RankIC 图表为空。

### 根因 2: Payload 层 — paper payload 未覆盖新因子
`single_factor_paper_page_payload.json` 只有 71 个因子。底层 CSV（`single_factor_paper_summary.csv` 等）已有 76 个因子的数据，但 `build_single_factor_paper_page_payload.py` 未重新运行。

### 根因 3: Builder 层 — 字段映射和 fallback 逻辑
- `rankic_std` / `rankic_ir` 的 period IC lookup 使用了错误的 key（2-tuple vs 3-tuple），永远返回 None
- `redundancy_cluster_id` 从旧 scorecard 读到 `-1`，未 fallback 到 profile 数据
- `novelty_assessment` 显示 `INSUFFICIENT_OVERLAP`，与 Unified Profile 矛盾

---

## 修复内容

### Layer 1: 补数据
- 合并 `factor_level_period_ic_summary_batch01.csv` 中 5 个因子的 period IC 数据到 canonical CSV
- 结果：71 → 76 因子，7576 行

### Layer 2: 修 HTML builder 字段映射
- 修复 `rankic_std` / `rankic_ir` 计算：从 `monthly_ic` 数据用 `statistics.stdev()` 和 `mean/std` 计算
- 添加 `profile_cluster_id` / `profile_cluster_size` 从 profile payload
- 添加 redundancy reconciliation post-processing

### Layer 3: 补 payload 覆盖
- 运行 `build_single_factor_paper_page_payload.py` 重新生成 paper payload（71 → 76 因子）
- shape_stability / decile_shape / capacity_liquidity 已有 5 因子数据（无需修复）

### Layer 4: 重建页面 + QA
- 重建 `factor-evaluation.html`（2.91 MB）
- QA: 22/22 PASS（新增 `pf_detail_completeness` 检查）

### Layer 5: 部署验证
- 部署到 `/var/www/momentum-report/factor-library/`
- `curl -I` → HTTP 200 OK
- JSON valid, factor_count=76

### Layer 6: 文档沉淀
- 更新 START_HERE.md 和 POST_INTAKE_WORKFLOW_RUNBOOK.md

---

## rev_2h 修复前后

| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| rankic_mean | 0.036 ✅ | 0.036 ✅ |
| rankic_std | None ❌ | 0.0154 ✅ |
| rankic_ir | None ❌ | 2.355 ✅ |
| rankic_t_stat | 29.82 ✅ | 29.82 ✅ |
| monthly_ic_positive_rate | None ❌ | 1.0 ✅ |
| monthly_ic | 0 条 ❌ | 25 条 ✅ |
| monthly_ls | 25 条 ✅ | 25 条 ✅ |
| redundancy_cluster_id | -1 ❌ | 45 ✅ |
| novelty_assessment | INSUFFICIENT_OVERLAP ❌ | NOVEL_DISTINCT ✅ |
| paper_viability_class | None ❌ | PAPER_MIXED ✅ |
| cost_sensitivity_class | None ❌ | COST_COLLAPSED ✅ |
| gross_sharpe | None ❌ | 1.22 ✅ |
| source_warning | no_horizon_data ❌ | (空) ✅ |

---

## 5 个 PM-35 因子 Detail Completeness

| 因子 | rankic | std | ir | t | ic_rate | mic | mls | paper | cluster | novelty | sw |
|------|--------|-----|-----|-----|---------|-----|-----|-------|---------|---------|-----|
| rev_2h | 0.036 | 0.015 | 2.35 | 29.82 | 1.0 | 25 | 25 | PAPER_MIXED | #45 | NOVEL_DISTINCT | (空) |
| mom_vol_adjusted_20h | -0.021 | 0.008 | -2.42 | -20.47 | 0.0 | 25 | 25 | PAPER_MIXED | #4 | REDUNDANT | (空) |
| range_breakout_vol_confirm_20h | -0.029 | 0.017 | -1.73 | -13.67 | 0.04 | 25 | 25 | PAPER_MIXED | #32 | REDUNDANT | (空) |
| volume_pressure_20h | -0.011 | 0.005 | -2.29 | -11.31 | 0.04 | 25 | 25 | PAPER_MIXED | #44 | NOVEL_DISTINCT | (空) |
| xs_rank_mom_accel | -0.024 | 0.008 | -3.00 | -20.51 | 0.0 | 25 | 25 | PAPER_REVIEW | #46 | NOVEL_DISTINCT | (空) |

---

## No Formulas / Factor Values / Signal Changed

- No factor formulas modified
- No `expected_direction` values changed
- No `factor_values` files modified
- No signal panel changes
- No `factor_formula_registry.py` changes
- No `factor_ops.py` changes
- No `build_factor_values.py` changes

---

## Lessons Added to START_HERE

1. 新因子 12/12 evidence complete ≠ 页面所有 legacy sections 自动完整
2. HTML builder 必须 merge legacy diagnostics + factor-level evaluation + unified profile payload
3. Monthly IC 必须纳入 post-intake workflow
4. 新增因子后必须做 per-factor detail completeness QA
5. 不允许页面出现 Unified Profile complete 但 legacy section 空白或冲突
6. Paper payload 需要手动重新生成（`build_single_factor_paper_page_payload.py`）
7. `rankic_std` / `rankic_ir` 需要从 period IC 数据计算，不能依赖 diagnostics summary

---

## Recommended Next PM

**PM-41: Post-intake factor interpretation and direction-semantics review**
- Review `expected_direction` for 5 new factors
- Review `decision_bucket` (`DIRECTION_REVIEW_REQUIRED`)
- Evaluate whether negative-t-stat factors should have direction flipped
- Review `paper_viability_class` and `cost_sensitivity_class` for actionable insights
