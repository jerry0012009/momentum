# Rank 316 / symmetric tiered maker ladder × inventory-skew / external hedge — fresh intake first verdict = keep_P1

- Time: 2026-04-03 20:06 UTC
- Target: `research/quant_digests/2026-04-03_1936_wintermute-hl-tiered-maker-ladder-alpha.md`
- Action: fresh intake first verdict
- Verdict: `keep_P1`
- Assigned Rank: `316`

## Why this changes runtime truth
这条对象已经不只是“观察 Wintermute 挂单画像”的 commentary。当前 digest 已把主语压缩得足够清楚：**Hyperliquid 单 venue 上的 symmetric tiered maker ladder，靠 spread capture / queue rent 赚钱，并用 inventory-skew 与必要时外部 hedge 控制 adverse selection**。这已经构成一条独立 raw alpha，而不是附着在别的方向策略上的执行备注。

对 fresh intake first verdict 来说，它已满足 `keep_P1` 门槛：
1. **主语清楚**：不是泛泛的 orderbook 观察，而是 `双边分层 maker quote -> 被动成交 -> inventory control / hedge` 的完整 maker raw alpha。
2. **最小实验壳清楚**：digest 已给出 `BTC/ETH/SOL`、`1s~5s` 采样、`1m/3m` 汇总、`3~5` 层 ladder、`对称/轻度 skew` 对照，以及 `5m/15m` 风险预算层的最小验证路径。
3. **公共数据路径清楚**：基于 Hyperliquid 公共 API 的 `openOrders / allMids / clearinghouseState` live probe 已验证结构今天仍存在，不依赖私有数据才能开始第一轮诚实验证。
4. **与现有前排证据轴不重合**：它补的是 maker / inventory-managed quoting 这条 execution-layer raw alpha，而不是再重复一条 taker/stat-arb admission 叙事。

## What it is not yet
这轮还不够直接升 `P2`，因为当前证据主要是：
- repo 规则级 source audit；
- 静态挂单与 inventory live probe；
- maker shell 的结构可复现，但还没有 fill-based 的净后生存证据。

也就是说，runtime truth 目前更像：

> `Rank 316` 已经证明自己是值得继续的一条独立 maker raw alpha，但还没证明在诚实的 fill / adverse-selection / refresh-friction 口径下能直接进入 desk admission。

因此最诚实的 first verdict 不是 `promote_P2`，而是先给 `keep_P1`，占用 survivor 的唯一一次 follow-up。

## Suggested one-shot survivor follow-up
唯一值得做的后续，不是继续复述 Wintermute 很会挂单，而是：
- 在统一 `BTC/ETH/SOL` shell 下，做 `3层/5层`、`对称/轻度 inventory skew` 的最小 maker simulator；
- 用同一口径回答 `gross spread capture - fee - short-horizon adverse selection - refresh/cancel friction` 后是否仍有可存活 pocket；
- 若只剩“静态 ladder 很漂亮”但 fill 后净后不存活，应直接收口到 `background/P0`；若在 majors 上已能看到诚实存活的 maker pocket，再考虑升 `P2`。

## Result sentence
`Rank 316`：Wintermute/HL symmetric tiered maker ladder 已具备清楚主语、公共 API 可复现数据路径与最小 maker 实验壳，足以作为独立 execution-layer raw alpha 保留；但当前仍缺 fill-based honesty 证据，因此本轮分配正式 `Rank 316` 并首判 `keep_P1`。