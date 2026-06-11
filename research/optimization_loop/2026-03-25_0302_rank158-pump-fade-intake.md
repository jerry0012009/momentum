# 2026-03-25 03:02 UTC · Rank 158 / pump-fade exhaustion reversal fresh intake

- 严格遵循：`docs/BOT2_BOT3_POLICY.md`、`docs/BOT2_BOT3_STATE.md`
- 本轮执行小点：`cycle_plan #3 / Fresh intake slot`
- 本轮只做：认领 1 个新的 raw alpha，并在最小公开证据 + 本地快检口径下直接回答 `park / keep_P1`

## 0. 认领对象
- Rank: `158`
- Target: `crypto-pump-fade-bot`
- Source digest: `research/quant_digests/2026-03-24_1520_pump-fade-exhaustion-reversal-raw-alpha.md`
- Source repo: <https://github.com/tocsnostrap/crypto-pump-fade-bot>

## 1. 为什么本轮选它
当前前排已经把 pairs/stat-arb 连续打到 `Rank 155 / 157`，本轮 fresh intake 更应该补一个相关性更低、但仍能在短周期里独立成策略的 raw alpha。`pump-fade exhaustion reversal` 满足三点：
1. 不是又一条慢频横截面/配对均值回归；
2. 有明确事件定义、入场确认、止损/止盈与 staged exit 骨架；
3. 现成公开证据里已经包含本地 source probe，不需要再伪装成“只有故事没有样本”的壳项目。

## 2. 最小公开证据 + 本地快检摘要
直接依据 digest 中已经冻结的公开证据与本地 source probe：
- 公开文献层：pump-and-dump 文献说明极端拉盘后短窗深回撤是普遍现象，但不自动等于 perp short 可稳定赚钱；因此必须等 `exhaustion + path deterioration`，不能裸空顶部。
- 工程层：repo 给了完整的事件驱动 fade 骨架，不只是检测器，包括 `RSI 回落 + volume decline + lower highs + structure break` 的确认式 short fade 思路，以及 staged exits vs 单一 TP 的对比。
- 本地 source probe（digest 引用的 `reports/artifacts/quant_digests/pump_fade_source_probe_20260324/summary.json`）显示：
  - 20 个标注 pump 事件里，中位 pump 幅度约 `174.1%`；
  - 中位回撤约 `83.0%`；
  - 中位 dump 时间约 `1h`；
  - `83.3%` 在 `1h` 内开始明显回落；
  - `77.8%` 的峰值 RSI ≥ 70，`77.8%` 的峰值量能 ≥ 平均 2 倍，`100%` 出现 3 个以上 lower highs。
- 但同一条线的 PnL 证据仍不干净：仓库一份结果偏正，另一份只有 `5` 笔交易、`60%` 胜率、总收益 `-1.69%`；说明这条线现在更像“形状成立但成本/执行高度敏感”的 raw alpha，而不是已毕业策略。

## 3. Intake verdict
本轮结论：**`keep_P1`**，不是 `park`。

原因：
- 它已经不是“只有灵感”的概念候选，而是有事件统计形状、明确执行骨架、且本地 source probe 能支持的可复现 raw alpha；
- 但它离 `P2` 还差得很远，因为当前真正决定成败的不是“会不会回撤”，而是 **在可成交深度、滑点、做空通道与确认延迟下，5m/15m confirm-fade 是否还能留下 post-cost 正期望**。

因此它配得上 `keep_P1`，但只配拿 **一次** 单一 decisive follow-up，而不是开放式补故事。

## 4. 唯一高杠杆 follow-up blocker
唯一值得给它的 survivor follow-up 应收口为：

**在冻结事件样本上，对 `immediate fade` vs `wait-for-lower-high + break` 做 5m/15m、含 taker/slippage/spread veto 的成本后 event-study；若确认式 fade 仍不能稳定留下正的 `net bps / event`，就直接 drop。**

这就是唯一 decisive blocker；不需要再先补第二层理论说明。

## 5. 一句话 result
`Rank 158 / pump-fade exhaustion reversal` 已有事件统计形状、确认式 fade 骨架与本地 source probe 支撑，足以进入 `keep_P1`；其唯一高杠杆下一步不是再补论文故事，而是冻结事件样本后直接验证 `confirm-fade` 在 5m/15m 上是否还能留下 post-cost 正期望。
