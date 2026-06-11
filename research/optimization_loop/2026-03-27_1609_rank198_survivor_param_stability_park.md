# Rank 198 survivor follow-up — park_to_background on parameter stability

- Time: 2026-03-27 16:09 UTC
- Target: `Rank 198 / dynamic cointegration surviving-pocket deployment`
- Verdict: `park_to_background`

## 本轮只回答的问题
只执行当前 `cycle_plan` 中排在最前的 pending 小点：

> 对这条 survivor 的唯一一次 follow-up 直接做便宜但诚实的参数稳定性检查，围绕 `TRXUSDT/ADAUSDT` 类 surviving pocket 测邻近 `entry_z / exit_z / max_hold / cost` 扰动后是否仍保留净边；必须一次性回答它是 `promote_P2` 还是 `park_to_background`。

## 本轮使用的证据
1. `research/optimization_loop/2026-03-27_1602_rank198_p2_exit_rescope_to_p1.md`
2. `research/optimization_loop/2026-03-27_1530_rank198_p2_admission_keep_p2_time_parameter_honesty.md`
3. `reports/artifacts/quant_digests/dynamic_cointegration_pairs_20260327_1332/summary.json`
4. `reports/artifacts/optimization_loop/rank198_survivor_param_stability_20260327_1609/summary.json`
5. `reports/artifacts/optimization_loop/rank198_survivor_param_stability_20260327_1609/grid.csv`

## 本轮怎么做（便宜但诚实）
原 digest 只留下 `summary.json`，没有完整 trade ledger，也没有把 trade-period rolling z-score 的窗口显式写出。本轮不重做 broad deployment，而是只对 survivor `TRXUSDT/ADAUSDT` 做最小 causal 重建：

- 样本结束时点固定到 digest 生成时：`2026-03-27 13:32 UTC`
- 市场与周期保持不变：Binance USDⓈ-M perpetual `15m`
- lookback：`120d`
- split：`60% formation / 40% trading`
- beta：formation 期 close log 上的 frozen OLS beta
- signal：trade 期 log spread rolling z-score
- execution：prior-bar signal、next-bar open entry/exit
- 为了尽量贴近原 digest 已发布指标，本轮选用 **`480` bars** 的 rolling window，因为在简单 causal 重建里它和原 artifact 的 trade count 最接近（本轮 baseline `51` 笔，对原 artifact `52` 笔）

扰动网格只围绕 policy 指定的四个轴：
- `entry_z ∈ {1.75, 2.00, 2.25}`
- `exit_z ∈ {0.25, 0.50, 0.75}`
- `max_hold ∈ {12, 16, 20}`
- `round-trip cost ∈ {4, 6, 8} bps`

共 `81` 组配置。

## 会改变系统认知的结论
### 1) baseline pocket 不是完全消失，但余量已经很窄
在最接近原 artifact 的重建里，baseline 近似规格：
- `entry_z=2.0`
- `exit_z=0.5`
- `max_hold=16`
- `cost=6 bps`

得到：
- `51` trades
- gross cumulative `≈ +3.39%`
- net cumulative `≈ +0.27%`
- win rate `≈ 45.1%`

也就是说：**这条 pocket 没有被一刀否掉，但当前净边已经窄到“还活着”和“足够稳健”之间只隔一层很薄的参数余量。**

### 2) 真正的问题不是 exit 微调，而是 survival 只剩一小块窄正值孤岛
网格结果非常集中：
- 在 `4 bps` 下，正 net 配置 `18 / 27`
- 在 `6 bps` 下，正 net 配置只剩 `6 / 27`
- 在 `8 bps` 下，正 net 配置只剩 `3 / 27`

并且 `6 bps` 下能活下来的几组，几乎都集中在：
- **更严格的 `entry_z=2.25`**
- **更宽的 `max_hold=20`**

最佳 `6 bps` 配置约为：
- `entry_z=2.25`
- `exit_z ∈ {0.25, 0.50, 0.75}`
- `max_hold=20`
- net cumulative `≈ +1.68%`

而一旦把 entry 放松成 `1.75`，即便同样只看邻近参数：
- 最差 `6 bps` 结果约落到 `-5.49% ~ -5.55%`
- 说明这条 pocket **不是“附近都差不多，只是最佳点更强”**，而是 **只剩一块很窄的正值孤岛**。

### 3) `exit_z` 对结果几乎不敏感，说明现在的 edge 不是稳定的均值回归结构，而更像 timeout 驱动的窄口袋
在这轮 survivor 网格里：
- 大多数相邻 `exit_z` 结果几乎不变；
- 真正决定成败的，是 `entry_z` 是否更苛刻、`max_hold` 是否更宽、以及成本是否再上一个台阶。

这意味着当前 surviving pocket 的可交易性，并没有表现出一个“邻近 exit 规则怎么动都还能自洽”的稳定 MR 结构；它更像是：

> **只有在更挑剔地等极端偏离、并给更长持有期时，才勉强剩下一点净边。**

这不够支撑把它重新送回 `P2`。

## 决策
本轮对 `Rank 198` 给出：

> **`park_to_background`**

新的系统读法应更新为：

> `Rank 198 / dynamic cointegration surviving-pocket deployment` 已完成 re-scope 后唯一一次 survivor follow-up；结果显示 `TRXUSDT/ADAUSDT` pocket 在邻近参数网格中只剩窄正值孤岛，`6 bps` 下仅 `6/27` 配置为正、`8 bps` 下仅 `3/27` 配置为正，因此它不足以重新升回 `P2`，应按 policy 诚实收口并移入 `Background pool`。

## 为什么不是 `promote_P2`
- `P2` 需要的是至少值得继续 admission 的对象；
- 但当前 surviving pocket 的正值区域已经窄到：
  - baseline 只剩轻微正净值；
  - 放松 `entry_z` 就明显转负；
  - 再加 `2 bps` 成本，幸存配置进一步大幅收缩；
  - `exit_z` 几乎不改变结论，说明不是一条稳健、邻近规则可持续的 MR deployment spec。

因此最诚实的结论不是“再给它一次 admission”，而是：

> **这条 re-scope 后的 pocket 只够留下证据，不够继续占前排资源。**

## Runtime writeback
- `Surviving candidate slot`：清空
- `followup_budget_remaining`：本次已用尽
- `Background pool`：写入 `Rank 198` 本轮正式 park 结论
- `cycle_plan #1`：标记为 `done`

## Reader-facing takeaway
`Rank 198` 最后不是死在“有没有 pocket”，而是死在 **pocket 太窄、不够稳**：

**TRX/ADA 这条 surviving pocket 仍能在极窄参数角落里留下正值，但邻近参数和成本一动，正净边就迅速塌缩；所以这轮最诚实的收口不是重回 `P2`，而是 `park_to_background`。**
