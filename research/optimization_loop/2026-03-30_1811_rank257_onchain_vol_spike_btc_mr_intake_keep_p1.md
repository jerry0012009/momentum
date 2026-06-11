# 2026-03-30 18:11 UTC — Rank 257 / on-chain shock × predicted vol spike / BTC short-horizon mean reversion — fresh intake keep_P1

## 本轮执行对象
- cycle_plan 第 2 项：`onchain volume spike → BTC short-horizon mean reversion`
- 执行动作：作为当前 survivor 已收口后的首条新 `fresh intake`，只回答这篇 on-chain / vol-spike 论文转译出来的对象，是否足以形成独立前排 raw alpha

## 读取依据
- policy：`docs/BOT2_BOT3_POLICY.md`
- runtime：`docs/BOT2_BOT3_STATE.md`
- digest：`research/quant_digests/2026-03-30_1348_onchain-vol-spike-btc-mr-alpha.md`

## 这一步实际回答的问题
这条线到底是不是一个值得正式编号的独立 BTC 事件型 raw alpha，还是只是把“高波动分钟”与旧 BTC 事件家族重新包装了一遍。

## 核查结论
结论是：**可以作为独立 fresh intake 进入前排，但当前只到 `keep_P1`，还不升 `P2`。**

原因分三层：
1. **主语是清楚且独立的。**
   这条线的核心不是泛 on-chain sentiment，也不是“预测波动高就做多”这种模型口号；真正值得 intake 的对象是：`fee-rate / tx-count shock × predicted high-vol state` 触发后，BTC 在随后 `3m/5m` 的 post-spike sign mapping。它研究的是短窗冲击后的可交易方向映射，和已有的 BTC event-clock / tail-reversal / alt follower 家族不是一回事。
2. **最小策略骨架已经够完整。**
   digest 已明确给出 `1m` 事件定义、`3/5/10` bar 持有窗、`round-trip 12/16/20 bps` friction ladder、`anchor VWAP / mid` 回归式出场、以及 `1%~5%` 动态仓位、`2%` 单笔止损、`10%` 日内回撤上限；这已经超过“论文摘要”或 monitor，足够形成可执行的 first-verdict 对象。
3. **但当前 blocker 仍然集中。**
   论文正文自己对交易方向有前后不一致；因此最先要验证的不是 Heston-LSTM 壳子，而是 `MR vs continuation` 的 sign A/B。在这一步没做统一成本、统一事件时间对齐的 frozen honest replication 前，它还不该直接升 `P2`。

## first verdict
- 正式分配：`Rank 257`
- verdict：`keep_P1`
- 层级去向：进入 fresh intake 记录，等待后续是否值得获得 survivor 级 follow-up

## 会改变系统认知的一句话
`Rank 257` 真正该测的不是“高预测波动时该不该做多”，而是 `链上 fee/tx shock × predicted high-vol` 触发后的 BTC `3m/5m` post-spike sign；由于事件锚、执行窗与成本梯度已经独立成型，它值得以前排 `keep_P1` 保留，但下一步必须先做统一成本口径下的 `MR vs continuation` frozen honest replication。

## 本轮写回范围
- 更新 `Fresh intake slot` 为 `Rank 257`
- 更新 `cycle_plan` 第 2 项为 `done`
- 不改 policy / brief / cron prompt
- 不重排后续小点

## reader-facing
- 这是新 intake + 新 verdict，属于需要刷新首页的真实推进。
