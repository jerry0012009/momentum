# 因子库真实执行链路与脚本地图

> Phase 12D-H6 · 研究解释页

## 声明

本页是研究解释页，不是实盘，不是交易建议。Phase 13 尚未开始。本页只解释因子库主链路，其他 momentum 项目功能不在本页讨论。

## 代码结构图

actual-script-map.html 包含一个交互式 SVG 结构图，展示：
- 8 个核心功能模块 + 1 个归档模块
- 箭头表示运行顺序（从上到下）
- 颜色分类：蓝色=active mainline，绿色=extension point，橙色=diagnostic/cost/paper，灰色=archived
- 点击任意节点查看目录、脚本、输出和扩展位置

### 4 个扩展点

| 扩展类型 | 位置 |
|----------|------|
| ★ 新增因子 | `src/momentum/factors/` + `scripts/build_factor_values.py` + `factor_formula_registry.py` |
| ★ 新增信号 | `signal construction` / `scripts/build_phase9b_signal_panel.py` |
| ★ 新增评价指标 | `src/momentum/signal_evaluation/` + `scripts/evaluate_signals.py` |
| ★ 新增成本/回测 | 对应 cost/paper diagnostic 层，不要混进 signal evaluation 核心层 |

## 主链路模块

```
1. Raw Data          → download_full_binance_1h_universe.py → bars_1h.parquet
2. Universe          → build_crypto_top50_universe.py → universe_snapshots.parquet
3. Labels            → build_labels.py → labels.parquet (1h/4h/24h/72h)
4. Factor Values     → build_factor_values.py + factor_formula_registry.py → factor_values.parquet
   ★ 新增因子
5. Signal Panel      → build_phase9b_signal_panel.py → phase9b_signal_panel.parquet
   ★ 新增信号
6. Signal Evaluation → evaluate_signals.py + src/momentum/signal_evaluation/ → RankIC/Spread/Consistency CSVs
   ★ 新增评价指标
7. Cost/Paper        → phase11a + phase12a + phase12b → cost/paper diagnostic CSVs
   ★ 新增成本/回测
8. Reports           → reports/site/factor-library/ → Apache 直接服务
```

## 当前研究结论

当前核心信号 **signal_v0_core_only** 在 RankIC 上显著为正，但 mean quantile spread 为负，**不是已经干净验证的 alpha**。当前结论：继续 paper diagnostic，不可解释为可交易策略。

## 已移除内容

- canary32b / NOT_FACTOR_LIBRARY_MAINLINE 相关内容
- "研究运行账本" → 改为"因子库计算产物"

---

*Phase 12D-H6 · Authority: actual repository scan · 2026-06-19*
