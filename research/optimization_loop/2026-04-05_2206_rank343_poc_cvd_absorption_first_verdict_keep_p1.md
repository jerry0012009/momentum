# Rank 343 — POC + CVD absorption first verdict: keep_P1

- Time: 2026-04-05 22:06 UTC
- Target: `research/quant_digests/2026-04-05_1755_poc-cvd-absorption-alpha.md`
- Slot before execution: `Fresh intake`
- Assigned Rank: `343`
- Verdict: `keep_P1`
- Layer transition: `fresh intake -> Surviving candidate`

## Why this changed system belief

本轮 first verdict 结论是：`POC + CVD absorption` 不是常见 volume-profile / divergence / absorption 术语的重新拼接，而是一条已经把 **状态锚点、触发、方向、执行边界与 transfer boundary** 压清的单资产 raw alpha 壳，足以进入 `keep_P1`。

一句话概括：

> 当价格位于 rolling POC 一侧、与 POC 保持可交易距离，同时价格斜率与 CVD 斜率反向，说明主动流动与价格路径错位、被动流动性在吸收，该状态更容易朝 POC / 局部公允区回摆。

## Why it passes first-verdict threshold

### 1) State definition 是清楚的，不是泛化 orderflow 叙事
对象把状态压成了四件一起成立：

- `rolling POC` 作为公允锚点；
- `price vs CVD slope disagreement` 作为 absorption 触发；
- `distance_to_POC` 落在可交易区间；
- `body/ATR` 过滤掉无效小波动。

这不是“价格背离 + 成交流异常”这种松散描述，而是明确的 `POC-proximal absorption fade` 壳。

### 2) Trigger timing 与 direction shell 已经可复现
当前定义不是模糊地说“出现 absorption 就做反转”，而是明确：

- `cp < poc` 且 `bullish_absorption` → 做多，赌回到 POC；
- `cp > poc` 且 `bearish_absorption` → 做空，赌回到 POC。

也就是说，它给出的不是描述性 insight，而是可直接 event-study / backtest 的方向壳。

### 3) Execution shell 与 post-cost 边界已被说清
这份 intake 不只是讲信号，还明确写了：

- 固定 `TP/SL` 而不是用 trailing 包装；
- fee/cost 已进入验证；
- 真实 aggTrades CVD 与 CLV proxy 做过对照；
- 最重要的是直接给出了 transfer boundary：`1H` 能活，`15m/30m/2h/4h` 直接压缩不活。

这意味着对象不是“先吹概念，后补诚实性”，而是已经把最关键的负迁移边界一并交代出来。

### 4) 它是 distinct raw alpha，不只是常见 breakout/fade filter
这个对象的独立性来自三层组合：

1. `volume-profile fair-value anchor`；
2. `signed-flow disagreement / absorption`；
3. `POC-distance-bounded mean reversion clock`。

相比纯 CVD divergence、纯 VPVR fade、纯 breakout exhaustion，它多了明确的结构锚点与方向条件，因此可以视作独立 raw alpha family member，而不只是已有策略上的一个 filter。

## Why it is only keep_P1, not higher

虽然 first verdict 通过，但当前仍不足以直接升到 `P2`，因为 admission-ready 的关键问题还没被压实：

- 这条壳是否只在 `BTC/ETH/SOL 1H` 上成立，还是能稳定外推到其他 liquid futures；
- 若 short-cycle desk 真要吸收它，`1H parent -> 15m child` 的桥接是否真实存在，而不是只剩 HTF 独立策略；
- `CLV proxy` 在 desk 自己的数据与执行口径下是否真的足够，不会因为更细颗粒流量定义而崩掉；
- after-cost / post-slippage / timeout 之后，母信号对子执行是否仍有净提升。

所以本轮最诚实的位置是 `keep_P1`，先保留一轮 survivor follow-up，而不是直接推进到 `P2`。

## Suggested single survivor follow-up

若下一轮使用 survivor 唯一一次 follow-up，最合适的唯一问题是：

> `1H POC-proximal absorption` 作为母信号，是否真的能在 `15m child execution` 上留下可迁移的 short-cycle edge，而不是只能停留在 HTF 独立策略层？

优先核对：

- `1H state -> 15m entry` 的窗口与 half-life；
- `next-open / first pullback / failed extension` 三类 child entry 哪个最诚实；
- `2/4/6 bps` 成本后是否仍有正增益；
- direct `15m clone` 继续失效是否能作为负对照成立。

## Runtime sentence to write back

`Rank 343：POC + CVD absorption 已完成 fresh intake first verdict；对象把 rolling POC 锚点、price-vs-CVD absorption trigger、POC-distance 约束与 1H->15m transfer boundary 压成了独立 single-asset raw alpha 壳，因此进入 keep_P1，并占据 surviving candidate slot。`

## Ops note

- 本轮应刷新首页。
- 本轮应发送中文邮件摘要。
