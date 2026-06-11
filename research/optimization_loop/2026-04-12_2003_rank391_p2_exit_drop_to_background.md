# bot3 执行日志（Active P2 出口决策轮）
- 时间：2026-04-12 20:03 UTC
- 执行槽位：Active P2 slot
- 对象：`Rank 391 / BTC dominance slope × strongest/weakest alt switch`
- 对应小点：`cycle_plan #1`

## 本轮执行小点
仅围绕唯一 blocker（`1.5bps one-way` 成本阈值鲁棒性）做最小复核，并补 1 条 execution realism 核验；本轮必须输出单一出口结论，不得继续 `keep_P2`。

## 新证据（会改变系统认知）
证据文件：`reports/artifacts/literature/rank391_p2_exit_decision_2026-04-12.json`

1) **成本阈值复核（selected config）**
- `1.00 bps`：`cumret +1.4717%`
- `1.25 bps`：`cumret +0.6480%`
- `1.50 bps`：`cumret -0.1691%`
- `1.75 bps`：`cumret -0.9795%`
- `2.00 bps`：`cumret -1.7834%`
- 估算 break-even one-way cost：`~1.53 bps`

结论：该策略在保守可交易成本口径附近（`1.5bps`）没有正收益缓冲，属于阈值边缘且已转负。

2) **execution realism 最小核验（成交时段/换仓频率 vs 容量假设）**
- 非零换仓 bars 占比：`1.76%`（`327 / 18574`）
- 换仓频率：均值 `2.14 bars/day`，`p95=4 bars/day`，单日上限 `4`（与 `6h` 栅格一致）
- 单次换仓强度：`turnover_x` 均值 `~0.997`，`p95=1.0`，最大 `2.0`
- 成交时段集中：`00:00 / 06:00 / 12:00 / 18:00 UTC` 占比 `100%`

结论：执行时间对齐本身是诚实且可落地的；本轮 decisive blocker 仍是成本阈值，不是时段错配或虚假换仓设定。

3) **同数据网格下的 1.5bps 鲁棒性横向复核（最小近似）**
- 使用 `btc_dominance_rotation_probe_2026-04-12_filtered_rebalance_summary.csv` 中所有同时具备 `1bps` 与 `2bps` 的配置做 `1.5bps` 线性插值近似：`60/60` 个配置估计值均不为正；最佳也约 `-0.156%`。

结论：不是单一参数点失效，而是整组可交易壳在 `1.5bps` 附近普遍缺乏正收益缓冲。

## 出口结论（单一）
`Rank 391`：`drop_to_background`。

## 一句话结果（写回 cycle_plan.result）
`Rank 391` 在 `1.5bps one-way` 成本阈值复核下由边际转负，且同网格近似下无正收益配置，故本轮从 `Active P2` 直接收口为 `drop_to_background`。
