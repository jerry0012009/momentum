# Rank 396｜survivor 唯一 follow-up 收口（drop_to_background/P0）

- 时间：2026-04-13 06:49 UTC
- 执行轮次：bot3 13m auto
- 对象：`Rank 396 / cexdex funding-arb shell`
- 对应小点：`cycle_plan #1`（survivor 唯一 follow-up）

## 本轮执行（仅围绕唯一 blocker）

唯一 blocker（来自上轮 first verdict）：
> 缺少“跨 venue、时间对齐、全摩擦（fee+slippage+gas/withdraw/bridge+latency）后仍为正”的可执行净边际证据链。

本轮最小核验：
1. 复核现有 artifact：`reports/artifacts/literature/funding_cexdex_binance_probe_2026-04-13_summary.csv`
   - `threshold=1bps/8h`：`events=84`
   - `weighted_mean_gross_bps=+0.5931`
   - `weighted_mean_net8_bps=-7.4069`
   - `weighted_winrate_net8=0.0`
2. 核查该对象是否已落地 cross-venue 时间对齐的可执行证据文件：
   - 当前仅存在 `funding_cexdex_binance_probe_2026-04-13_{summary,detail,asset_breakdown}.csv`
   - 未发现包含第二 venue 同时点可成交 quote、对冲成交代理、转账/bridge/gas/latency 全摩擦合并核算的运行产物。

## 本轮封口决策

- 问题：`跨 venue 可执行 edge_after_cost 是否仍为正？`
- 结论：**当前不能证明为正，且现有可复核口径（same-venue proxy）明确为负。**
- 因此按 survivor 唯一 follow-up 收口规则执行：**`drop_to_background/P0`**（不再保留在前排槽位）。

## 会改变系统认知的一句话

`Rank 396` 已完成 survivor 唯一 follow-up 且未打穿唯一 blocker：在现有证据下无法建立跨 venue 全摩擦后仍为正的可执行净边际，故本轮直接 `drop_to_background/P0` 并退出前排。