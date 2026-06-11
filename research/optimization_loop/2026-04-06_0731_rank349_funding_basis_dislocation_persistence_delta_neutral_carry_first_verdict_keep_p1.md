# Rank 349 / funding-basis dislocation persistence × delta-neutral carry — fresh intake first verdict = keep_P1

- 时间：2026-04-06 07:31 UTC
- 对象：`research/quant_digests/2026-04-06_0424_funding-basis-persistence-deltaneutral-alpha.md`
- 轮次角色：bot3 当前轮 `fresh intake` first verdict
- 结论：`keep_P1`
- 正式 Rank：`349`

## 本轮要回答的唯一问题
这条 `funding/basis dislocation persistence × delta-neutral carry`，是不是值得留在前排继续做那唯一一次 survivor follow-up；还是它其实只是旧 funding carry 家族的参数换皮，应该直接回 `background / P0`。

## 本轮新结论
`Rank 349` 值得保留为 `keep_P1`。

原因不是“repo 提到了 deep learning”或者“funding carry 听起来很赚钱”，而是这条对象确实给出了一个和 `Rank 348` 不同的独立主语：

- `Rank 348` 的主语是：`basis relaxation -> carry timing -> regime-sized hold governance`
- `Rank 349` 的主语是：`funding level + basis deviation + persistence horizon + sign-flip/liquidity gate` 共同决定 **哪一笔 delta-neutral carry 值得持有到下一次或下几次 funding payoff**

也就是说，`Rank 349` 不是在原 carry 上再多加一个 sizing overlay，而是在回答另一件更前面的事：

> 不是“谁 funding 最肥就空谁”，而是“哪种 funding+basis 偏离在成本后仍有足够高的持续性，值得做成 delta-neutral carry”。

这已经构成独立的 raw alpha / carry shell，值得进入唯一 survivor follow-up。

## 为什么这轮不是直接升 P2
当前 digest 里，骨架已经足够清楚，但证据仍主要停留在：

- repo proposal / 变量表
- 官方 funding 机制文档
- perpetual futures 理论与结构性偏离论文
- 公开 API 可行性

它还没有把最关键的 desk admission 句子压实：

- 在 `BTC/ETH/SOL`
- 用 `5m/15m` 决策频率
- 在显式 `after-cost`
- 对照 `level-only carry`

时，`funding+basis+persistence+sign-flip veto` 是否真的保留稳定、可迁移的净增量。

所以本轮最诚实的层级不是 `promote_P2`，而是：

- 先给正式 `Rank 349`
- 保留为 `keep_P1`
- 把它送入唯一一次 survivor follow-up

## 为什么它不是直接回 background / P0
因为它并不只是“old funding carry 再换个词”。

这条对象至少已经把以下几层独立骨架压清：

1. **state 不是单看 funding level**
   - 同时看 `funding`、`basis`、`z-score`、`sign flip risk`、`liquidity / OI`
2. **payoff event 不是逐根 K 线方向**
   - 而是“下一笔 / 下几笔 funding 是否还能兑现 + basis 是否回归”
3. **治理逻辑是 carry persistence，不是纯 sizing**
   - 核心在 `hold horizon / sign-flip veto / liquidity gate`
4. **和 short-cycle desk 有可翻译接口**
   - `1m` 更新状态
   - `5m/15m` 做 admission / continue / exit

这几层合在一起，足以说明它是可检验的新前排对象，而不是空泛叙事。

## 唯一 survivor follow-up 应该补什么
下一步不该再重复争论“它和旧 funding carry 是否同一个家族”。

唯一高杠杆 follow-up 应该直接检查：

- `BTC / ETH / SOL`
- `5m / 15m`
- `explicit after-cost`
- baseline: `level-only carry`
- candidate: `funding + basis + persistence + sign-flip veto (+ liquidity gate)`

是否真的带来：

- 更高净收益 / 更低回撤
- 更少 sign-flip 前误入场
- 更稳定的 next-tick / next-few-ticks capture
- 可迁移到 desk 当前周期，而不是只停留在 8h funding 叙事

## 对 runtime 的直接影响
- 分配新正式 `Rank 349`
- 当前 fresh intake first verdict = `keep_P1`
- 进入 `Surviving candidate slot`
- `followup_budget_remaining = 1`

## 一句话结果（写回 state 用）
`Rank 349` 完成 fresh intake first verdict：其独立增量是 `funding+basis` 偏离能否跨到下一笔或下几笔 funding 的 persistence / sign-flip / liquidity 联合治理，而不是 `Rank 348` 那条 `basis relaxation + regime-sized governance` 的同义改写，因此保留为 `keep_P1` 并进入唯一 survivor follow-up。
