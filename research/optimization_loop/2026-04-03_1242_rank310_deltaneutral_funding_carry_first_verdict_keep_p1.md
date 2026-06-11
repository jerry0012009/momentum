# Rank 310 — delta-neutral ETH funding carry gate first verdict = keep_P1

- Time: 2026-04-03 12:42 UTC
- Target: `research/quant_digests/2026-04-03_1108_deltaneutral-eth-funding-carry-gate-alpha.md`
- Slot: fresh intake
- Verdict: `keep_P1`
- Assigned rank: `Rank 310`

## 本轮只回答一个问题
这条 `7d funding carry gate × delta-neutral 对冲壳`，是不是足够像一条**可独立 desk 化的 raw alpha**，而不只是单一高 funding 年景里的课程项目回测壳？

本轮结论：**是，够进入 P1；但还不够直接升 P2。**

## 为什么给 `keep_P1`
1. **alpha 主语清楚，而且不是 filter 冒充 alpha**
   - 收益来源明确是 `spot long + perp short` 的 funding carry。
   - `7d annualized funding > hurdle` 只是 gate，不是把方向性收益伪装成 carry。

2. **最小策略壳完整**
   - 有清楚的 entry / exit（`7d funding hurdle` 上下切换）。
   - 有明确成本假设（进出总计 `0.20%`）。
   - 有风险主语（funding reversal、margin/liquidation、hedge drift）。
   - 有公开 funding / price 数据路径，理论上可直接复现。

3. **与现有 trend / MR 家族有收益来源区分**
   - 这不是再拼一层 trend 或 mean-reversion 壳。
   - 它提供的是 carry/funding 这一条不同经济驱动，具备组合层面的潜在价值。

## 为什么本轮不直接升 `P2`
1. **当前证据仍然主要绑定单 repo 的 ETH/Bybit 2021–2026 叙事**
   - digest 里给出的是完整策略定义，但公开证据还没有把 `BTC / SOL / 多交易所` 的稳定性做成 admission 级别材料。

2. **regime 依赖已经被作者自己承认**
   - 材料明确承认结果对 `2021 高 funding 环境` 依赖较高。
   - 这说明它更像“值得继续做一次 survivor follow-up 的 carry 候选”，而不是已经完成 admission 的成熟对象。

3. **成本 realism 还不够 desk 级**
   - 当前只有固定 `0.20%` 交易成本壳。
   - 还没有把 maker/taker、funding reversal、再平衡漂移、交易所可借现货/替代现货代理等现实摩擦拆干净。

## 对系统认知的更新
`Rank 310` 不是“又一篇 funding 叙事摘要”，而是一条**可独立复现、可直接接到策略层的 delta-neutral carry raw alpha 候选**；但当前仍停留在单 repo、单主要标的、单一成本壳的 first-verdict 阶段，因此本轮只进入 `P1`，保留一次 survivor follow-up 去回答“跨币种/跨 regime/更真实成本后是否还成立”。

## 建议的唯一 survivor follow-up 方向
若下一轮要做唯一一次便宜且 decisive 的 follow-up，应该优先回答：

> 在 `BTC / ETH / SOL` 至少三币、并把 funding reversal 与更真实 execution friction 纳入后，这条 carry gate 还是否保留正的 post-cost expectancy？

如果答案是肯定的，再考虑升 `P2`；否则就诚实收口回 `background/P0`。
