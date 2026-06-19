# 因子库真实执行链路与脚本地图

> Phase 12D-H5 · 研究解释页

## 一句话总览

这页不是代码目录，也不是全部脚本列表。它只解释当前因子库主链路中真正相关的脚本，以及哪些脚本属于其他 momentum 功能。

## 活跃入口点

**`scripts/evaluate_signals.py`** — 使用公共 `momentum.signal_evaluation` API 的规范 CLI 入口。

旧 Phase 10A/10A-R/10B/10D 脚本已归档至 `archive/legacy_phase_scripts/phase10/`，仅供历史参考。

## 当前活跃评价维度

| 维度 | 目的 | 脚本 |
|------|------|------|
| **RankIC** | 信号排序与未来收益排序的 Spearman correlation | `evaluate_signals.py` |
| **Quantile Spread** | 高分组与低分组的未来收益差 | `evaluate_signals.py` |
| **Direction Consistency** | RankIC 方向与 spread 方向是否一致 | `evaluate_signals.py` |

## 历史扩展诊断（不在当前 evaluate_signals.py 中）

| 维度 | 状态 | 结果文件 |
|------|------|----------|
| Bucket / Tail Diagnostics | Phase 10B 已归档 | `phase10b_*.csv` |
| Tail-aware Policy Design | 设计阶段，非标准指标 | 设计文档 |
| Variant Grid | Phase 10D 已归档 | `phase10d_*.csv` |

## 旧 Phase 10 脚本归档说明

旧脚本已从 `scripts/` 移至 `archive/legacy_phase_scripts/phase10/`：

| 旧脚本 | 原功能 | 当前状态 |
|--------|--------|----------|
| `run_phase10a_signal_backtest.py` | RankIC + Spread 初评 | Archived → 功能已整合到 `evaluate_signals.py` |
| `run_phase10a_r_diagnostics.py` | 方向一致性 | Archived → 功能已整合到 `evaluate_signals.py` |
| `run_phase10b_tail_diagnostics.py` | Bucket / Tail 诊断 | Archived → 结果保留在 CSV |
| `run_phase10d_tail_aware_variants.py` | 变体网格评估 | Archived → 结果保留在 CSV |

## 当前代码结构

当前 active structure 已完成：
- `src/momentum/signal_evaluation/` — 公共 API 包（`rank_ic.py`、`quantile_spread.py`、`consistency.py`、`_vectorized.py`）
- `scripts/evaluate_signals.py` — 规范 CLI 入口
- `scripts/run_signal_evaluation_parity_harness.py` — parity 测试工具
- 旧 Phase 10 脚本已归档

未来如需扩展（tail diagnostics、variant grid），应作为新模块加入 `src/momentum/signal_evaluation/`，不恢复旧脚本。

## 当前信号评价结论摘要

当前核心信号 **signal_v0_core_only** 在 RankIC 上显著为正，但 mean quantile spread 为负，**说明它不是一个已经干净验证的 alpha**。当前结论是：该信号可以继续 paper diagnostic，不可解释为可交易策略。

---

*Authority: actual repository scan · Phase 12D-H5 · 2026-06-19*
