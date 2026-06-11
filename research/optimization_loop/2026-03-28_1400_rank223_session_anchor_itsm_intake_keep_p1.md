# Rank 223 / session-anchor ITSM × low-liq low-ID gate intake keep P1

- Time: 2026-03-28 14:00 UTC
- Target: `research/quant_digests/2026-03-28_1304_session-anchor-itsm-liquidity-gate.md`
- Action: fresh intake first verdict
- Verdict: `keep_P1`
- Rank: `223`

## What changed
这条对象留下来的不是“再讲一次 generic intraday TSMOM”，而是一条 **更窄、可直接 desk 化的 event-anchor continuation spec**：

> **只在真实事件锚点后观察首段 `5m/15m` 收益方向，交易下一段同向续动，再叠加 `low-liq / low-ID` gate。**

这和已被否决的 `Rank 163 / Intraday TSMOM high-vol × low-liq pocket alpha` 不是同一个对象。`Rank 163` 失败的是 **全天候 own-past bar-bar continuation** 在更接近执行现实后成本全面转负；而这条新 digest 明确把 alpha 本体缩到 **外生锚点后的首段价格发现尚未完成** 这一更具体的机制上，scope、触发时钟和 gate 结构都变了，因此它是一个合法的新 fresh intake，而不是旧 rank 的自动 reopen。

## Why it is not P2 yet
1. 目前证据仍主要来自股票论文与 crypto desk translation，**还没有本地最小 transfer 结果** 去证明 `00:00 / 08:00 / 13:30 / 16:00 UTC` 这些锚点后的 `5m/15m -> 5m/15m` continuation 在 BTC/ETH 上成本后为正。
2. digest 虽然把实验设计写得很清楚，但这仍属于 **spec-quality evidence**，不是 admission-quality evidence；连最基础的 anchor-by-anchor `hit rate / avg bps / post-cost pnl` 都还没落到本地 artifact。
3. 低流动性与低 ID 在这条对象里应当只是增强器；在还没先确认 **anchor-only 裸 alpha** 的前提下，直接升 `P2` 会把 filter 当成本体，风险太大。

## Why it still deserves keep_P1
1. alpha 本体足够清楚，而且比 `Rank 163` 更接近可交易现实：不是全天候追每根 bar，而是只在 **有限、可枚举、可解释的 event clock** 上开火，天然更 sparse，也更有机会避开“信号到处都是、成本把边吃光”的老问题。
2. digest 已经把最小可执行 spec 压缩得足够具体：
   - anchors: `00:00`, `08:00`, `13:30`, `16:00 UTC`
   - formation: `5m`, `15m`
   - holding: `5m`, `15m`
   - symbols: `BTCUSDT perp`, `ETHUSDT perp`
   - cost: round-trip `4bps` first, then `6bps` stress
3. 它天然给出一个单一、便宜、决定性的 survivor follow-up：**先只回答 anchor-only 裸 alpha 在 BTC/ETH 上是否存在净边；若连这一层都不成立，就直接收口回 background，而不是继续补 low-liq / low-ID 的装饰性研究。**

## Minimal honest next follow-up
若进入 survivor，唯一一次 cheap decisive follow-up 应只做：
- 在 Binance perp `1m` 数据上，对 `BTC/ETH` 的 `00:00 / 08:00 / 13:30 / 16:00 UTC` 四类锚点并排做 strict A/B；
- formation 只跑 `5m` 与 `15m`，holding 只跑 `5m` 与 `15m`；
- 统一 `next-bar open / no-overlap / round-trip 4bps + 6bps stress`；
- 直接回答：**哪怕不加 `low-liq / low-ID` gate，session-anchor 首段方向 -> 下一段同向续动在至少一个 anchor × horizon pocket 上是否还能留下正的 after-cost avg pnl。**

若答案是否定的，这条线就应按 `keep_P1 后转 background` 收口；若答案肯定，再进入更窄的 gate admission，而不是反过来先堆 filter。

## Runtime implication
- 正式分配 `Rank 223`。
- 层级定性为 `P1`，**不直接升 `P2`**。
- 当前 `Surviving candidate slot` 为空，因此这条对象应占据 survivor 槽位，并恢复 **1 次** 最小 decisive follow-up 预算。

## Result sentence
`Rank 223 / session-anchor ITSM × low-liq low-ID gate` fresh intake 完成并保留为 `keep_P1`：它不是已被否决的全天候 `Rank 163` ITSM pocket 的自动 reopen，而是把对象诚实缩到“真实事件锚点后的首段续动”这一更 sparse 的 raw alpha；但在本地还没有任何 anchor-by-anchor after-cost transfer 结果前，仍不足以直接升 `P2`。