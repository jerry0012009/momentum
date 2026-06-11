# Rank 320 — Wilder RSI breakout × EMA200/ADX/volume allow × fast RSI-45 exit first verdict：keep_P1

- Time: 2026-04-04 01:01 UTC
- Target: `research/quant_digests/2026-04-03_2141_wilder-rsi-fast-exit-trend-shell-alpha.md`
- Action type: fresh intake first verdict
- Verdict: `keep_P1`
- New formal rank assigned: `Rank 320`

## 结论
`Wilder RSI breakout × EMA200/ADX/volume allow × fast RSI-45 exit` 已足够作为一条清楚的 short-cycle single-asset trend raw alpha 母板进入 `P1`，因为它不只是 4h walk-forward 包装，而是已经具备完整可复现的 `entry / allow / exit / sizing / cost` 壳；同时，本轮证据也表明它当前更像需要先做 `asset / timeframe admission` 的单资产趋势母板，而不是已经证明可跨资产直接部署的 universal strategy，因此本轮先保留为 `P1 survivor`，只值得再做一次最小 decisive follow-up。

## 为什么不是 background/P0
1. **base alpha 清楚**：主语不是“验证框架”，而是 `RSI breakout continuation`。
2. **策略壳完整**：已有 `EMA200 + ADX + volume` 准入、`ATR trail + RSI exit` 出场、以及 risk/cost 口径。
3. **短周期最小便携性已给出可行路径**：digest 内已明确展示，在 `5m/15m` 上把 exit 提快到 `RSI-45` 后，BTC/ETH/SOL 至少存在可复现的 post-cost proxy 正收益路径。
4. **当前不足是可迁移性，不是主语缺失**：问题在于它更像 `asset-specific admission` 母板，而不是说明 alpha 本体不存在。

## 为什么先停在 P1，而不是直接升 P2
- 当前最强证据仍是 `BTC/ETH/SOL` 上的最小 portability probe，而不是系统性的 cross-asset / time-stability / parameter-stability admission。
- `5m` 与 `15m` 的较优参数并不完全一致，说明它更像要先回答“哪些币、哪些 timeframe 诚实可用”，而不是已经证明可以作为统一 desk 壳直接推进。
- 因此更合规的下一步不是继续重复 repo 转述，而是做 **一次唯一的 survivor follow-up**：确认它到底存在清楚的 `asset-admission` 路径，还是最终只适合作为共享 fast-exit / trend-allow 组件。

## 本轮写回 runtime 的系统认知变化
- 该对象获得正式 durable identity：`Rank 320`。
- 该对象从 fresh intake first verdict 收口到 `keep_P1`。
- 该对象占用当前唯一 `Surviving candidate slot`，等待一次最小 decisive follow-up。

## Reader-facing一句话
`Rank 320` 不是一份只能停留在 4h walk-forward 的 RSI 报告；它已经足够证明自己是一条可继续追踪的 `short-cycle trend continuation` 母板，但现阶段更像需要先做 `asset / timeframe admission` 的单资产趋势候选，因此先进入 `P1 survivor`。
