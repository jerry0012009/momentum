# Phase 2E Closeout — Batch Factor Evaluation

> Date: 2026-06-13
>
> Status: **COMPLETE**
>
> Previous: Phase 2D COMPLETE, Phase 2E Batch 1 COMPLETE
>
> Next: Phase 3 (V1 Long-window Baseline)

---

## 1. Phase 2E 目标

Phase 2E = **Batch Factor Evaluation**。目标是：实现 shortlisted 因子，生成 factor_values，运行标准化评价，保留所有新因子为 DIAGNOSTIC_PROBE 直到 human review。

**Phase 2E 证明的是评价流水线的能力，不是 alpha 质量。**

## 2. 已完成事项

| 阶段 | 内容 | Commit |
|------|------|--------|
| Phase 2E0 | Batch 1 实施计划（6 个 direct_formula 因子） | `31a31ee` |
| Phase 2E0b | Spec 修正（output schema + expected_direction） | `0ac766b` |
| Phase 2E1-A | 实现 6 个因子函数 + 30 个单元测试 | `3997223` |
| Phase 2E Batch 1 Eval | 运行 11 因子评价 + 生成 metrics + registry 更新 | `d4c1eaa` |

**测试结果：** 63/63 passed（30 batch1 + 33 existing）
**因子值生成：** 11 factors × 215,061 rows
**评价周期：** 2025-12-15 ~ 2026-06-13（~180 days）

## 3. 11 个因子评价结果摘要

### V0 Probes（已有）

| factor | RankIC (1h) | RankICIR | raw_spread (1h) | dir_adj (1h) | status |
|--------|-------------|----------|-----------------|--------------|--------|
| mom_20h | -0.015 | -0.075 | 0.035% | 0.035% | DIAGNOSTIC_PROBE |
| reversal_5h | 0.024 | 0.116 | -0.029% | 0.029% | DIAGNOSTIC_PROBE |
| volatility_20h | -0.017 | -0.085 | 0.071% | -0.071% | DIAGNOSTIC_PROBE |
| rsi_14h | -0.014 | -0.073 | 0.050% | -0.050% | DIAGNOSTIC_PROBE |
| bb_zscore_20h | -0.019 | -0.099 | 0.042% | -0.042% | DIAGNOSTIC_PROBE |

### Batch 1（新实现）

| factor | RankIC (1h) | RankICIR | raw_spread (1h) | dir_adj (1h) | status |
|--------|-------------|----------|-----------------|--------------|--------|
| wq101_alpha101 | -0.025 | -0.143 | 0.007% | 0.007% | DIAGNOSTIC_PROBE |
| wq101_alpha12 | 0.003 | 0.019 | -0.016% | null | DIAGNOSTIC_PROBE |
| wq101_alpha53 | 0.016 | 0.092 | -0.013% | null | DIAGNOSTIC_PROBE |
| q158_high_low_range | -0.016 | -0.079 | 0.071% | null | DIAGNOSTIC_PROBE |
| tech_macd | -0.006 | -0.038 | 0.023% | 0.023% | DIAGNOSTIC_PROBE |
| tech_atr | 0.009 | 0.058 | -0.008% | null | DIAGNOSTIC_PROBE |

**说明：**
- conditional 因子的 dir_adj_spread = null（正确：不强行定方向）
- q158_high_low_range 和 tech_atr 的 raw_spread 显著，但这是波动率结构，不是 alpha
- 所有因子 RankICIR < |0.2|，无显著预测信号

## 4. 为什么不继续 Batch 2

- Batch 1 已证明评价流水线可以正常运行
- Batch 1 的 6 个因子均无显著信号，继续增加类似因子的边际收益低
- 需要先解决数据窗口问题：~180 天对因子筛选太短
- Phase 3（长窗口基线）比 Batch 2 更有价值

## 5. 为什么不升级任何 factor

- **无因子满足 CANDIDATE_REVIEW 条件**
  - RankICIR < |0.2| for all factors
  - IC 方向不稳定（多数因子在不同 horizon 方向不一致）
  - 高 turnover 因子（wq101_alpha101, wq101_alpha53 > 78%）的 spread 会被交易成本吃掉
- Phase 2E 证明的是流水线，不是 alpha
- 升级需要更长窗口、更严格的统计检验、以及人类判断

## 6. 为什么 Phase 3 是下一步

| 问题 | Phase 2E 无法解决 | Phase 3 可以解决 |
|------|-------------------|------------------|
| 数据窗口太短 | ~180 天，统计功效不足 | 扩展到 1-2 年 |
| 因子稳定性未知 | 单窗口无法判断 | 长窗口 + 滚动窗口对比 |
| 动态 universe 未测试 | 静态 Top50 | Phase 3 仍用静态，Phase 4 再做动态 |
| 评价标准未校准 | 无历史基准 | 长窗口提供基线参考 |

## 7. 禁止事项

- 不要实现新因子
- 不要继续 Batch 2
- 不要升级任何因子到 CANDIDATE_REVIEW 或更高
- 不要做策略回测
- 不要做组合建模
- 不要进入 Phase 4

## 8. 结论

**Phase 2E: COMPLETE**

- 评价流水线已验证
- 11 个因子全部为 DIAGNOSTIC_PROBE
- 无 alpha 证据
- 下一步：Phase 3 — V1 Long-window Baseline
