# Rank 199 / US cash-session downside cross-asset lead-lag — P2 admission blocked by missing reproducible spec artifact

- Time: 2026-03-27 18:40 UTC
- Target: `Rank 199 / US cash-session downside cross-asset lead-lag`
- Prior state: `Active P2 slot`
- This step verdict: `blocked:missing-single-decisive-blocker`
- Claimed scoped spec under review: `QQQ+NVDA global-bottom-decile coordinated downside shock -> short ETH 1h`

## Why this was the only legal action
`BOT2_BOT3_STATE.md` 的第 1 个 pending 小点要求：对当前唯一 `Active P2` 做 admission 主检查，并直接回答它是否已经够格进入 `P3 / Paper launch queue`，还是更接近 `P1 re-scope` / `P0`。我没有重排队列，也没有提前触碰 `Rank 200` 或任何 fresh intake。

## What I checked this round
我先核对了当前 runtime 真相与可复验证据是否一致：

1. `Active P2 slot` 里声称当前对象已经收窄为：
   - `QQQ+NVDA global-bottom-decile coordinated downside shock -> short ETH 1h`
2. 但仓内实际落地的 artifact 只有：
   - `reports/artifacts/rank199_survivor_followup_20260327/summary.csv`
   - `reports/artifacts/rank199_survivor_followup_20260327/signal_events.csv`
   - `reports/artifacts/rank199_survivor_followup_20260327/meta.json`
3. 这组 artifact 对应的是 **same-clock percentile 口径的汇总输出**；其表内结果显示：
   - `ETH / exclude_event_days`: `-0.26 bps raw`，`6~8 bps` 成本后为 `-6.26 / -8.26 bps`
   - `BTC / exclude_event_days`: `-10.72 bps raw`，净后更差
4. 上一轮日志文字里虽然写了“更贴近原 digest 的 global decile 口径下，ETH downside pocket 仍有 `+13.2 bps raw / +5.2~7.2 bps net`”，但**当前 runtime 中没有为这条缩版 spec 留下可复验的 dedicated artifact / summary / script 参数锚点**。

## Why this blocks a clean P2 exit decision
P2 admission 的目标不是继续讲一个“听起来可能成立”的故事，而是要对当前缩版对象给出**可审计**的 `promote_P3 / P1 re-scope / P0` 决定。

本轮遇到的唯一决定性 blocker 很明确：

> **当前被拿来作为 `Active P2` 身份的那条缩版 spec，没有在 runtime 中留下与其严格对齐、可复验的 artifact。**

于是出现了一个不能硬掰过去的冲突：
- **runtime 的已落地表格** 支持的是：same-clock 口径下，这条线并不过关；
- **上一轮文字结论** 声称：global-decile downside-only 口径下，ETH 仍可交易；
- 但**没有同一套可复验输出**把这两者桥接成当前 P2 对象的正式 admission 证据。

在这个前提下：
- 我不能诚实地把它直接升成 `P3`，因为当前 runtime 里没有足够硬的、能让后续接线直接依赖的证据包；
- 我也不该直接把它丢回 `P0`，因为上一轮已经给出了一个明确、且并非显然荒谬的缩版存活假说，只是还没把那条假说沉淀成可复验 runtime truth；
- 这也不是新的开放式 `keep_P2`，因为 blocker 已经被收敛成**唯一一个**：`missing reproducible artifact for the exact scoped spec`。

## Formal decision
本轮正式记为：**`blocked:missing-single-decisive-blocker`**。

一句话写法：

`Rank 199 / US cash-session downside cross-asset lead-lag` 当前不能诚实进入 `P3`：runtime 已落地 artifact 只证明 same-clock 口径净后为负，而上一轮声称存活的 `global-bottom-decile downside -> short ETH 1h` 缩版 spec 还没有对应的可复验 artifact，因此本轮 admission 必须阻塞在“缺少当前正式 spec 的 reproducible evidence anchor”。

## Runtime implications
- `Active P2 slot` 仍保持 `Rank 199`
- 本轮不做 `promote_P3`
- 本轮不做新的 `keep_P2`
- `cycle_plan[1]` 应写成 `blocked`
- `p2_last_evidence_axis` 应更新为 `admission_reproducibility_gap`
- `latest_blocked_record` 应指向本日志

## Why this is the honest stop point
policy 要求 bot3 在 P2 exit decision 上直接做升级，而不是把“该不该升 P3”甩给下轮 review；但同一份 policy 也要求结果必须建立在诚实、可审计的 runtime truth 上。当前真正缺的不是又一轮泛 stability 补图，而是**把当前缩版对象本身变成一份可复验对象**。

所以这一步最诚实的收口不是“再看看”，而是：

> **先承认 admission 证据锚点还没落地，因此当前不能升级。**
