# Rankless fresh intake — Hyperliquid public trigger / liquidation cluster continuation

- Time: 2026-04-03 23:28 UTC
- Target: `research/quant_digests/2026-04-03_1425_hyperliquid-public-trigger-cluster-alpha.md`
- Action: fresh intake first verdict
- Verdict: `background/P0`

## Why this round closes to P0

这条线的优点很清楚：
- Hyperliquid 的 `frontendOpenOrders` / `clearinghouseState` / `allMids` 的确公开可拉；
- `public trigger / liquidation cluster -> short-horizon continuation` 也确实是一个像样的 event-driven 研究方向；
- `1m/3m/5m` 的最小 event shell、cluster score、距离门槛和成本口径都已经能写成实验草图。

但按这轮 fresh intake 的收口标准，它**还没有脱离“先解决 wallet discovery 才能成立”的阶段**，因此当前不应占前排资源：

1. digest 自带的 live probe 已把最关键问题说透：repo 示例 `13` 个钱包白名单在 `BTC/ETH/SOL` 上只扫到稀疏公开数据，`1%` 邻域内没有可交易密集 cluster；
2. 也就是说，当前真正的决定性瓶颈不是 cluster continuation 公式本身，而是**如何持续发现/更新高活跃钱包池**；
3. 在 discovery 层没补出来之前，所谓最小 `1m/3m/5m` shell 仍主要建立在“未来先把地址发现工程做好”的前提上，而不是已经可以直接复现的独立 raw alpha 壳；
4. 因而这轮对象更像一条值得保留的 research direction，而不是已经足够拿到 `keep_P1` 锁槽资格的 fresh intake。

## What changed in runtime truth

系统认知更新为：

> `Hyperliquid public trigger / liquidation cluster continuation` 的公开 API 路径成立，但当前 edge 是否可交易，主要仍取决于尚未落成的 wallet discovery 层；在 discovery 缺位下，它还不是一个脱离地址发现工程、可直接前排推进的独立 raw alpha，因此本轮 fresh intake first verdict 直接收口到 `background/P0`。

## Notes

- 这不是否定 cluster-based stress-path 研究方向本身；
- 只是按 bot2/bot3 当前 policy，它还没有达到需要占用 survivor / P2 槽位的成熟度；
- 若未来有独立的动态 wallet discovery 证据壳或更密的公开 cluster replay，再由人工明确 `reopen` 更合适。
