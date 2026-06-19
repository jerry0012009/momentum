# 因子库真实执行链路与脚本地图

> Phase 12D-H7 · 研究解释页

## 声明

本页是研究解释页，不是实盘，不是交易建议。Phase 13 尚未开始。本页只解释因子库主链路，其他 momentum 项目功能不在本页讨论。

## 代码结构图

actual-script-map.html 包含一个交互式 SVG 结构图，展示：
- 8 个核心功能模块 + 1 个归档模块
- 箭头表示运行顺序
- 颜色分类：蓝色=active，绿色=扩展点，橙色=诊断/成本，灰色=归档
- 点击节点查看目录、脚本、输出、扩展位置

## 主链路

```
Raw Data → Universe → Labels → Factor Values → Signal Panel → Signal Evaluation → Cost/Paper → Reports
```

## 公开页面

| 页面 | 职责 |
|------|------|
| index.html | 极简入口页（3 个卡片） |
| actual-script-map.html | 代码结构、目录、脚本、运行顺序、扩展位置 |
| factor-evaluation.html | 单因子注册表、公式、类别、信号使用状态、factor-level IC |
| signal-evaluation-summary.html | 信号级 RankIC、Spread、Consistency、研究结论 |

## 扩展位置

1. 新增因子：`src/momentum/factors/` + `scripts/build_factor_values.py` + `factor_formula_registry.py`
2. 新增信号：`scripts/build_phase9b_signal_panel.py`
3. 新增评价指标：`src/momentum/signal_evaluation/` + `scripts/evaluate_signals.py`
4. 新增成本/回测：对应 cost/paper diagnostic 层

## 关联页面

- [因子评价](factor-evaluation.html) — 53 个因子的注册表和评价状态
- [信号评价](signal-evaluation-summary.html) — 信号级评价结果
