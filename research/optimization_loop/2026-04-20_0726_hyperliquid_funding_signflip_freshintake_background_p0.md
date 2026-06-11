# Rank? / bidirectional funding sign-flip × 15m child execution
- time: 2026-04-20 07:26 UTC
- target: `research/quant_digests/2026-04-19_1932_hyperliquid-funding-signflip-shell.md`
- decision: `background/P0`

## 最小 honesty 检查
把这条壳压成最便宜的可执行下限后，只剩一个问题：**公开 funding-history 里，阈值触发 + sign-flip 的资金费率本体，能不能在统一双腿成本下留出可复制 after-cost pocket？**

## 看到的事实
- Hyperliquid 近 90d funding probe（BTC/ETH/SOL/HYPE）里，`1bp` 默认阈值对 `BTC/ETH/HYPE` 都是 `0` 次触发，只有 `SOL` 仍有 `11` 次，说明默认门槛对 majors 过稀疏。
- `0.5bp` 下，`BTC/ETH` 仍只有 `2/4` 次，`SOL` 才到 `56` 次且全为负 funding，`HYPE` 只有 `5` 次且全为正 funding。
- `0.25bp` 下，仍是明显 coin-specific：`SOL` 负 funding streak 很长，但 `BTC/ETH` 触发很少，`HYPE` 只是一小撮正 funding burst。

## 结论
- 这不是一个可稳定共用的多资产 front object。
- 它更像两个窄 pocket：`SOL` 的负 funding carry 与 `HYPE` 的正 funding carry；但阈值/方向/时钟都高度 coin-specific。
- 在需要 `15m child execution`、再加上真实开平、换仓、basis/滑点现实之后，当前证据不足以证明存在**不是单一 lucky coin 的可复制 after-cost pocket**。

## verdict
`background/P0`
