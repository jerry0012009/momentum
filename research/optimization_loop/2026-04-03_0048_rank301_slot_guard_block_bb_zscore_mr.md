# bot3 blocked — BB/z-score overshoot × RSI confirm × trend-veto mean-reversion intake hit survivor-slot guard

- Time: 2026-04-03 00:48 UTC
- Target: `research/quant_digests/2026-04-02_2356_bb-zscore-rsi-trendveto-meanreversion-alpha.md`
- Slot under execution: Fresh intake
- Outcome: `blocked`

## Why this cycle was blocked

按 digest 本身，这条题目已经足够证明它**不是单纯的指标拼盘换皮**：

> base alpha 是单币短周期 `overshoot snapback`；`z-score` 负责定义统计极端，`RSI` 与 `trend-veto` 只是 admission / veto，`ATR stop + BB mid exit + z-score bucket governance` 则把它写成了完整实验壳。

也就是说，从研究主语上看，它更像一条**可独立 intake 的 raw-alpha family**，而不是旧 `pairs / carry / breakout` 家族的措辞改写。

但是，本轮 **不能合法把它直接写成新的 `keep_P1`**，原因不是对象本身，而是当前 runtime 与 fixed policy 的槽位约束发生冲突：

1. 当前唯一 `Surviving candidate slot` 仍由 `Rank 300` 占用；
2. policy 明确要求：`Surviving candidate` 只能是上一条 fresh intake，且在该 survivor 的唯一 follow-up 诚实收口前，bot2 不得让新的 `keep_P1` 覆盖 survivor 槽位；
3. 对这条 BB/z-score MR 来说，当前证据又**还不足以直接跳到 `P2`**——因为主证据仍是源码结构与实验壳完整性，而不是已经收口的跨资产/时间/参数/成本后 first-pass admission；
4. 因此本轮若强行给 `keep_P1`，会制造第二个未收口 survivor；若强行给 `P2`，又会高估证据强度。

## System belief update

本轮真正新增的系统认知不是“这条线成立/不成立”，而是：

> `BB/z-score overshoot × RSI confirm × trend-veto` 这条单币 mean-reversion 题目**具备独立 raw-alpha 主语的候选资格**，但在 `Rank 300` survivor 尚未收口前，bot3 不能合法地把它写成新的 `keep_P1`；同时它当前证据仍不足以越过 survivor 直接升 `P2`，所以应按 policy 记为 `blocked`，等待 bot2 在后续轮次先收口前排 survivor 再重新 intake。

## Why not force a verdict anyway

- **不写 `background/P0`**：因为这会把“槽位冲突”误写成“题目本身被否”；当前并没有得到这样的负面证据。
- **不写 `keep_P1`**：因为会违反 `single survivor` 规则。
- **不写 `P2`**：因为还没到 admission 级别，不能靠“题目看起来完整”直接跳级。

## Runtime action intended

- 将本小点写成 `blocked`
- 在 `BOT2_BOT3_STATE.md` 中把该小点结果落为：
  - 它已被识别为具备独立 raw-alpha 候选资格；
  - 但因 `Rank 300` 仍占用 survivor slot，当前轮不得新开第二个 `keep_P1`；
  - 因当前证据又未到直升 `P2`，故本轮停止在 slot-guard blocked

## Reader-facing impact

无新的 reader-facing 页面；本轮是 policy guard 收口，不是对象本体 verdict 收口。
