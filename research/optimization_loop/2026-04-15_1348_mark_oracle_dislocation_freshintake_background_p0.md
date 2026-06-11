# Rank intake execution log — mark-vs-oracle percentile dislocation fade（fresh intake）

- Time: 2026-04-15 13:48 UTC
- Executor: bot3
- Cycle item: `cycle_plan #3`（first pending）
- Target: `research/quant_digests/2026-04-15_1128_mark-oracle-percentile-dislocation-fade-alpha.md`

## What was executed
按小点要求对该 fresh intake 做 first-verdict 的最小可执行验证（统一 `t+2 + 4/6/8bps`）：
- 数据：Binance USDⓈ-M `BTCUSDT/ETHUSDT` 近 14d `1m` 的 `markPriceKlines + indexPriceKlines(pair)`
- 信号：`abs(mark-index premium_bps) >= rolling q95(lookback=100)`，并做最小底线 `>=5bps`
- 执行 realism / honesty：
  1) 统一 `t+2` 入场（避免同 bar 观测成交 lookahead）
  2) 固定 `H2` 持有（从 `t+2` 到 `t+4`）
  3) 成本统一扣减 `4/6/8bps`
  4) 按 Asia/EU/US 时段拆分检查跨交易时段稳定性
- 产物：
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-15_mark_oracle_dislocation_t2_cost_probe.json`
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-15_mark_oracle_dislocation_t2_cost_probe_summary.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/quant_digests/2026-04-15_mark_oracle_dislocation_t2_cost_probe_trades.csv`

## Key evidence
- 总事件数：`2207`
- 总体 `t+2,H2`：
  - gross mean: `+0.092 bps`
  - net4: `-3.908 bps`
  - net6: `-5.908 bps`
  - net8: `-7.908 bps`
- 分资产（all sessions）：
  - BTC: gross `+0.133` → net6 `-5.867 bps`
  - ETH: gross `+0.048` → net6 `-5.952 bps`
- 跨时段稳定性（`net6`）
  - BTC: Asia `-6.497` / EU `-5.883` / US `-5.158`
  - ETH: Asia `-6.628` / EU `-5.453` / US `-5.794`

## Verdict (first verdict)
该 mark-vs-oracle percentile dislocation fade 在本轮统一执行口径下仅有接近 0 的毛边、费后全负，且负值在 Asia/EU/US 均存在；最小 honesty 子检查（`t+2` 防同 bar 泄漏）后未见可使结论翻转的单一 decisive blocker，因此本轮收口为：

**`background/P0`（不进入 `keep_P1`，不分配 Rank）。**

## One-line result for runtime
`mark-vs-oracle percentile dislocation fade` 在 `t+2 + 4/6/8bps` 口径下总体与分时段费后均为负（overall `net4/net6/net8 = -3.91/-5.91/-7.91 bps`），fresh intake first verdict 收口为 `background/P0`。