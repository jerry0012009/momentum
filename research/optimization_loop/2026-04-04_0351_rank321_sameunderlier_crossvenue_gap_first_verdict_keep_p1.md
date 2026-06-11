# Rank 321 — same-underlier cross-venue gap mean reversion × latency budget first verdict：keep_P1

- Time: 2026-04-04 03:51 UTC
- Target: `research/quant_digests/2026-04-04_0146_sameunderlier-crossvenue-gap-latency-budget-alpha.md`
- Action type: fresh intake first verdict
- Verdict: `keep_P1`
- New formal rank assigned: `Rank 321`

## 结论
`same-underlier cross-venue gap mean reversion × latency budget` 已足够作为一条清楚的 short-cycle relative-value raw alpha 母板进入 `P1`，因为它的主语不是“模拟器会不会太理想”，而是非常明确的 **同一标的跨 venue 短暂错价会向共同价格回归**，并且 digest 已经把最小 `entry / exit / threshold / cost / latency / inventory-funded vs transfer-cooled` 壳写完整。与此同时，这轮证据也同样说明它现在还**不是**可以直接升入 `P2` 的 desk-ready 候选：公共 `1m` 快检里可见的 gross convergence 普遍只有亚 `1~2 bps` 量级，repo stress test 也清楚显示只多 `1` 个 step latency 就能从正值翻负，因此当前更诚实的定位是“值得保留并再做一次唯一的 survivor follow-up，回答它到底是否存在可迁移的低延迟最小 desk lane”，而不是假装 bar-level 价差回归已经等于可实盘部署。

## 为什么不是 background/P0
1. **base alpha 很清楚**：主语就是 `same-underlier cross-venue gap -> convergence`，不是 execution 评论、也不是泛套利综述。
2. **策略壳完整**：digest 已明确写出 `gap 定义 / rich-cheap 动态判定 / entry threshold / convergence exit / timeout exit / sizing / inventory cap / latency bucket`，不是只有概念没有策略骨架。
3. **最小诚实证据足够证明“有东西”**：repo 的 stress study 明确给出 latency cliff；本地 `Binance/OKX 1m` 粗检也证明 venue-gap 回归倾向在 BTC/ETH/SOL 上确实存在，而不是纯 notebook 幻觉。
4. **当前不足是执行条件苛刻，不是 alpha 主语缺失**：真正的问题是 edge 极薄、极度依赖费用/延迟/双腿成交条件，所以它应先回答“有没有诚实可迁移的低延迟 lane”，而不是直接被打回背景池。

## 为什么先停在 P1，而不是直接升 P2
- 现有 reader-facing 证据仍以 synthetic stress study + `1m` public close precheck 为主，尚未完成真正有决策意义的 `1s/5s top-of-book + latency bucket + net-of-fee/spread` admission。
- 当前最强信息其实是 **latency 是生死线**，而不是“已经找到可稳定 paper 的净边”。这更像一条需要先验证 infra 约束能否留下诚实 lane 的高要求 raw alpha。
- 因此最合规的下一步不是重复 repo 机制转述，而是做 **一次唯一 survivor follow-up**：明确它是否存在至少一条可迁移的 `BTC/ETH/SOL × Binance/OKX(/Bybit) × low-latency inventory-funded` 最小 desk lane；若没有，就应及时收口而不是继续美化。

## 本轮写回 runtime 的系统认知变化
- 该对象获得正式 durable identity：`Rank 321`。
- 该对象从 fresh intake first verdict 收口到 `keep_P1`。
- 该对象占用当前唯一 `Surviving candidate slot`，等待一次最小 decisive follow-up。

## Reader-facing一句话
`Rank 321` 不是“又一个跨所模拟器”；它已经足够证明自己是一条主语清楚的 `same-underlier cross-venue stat-arb` 母板，但目前仍是**高度基础设施敏感**的候选，所以先进入 `P1 survivor`，下一步只该回答是否真的存在一条诚实可迁移的低延迟 desk lane。
