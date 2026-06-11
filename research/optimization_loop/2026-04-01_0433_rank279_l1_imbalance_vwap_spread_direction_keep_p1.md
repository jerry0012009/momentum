# Rank 279 — L1 imbalance × VWAP spread direction alpha — fresh intake first verdict = keep_P1

- Time: 2026-04-01 04:33 UTC
- Target: `research/quant_digests/2026-04-01_0138_l1-imbalance-vwap-spread-direction-alpha.md`
- Slot: Fresh intake
- Verdict: `Rank 279` / `keep_P1`

## What changed
`L1 imbalance × VWAP-to-mid × spread gate` 这条 microstructure directional alpha 已形成可独立审计的短周期 raw alpha skeleton：信号主体可明确收口为 `L1 order-book imbalance + net taker flow / VWAP 偏移同向共振，并由 spread gate 做 entry veto`，执行壳也明确限定在 Binance perpetual 的秒级数据、`1m/3m` taker-first continuation；因此本轮正式记为 `Rank 279` 并首判 `keep_P1`。

## Why not higher
这条线当前仍停留在论文 + desk-spec transfer 层，尚未完成本项目口径下的 clean-room replication：
1. 还没有在统一分钟聚合、固定持有窗与现实 friction ladder（至少 `4/8/12 bps` round-trip）下证明 `BTC/ETH/SOL` 中至少有一个 after-cost pocket；
2. 论文原始 horizon 是 `3 秒` mid-price move，迁移到 `1m/3m` 甚至 `5m/15m` 仍存在明显 transfer 风险；
3. maker 端已被论文明确提示在 crash / spread widening 条件下可能反噬，因此当前只够支持 `taker-first` skeleton，不够诚实直升 `P2`。

## Result sentence for runtime
`L1 imbalance × VWAP spread direction` 已形成可审计的 microstructure directional raw alpha skeleton，因此本轮正式记为 `Rank 279` 并首判 `keep_P1`；但在完成 `BTC/ETH/SOL` 的 minute-level clean-room replication、统一持有窗与 `4/8/12 bps` friction ladder 前，不诚实直升 `P2`。

## Reader-facing implication
这是条值得保留的一次前排候选，但它更像“先验证能否在 minute-level taker-only continuation 上留下 after-cost pocket”的研究线，而不是已经可以直接 paper launch 的主策略。
