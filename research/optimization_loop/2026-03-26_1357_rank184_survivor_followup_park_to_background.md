# Rank 184 / cross-venue cheapest-spot-richest-perp contango carry — survivor follow-up park_to_background

- Time: 2026-03-26 13:57 UTC
- Executor: bot3 auto 13m loop
- Source record: `research/optimization_loop/2026-03-26_1322_rank184_cross_venue_contango_intake_keep_p1.md`
- Source digest: `research/quant_digests/2026-03-26_1122_cross-exchange-cheapest-spot-richest-perp-contango.md`
- Object: `Rank 184 / cross-venue cheapest-spot / richest-perp fee-adjusted contango carry`
- Verdict: `park_to_background`

## What this follow-up had to answer
按当前 runtime，`Rank 184` 作为 survivor 只允许做一次便宜 follow-up，且问题被限定为：

> 它是否只在 `altcoin dislocation / maker-fee pocket / 更低费率层级` 中才真正可活？

这轮不能再回到 `majors taker/taker` 的重复验证，也不能把“也许换个 fee tier 就行”继续当开放式研究 backlog。

## Evidence used this round
本轮没有新增 repo 叙事，而是直接用 intake 时已经拿到、且足以决定 survivor 去留的证据做收口：

1. `research/quant_digests/2026-03-26_1122_cross-exchange-cheapest-spot-richest-perp-contango.md`
2. `reports/artifacts/quant_digests/cross_exchange_contango_20260326_live_summary.csv`
3. `reports/artifacts/quant_digests/cross_exchange_contango_20260326_top6_snapshot.json`

其中最关键的事实是：

- 24 次 `BTC` 秒级快照里，最佳 fee-adjusted net spread **平均约 -20.1bp**，最好一次也只有 **-18.5bp**；
- 超过代码阈值 `15bp` 的次数是 **0/24**；
- top-6 snapshot 不只 `BTC/ETH` 为负，连 `SOL/XRP/ADA/DOGE` 也仍是 **-19bp ~ -30bp** 的负毛边；
- 因而当前公开 quick check 并没有给出一个已经被确认的 `altcoin pocket`，更没有给出一个已经 desk 化的 `maker-fee pocket / lower-fee-tier pocket` exact object。

## Why this is a park, not a P2 promotion
`Rank 184` intake 时保留下来的，是一条结构完整的 raw alpha 本体；这没有变。

但 survivor 轮需要的是：
- 要么证明它已经缩到一个**明确、可继续 admission 的 pocket**；
- 要么诚实承认目前只剩“换 alt / 换 maker / 换更低费率也许能活”的开放式猜想。

当前证据属于后者。

更具体地说：

1. **`altcoin dislocation` 仍未被具体化成对象。**
   现有公开快照里，手头能看到的几个 liquid alts（`SOL/XRP/ADA/DOGE`）仍然全部 fee-adjusted 为负；这不足以支持“已找到可保留的 alt pocket”。

2. **`maker-fee pocket / lower-fee-tier pocket` 仍只是执行假设，不是已经验证的幸存对象。**
   digest 确实指出这条线的可活性可能强依赖 fee tier 与 maker 化，但本轮并没有任何已验证的 break-even 曲线、venue-tier 切片、或可直接 admission 的 exact spec。

3. **继续保留只会把 survivor 轮拖成开放式 wishlist。**
   policy 明确要求 survivor 只有这一次 cheap follow-up；如果这一轮仍然只能得出“可能活在某些更优 pocket”而没有落到唯一明确对象，就应诚实收口，而不是继续占用前排。

## Decision
本轮收口结论是：

> `Rank 184 / cross-venue cheapest-spot-richest-perp contango carry` 当前只能停留在“结构上成立、但尚未找到被公开证据确认的可活 pocket”的状态；因此 survivor follow-up 结束后应 `park_to_background`，不升 `P2`。

## Reader-facing result
`Rank 184 / cross-venue cheapest-spot-richest-perp contango carry` 的 survivor 唯一 follow-up 已诚实收口为 `park_to_background`：当前公开证据仍只支持“这是一条结构清楚的 raw alpha”，但并未确认任何足够具体、可 admission 的 `altcoin dislocation / maker-fee / lower-fee-tier` 存活 pocket；在 majors 与已抽到的 liquid alts 上，fee-adjusted spread 依旧普遍为负，因此现阶段不值得升入 `P2`。
