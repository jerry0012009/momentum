# Rankless fresh intake verdict — OFI 极值 × 3~5s microburst continuation -> background/P0

- 时间：2026-04-25 15:48 UTC
- 执行轮次：bot3 13m auto loop
- 对象：`research/quant_digests/2026-04-25_1515_ofi-jthreshold-microburst-alpha.md`
- 动作：fresh intake first verdict
- 结论：`1s OFI 极值 × 3~5s microburst continuation` 本轮诚实收口为 `background/P0`，不分配 Rank。

## 为什么这一步已经足够改变系统认知
这条线的 public sanity probe 只证明了 **秒级 OFI 极值后仍能测到极薄的同向漂移**，没有证明它在统一执行现实口径下还是一个可保留的独立交易 pocket：

1. digest 里唯一 reader-facing 快检只有最近约 `19m` 的 Binance 单 venue snapshot，样本窗口极短；
2. `3s` markout 只有约 `+0.167 bps`（正向极值）与 `+0.145 bps`（反向极值按做空方向记），量级明显低于常见 taker friction，也不足以证明 maker-first 后仍可稳定留存；
3. repo 的价值更多在于把 OFI 做成 `J-threshold + risk realism` 的研究壳，而不是给出已经跨时间、跨 venue、跨 friction 仍成立的可交易 pocket；
4. 当前最像真的 reader-facing结论是：它可以作为 `maker skew / quote bias / veto / router` 的微结构原料，但还不够支撑 fresh intake 直接 `keep_P1`。

## 最小 decisive blocker
缺的不是再多看一段短窗 recent snapshot，而是 **至少一个跨时间且带 friction ladder 的可保留 pocket**：需要证明某个明确持有窗 / 执行方式在 `>=1 bps` 级现实成本假设下仍有稳定净 edge。现有 digest 没做到这一点。

## 本轮 runtime verdict
- slot verdict: `background/P0`
- level change: 无（未进入 P1，因此不分配 Rank）
- 可保留价值：仅保留为未来可能的 `microstructure overlay / veto / router ingredient` 背景素材，不进入当前前排。

## 写回 state 的一句话结果
`1s OFI 极值 × 3~5s microburst continuation` fresh intake 已诚实收口 `background/P0`：public probe 只证明秒级方向漂移仍“活着”，但 `3s` markout 仅约 `0.15~0.17 bps` 且样本只来自单 venue 短窗，尚无跨时间 / friction 后仍可保留的独立交易 pocket，当前更适合作为 maker-skew / veto / router 原料而非 `keep_P1` 候选。
