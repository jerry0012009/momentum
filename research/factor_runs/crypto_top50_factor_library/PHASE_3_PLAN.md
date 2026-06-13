# Phase 3 Plan — V1 Long-window Baseline

> **Status:** NOT STARTED
>
> Date: 2026-06-13
>
> Previous: Phase 2E COMPLETE
>
> Human decision: Phase 3 ALLOWED TO START

---

## 1. Phase 3 定义

**V1 Long-window Baseline**

使用更长的历史窗口评估当前 11 因子库，在进入动态 universe 之前建立基线。

## 2. 目标

- 将数据窗口从 ~180 天扩展到 1-2 年（如果 Binance 历史数据可用）
- 保持相同静态 Top50 universe 协议
- 复用现有 labels 和 evaluation 评价协议
- 评价当前 11 个因子在长窗口下的表现
- 对比 180d vs long-window 诊断结果
- 记录因子稳定性 / 不稳定性

## 3. 允许做什么

| 允许 | 说明 |
|------|------|
| 扩展数据窗口 | 从 Binance 拉取更长历史（1-2 年） |
| 保持静态 Top50 | 不做动态 universe |
| 复用 labels + eval | 使用现有 build_labels.py + evaluate_factors.py |
| 评价 11 因子 | 不新增因子 |
| 对比窗口 | 180d vs long-window |
| 记录稳定性 | 滚动窗口 IC / RankIC |

## 4. 禁止做什么

| 禁止 | 原因 |
|------|------|
| 实现新因子 | 保持 11 因子不变 |
| 使用动态 universe | Phase 4 再做 |
| 策略回测 | 不在 Phase 3 范围 |
| 组合建模 | 不在 Phase 3 范围 |
| 交易成本建模 | 不在 Phase 3 范围 |
| 升级因子到 alpha | 无依据 |
| 进入 Phase 4 | 需要 Phase 3 closeout |

## 5. 交付物

| 交付物 | 说明 |
|--------|------|
| Long-window data manifest | 扩展后的 bars_1h.parquet 元数据 |
| Long-window data validation | 数据质量报告（缺失率、gap、symbol 覆盖） |
| Long-window factor_values | 11 因子在长窗口下的 factor_values.parquet |
| Long-window evaluation summary | 11 因子在长窗口下的 metrics |
| Comparison report | 180d vs long-window 对比（IC、RankIC、spread 稳定性） |
| PHASE_3_CLOSEOUT.md | Phase 3 收口文档 |

## 6. 实施步骤

```
Phase 3A: Data Extension
  - 检查 Binance 历史数据可用性（1m/1h bars back to 2024 or earlier）
  - 拉取扩展数据
  - 验证数据质量

Phase 3B: Long-window Pipeline
  - 使用扩展数据重新生成 universe
  - 重新生成 labels
  - 重新生成 11 因子 factor_values

Phase 3C: Long-window Evaluation
  - 运行 evaluate_factors.py
  - 生成 long-window evaluation summary

Phase 3D: Comparison
  - 对比 180d vs long-window
  - 滚动窗口 IC 稳定性分析
  - 记录哪些因子稳定 / 不稳定

Phase 3E: Closeout
  - 写 PHASE_3_CLOSEOUT.md
  - 更新 roadmap / registry
  - 决定 Phase 4 是否允许
```

## 7. 进入 Phase 4 的条件

- Phase 3 closeout 完成
- 至少有 1 个因子在长窗口下显示稳定信号（RankICIR > 0.3 在 ≥ 2 个 horizon）
- 或者确认所有因子均无信号，需要重新设计因子库
- Human approval

## 8. 禁止事项

- 不要实现新因子
- 不要使用动态 universe
- 不要做策略回测
- 不要做组合建模
- 不要交易成本建模
- 不要升级因子到 alpha
- 不要进入 Phase 4
