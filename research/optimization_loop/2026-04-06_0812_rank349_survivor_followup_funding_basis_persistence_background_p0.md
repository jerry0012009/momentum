# Rank 349 / funding-basis dislocation persistence × delta-neutral carry — survivor follow-up 收口 = background / P0

- 时间：2026-04-06 08:12 UTC
- 对象：`Rank 349 / funding-basis dislocation persistence × delta-neutral carry`
- 轮次角色：bot3 当前轮 `Surviving candidate` 的唯一一次 decisive follow-up
- 结论：`background / P0`

## 本轮要回答的唯一问题
`Rank 349` 在 `BTC/ETH/SOL × 5m/15m × explicit after-cost` 下，`funding+basis+persistence+sign-flip/liquidity gate` 相对 `level-only carry` 是否已经被压成可迁移净增量；若是，则升 `P2`，否则用尽 survivor 预算后诚实收口。

## 本轮新结论
当前不能把 `Rank 349` 升到 `P2`。

不是因为这条线没有研究价值，而是因为它仍停留在 **repo/proposal + 机制文档 + 理论 grounding** 的层面，没有把本轮 follow-up 要求的那句 admission 结论压实：

- 没有给出 `BTC/ETH/SOL` 三个资产上的并列结果；
- 没有给出 `5m/15m` 决策频率下相对 `level-only carry` 的直接对照；
- 没有把 `fees / slippage / holding-cost` 后的净收益优势写成 reader-facing、可复核的结果；
- 也没有证据证明 `sign-flip veto + liquidity gate` 在 desk 当前周期里不是叙事层补丁，而是真能稳定改善 next-funding net capture。

换句话说，`Rank 349` 目前最强的是“对象定义得更完整”，而不是“已经证明它在 desk 当前周期里比 baseline 更能赚钱”。

## 为什么这轮不能 keep_P1 / keep_P2
policy 很清楚：

1. `Surviving candidate` 只有 **1 次** 最小 decisive follow-up 预算；
2. 这次 follow-up 必须直接回答 admission 句子；
3. 若优势仍停在单一叙事、proposal 变量表、或未压成 `5m/15m × after-cost × cross-asset` 的可迁移结果，就要诚实收口，不能继续拖在前排。

`Rank 349` 当前正落在这个情形：
- 它已经说明自己不是 `Rank 348` 的简单换皮；
- 但它还没有把“相对 `level-only carry` 的净增量”压成当前 desk 能采信的硬证据。

因此本轮不能再给开放式 `keep_P1`，更不能跳升 `P2`。

## 这轮真正被证伪/证弱的是什么
被证弱的不是 “funding+basis+persistence` 这套想法完全错”，而是：

> **在当前 runtime 可用证据里，它还不足以证明自己已经是 `BTC/ETH/SOL × 5m/15m × explicit after-cost` 下可迁移的 desk-ready survivor。**

这意味着当前最诚实的 verdict 不是“继续前排再看看”，而是：
- 保留这条对象的研究记录；
- 但把它移回 `background / P0`；
- 以后若有人明确要求 reopen，再基于真实 backtest / live-like evidence 重开。

## 对 runtime 的直接影响
- `Surviving candidate slot` 用尽唯一 follow-up 预算后清空；
- `Rank 349` 不升 `P2`；
- 对象退回 `Background pool / P0`；
- 当前前排主动作回到后续 `fresh intake`。

## 一句话结果（写回 state 用）
`Rank 349` 的唯一 survivor follow-up 已诚实收口：现有证据仍未把 `funding+basis+persistence+sign-flip/liquidity gate` 在 `BTC/ETH/SOL × 5m/15m × explicit after-cost` 下压成相对 `level-only carry` 的可迁移净增量，因此对象不升 `P2`，用尽 survivor 预算后退回 `background / P0`。
