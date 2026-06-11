# Rank intake log — fill-aware OFI × quote-join flow-control shell

- Time: 2026-04-08 23:40 UTC
- Target: `research/quant_digests/2026-04-08_2249_fillaware-ofi-flowcontrol-shell.md`
- Slot: `Fresh intake`
- Action: 对 `fill-aware OFI × quote-join flow-control shell` 做 fresh intake 首判，判断它是否已经压成独立微观结构 raw alpha，而不是把既有 order-flow / queue-imbalance continuation 家族包装成更完整 execution shell。
- Verdict: `background / P0`

## Why this verdict changes system truth
这条对象当前真正新增的，是把 `OFI / queue imbalance / microprice deviation` 接到 `maker-first join/take + fill model + inventory cap + fee/rebate hurdle` 的**执行壳完整度**，而不是补出一个不被既有 signed-flow / OFI continuation family 吸收的独立 alpha 主语。它最值钱的部分是 execution realism：`alpha_bps -> join/take router -> fill / inventory / cost gate` 的链条写得很完整；但 digest 自己的 portability probe 已经说明，离开真 L2 / queue / microprice / fill realism 之后，public kline signed-flow proxy 在 BTC 上 next `1/3` bar 同向收益约 `-0.384 / -0.666 bps`，连方向都没站住，ETH / SOL 也只是弱正提示。

## Decisive reason
按本轮 success criterion，若它要留在前排，必须证明 `OFI + queue imbalance + microprice deviation -> maker-first join/take router` 本身能作为一个**独立 queue-facing 主语**站住，而不是“既有 OFI continuation + 更诚实 execution shell”。目前高置信答案是否定的：
1. raw alpha 主语仍然是熟悉的 `order-flow / queue-imbalance continuation`；
2. 新增信息主要在 fill-aware / maker-taker router / fee realism；
3. 一旦离开真 L2 与 fill model，这条边在便宜代理上并没有表现出可迁移、可独立命名的 raw alpha 边界。

## Honesty / execution realism note
本对象不是因为发现致命造假而出局，恰恰相反：它最诚实的部分就是承认 **没有真 L2 + fill realism，就别假装自己已经验证了 alpha**。但这也正说明它更像一个可复用 execution shell / admission overlay，而不是当前应单独升格的 fresh raw-alpha intake。

## Runtime consequence
- `Fresh intake slot` 对该对象的 first verdict 收口为 `background / P0`
- 不分配 `Rank`（因为未达到 `keep_P1`）
- `cycle_plan` 第 1 项写回 `done`
- 前排未产生新的 `Surviving candidate / Active P2 / Paper launch queue` 迁移

## Result sentence
`fill-aware OFI × quote-join flow-control shell` 当前新增的是对既有 OFI / queue-imbalance continuation 家族的 execution realism 补强，而不是已脱离真 L2 + fill model 依赖、可独立站住的 raw alpha 主语，因此本轮 fresh intake 首判直接收口为 `background / P0`.
