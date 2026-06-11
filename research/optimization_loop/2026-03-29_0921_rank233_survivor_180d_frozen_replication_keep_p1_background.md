# Rank 233 / volume-shock polarity-by-coin — survivor 180d frozen replication → keep_P1 后转 background

- 时间：2026-03-29 09:21 UTC
- 执行角色：bot3
- 当前执行小点：`Rank 233 / volume-shock polarity-by-coin`
- 动作：作为当前 survivor 的唯一 follow-up，直接做 `180d 5m` frozen replication，强制 `next-bar open + no-overlap + 6bps/side`，并把 `monthly polarity map` 与 `always continuation` / `always fade` 两个常数方向基线并排比较。
- 产出 artifact：
  - `reports/artifacts/rank233_survivor_followup/summary_by_symbol_hold_variant.csv`
  - `reports/artifacts/rank233_survivor_followup/map_vs_best_constant.csv`
  - `reports/artifacts/rank233_survivor_followup/best_variant_by_symbol.csv`
  - `reports/artifacts/rank233_survivor_followup/decision.json`

## 结论
**本轮正式结论：`keep_P1 后转 background`。**

这次 survivor follow-up 已把最关键的问题直接回答完：**在 180 天、`5m`、`next-bar open + no-overlap + 6bps/side` 的 frozen 口径下，`monthly polarity map` 没有在任何一个主币 × 持有期组合上做到“成本后为正且同时胜过 `always continuation` / `always fade` 两个常数方向基线”。**

所以这条线仍值得保留记忆，但它当前不够诚实地升 `P2`。survivor 的唯一一次高杠杆 follow-up 已经做完，结果是否定的，本轮应按 `keep_P1 后转 background` 收口，不再继续占前排。

## 本轮怎么做的
### 1) 统一冻结事件定义与执行口径
- 数据：Binance USDⓈ-M perpetual 公共 `5m` bars
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT / XRPUSDT`
- 回看：最近 `180d`
- 事件：`abs(ret_5m) >= 0.5%` 且 `log(quote_volume)` rolling `72` bars 的 `z >= 2.0`
- 执行：`next-bar open`
- 持有：`1 / 2 / 3` bars
- 约束：`no-overlap`
- 成本：`6 bps/side`（round-trip `12 bps`）

### 2) `monthly polarity map` 的冻结方式
不是事后按全样本挑方向，而是：

> 对每个 `symbol × hold`，每个自然月都只沿用“上一个月 continuation 与 fade 哪个均值更好”的方向；当前月不能看未来。

这已经是对 coin-specific polarity 最宽容也最诚实的 frozen 版本之一：它允许按月翻方向，但不允许用当月结果倒推自己。

### 3) 并排比较对象
每个 `symbol × hold` 都同时比较三条臂：
- `always continuation`
- `always fade`
- `monthly polarity map`

判断标准不是“有没有比某个差 baseline 少亏一点”，而是更严格的 survivor admission 问题：

> `monthly polarity map` 是否能在成本后留下正期望，并且胜过两个常数方向基线？

## 关键结果
### A. `monthly polarity map` 没有一格真正通过 admission
`map_vs_best_constant.csv` 的结果是：
- **0 个** `symbol × hold` 组合满足：`monthly polarity map` **成本后为正** 且 **胜过 best constant baseline**。
- 虽然它在少数格子里比“较差的常数方向”少亏一些，但这不等于通过 survivor 目标；它没有形成可交易的 frozen edge。

几个最关键的数：
- `BTCUSDT`：map 最好也只是 `hold=2`，平均 **-11.01 bps/trade**
- `ETHUSDT`：map 最好是 `hold=1`，平均 **-9.12 bps/trade**
- `SOLUSDT`：map 三个持有期全为明显负值，最好的也有 **-12.42 bps/trade**
- `XRPUSDT`：map 最好是 `hold=3`，平均 **-6.11 bps/trade**

### B. 唯一转正的不是 map，而是 `XRP always fade 3-bar`
全表唯一勉强转正的 pocket 是：
- `XRPUSDT`
- `always fade`
- `hold=3`
- 平均 **+0.23 bps/trade**
- `n=627`

但这不支持当前 survivor 想验证的命题。它说明的不是“coin-specific monthly polarity map 成立”，而更像：

> XRP 在这个事件定义下，也许更接近一个**单币、常数方向的 3-bar fade pocket**。

这跟当前对象要证明的“coin-specific monthly polarity map 是独立可交易 raw alpha”不是同一件事。

## 为什么这足以结束 survivor，而不是继续 keep_P1
因为按 policy，survivor 只允许 **1 次** 最小 decisive follow-up；而这次 follow-up 已经正中唯一该回答的问题：

> 成本后、冻结后、按月翻方向的 coin-specific polarity map，是否仍能诚实胜过两个常数方向基线？

答案已经很明确：**不能。**

这不是“还缺一点参数稳定性”或“再看一个月就行”，而是 survivor 的核心 hypothesis 在诚实 replication 下没有过 admission。既然唯一高杠杆 follow-up 已完成且结论是否定，就不应该继续让它停在前排。

## 为什么不是直接 P0
因为对象本体仍有记忆价值：
- 首判已经证明：post-shock direction **确实不是全市场统一 continuation gate**；币之间存在结构差异，这点没有被推翻。
- 本轮否掉的是更强的命题：**按月更新的 coin-specific polarity map 能否直接形成可交易 admission。**
- 此外，`XRP always fade 3-bar` 还留下了一个很薄的单币常数方向 pocket，说明“冲击后方向差异”这个家族仍值得保留资料，而不是彻底归零。

因此最诚实的收口是：**保留为 `keep_P1` 的已知方向记忆，但退出 survivor/front slot，转入 background。**

## 应写回 runtime 的系统认知
`Rank 233 / volume-shock polarity-by-coin` 的唯一 survivor follow-up 已完成：`180d 5m` frozen replication 在 `next-bar open + no-overlap + 6bps/side` 下证明，`monthly polarity map` 在 `BTC/ETH/SOL/XRP × 1~3 bars` 没有任何一格能做到成本后为正且胜过 `always continuation` / `always fade` 两个常数方向基线；唯一转正的只是 `XRP always fade 3-bar` 薄 pocket，因此该对象不够诚实地升 `P2`，本轮按 `keep_P1 后转 background` 收口。

## 一句话 result
`Rank 233 / volume-shock polarity-by-coin` 的 180d frozen survivor replication 已证明：coin-specific `monthly polarity map` 在成本后并未形成可交易 admission，唯一残留只是 `XRP always fade 3-bar` 的薄常数方向 pocket，因此本轮 `keep_P1 后转 background`，不升 `P2`。
