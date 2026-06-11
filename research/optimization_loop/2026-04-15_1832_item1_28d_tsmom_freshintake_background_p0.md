# bot3 optimization loop log — 2026-04-15 18:32 UTC

## 执行小点
- cycle_plan item 1
- target: `research/quant_digests/2026-04-15_1758_28d-market-tsmom-longonly-alpha.md`
- action: fresh intake first-verdict（统一 `t+2 + 4/6/8bps` 成本口径 + 最小 execution realism 检查）

## 结果摘要（会改变系统认知）
`28d market TSMOM long-only` 在本轮统一口径下未通过 first verdict：虽然整体均值为正，但 `US` 分时段在 `4/6/8bps` 下均为负，未满足“Asia/EU/US 同向为正”的前排门槛，因此本轮收口 `background/P0`（不进入 survivor，不分配 Rank）。

## 关键证据
复核产物：
- `reports/artifacts/quant_digests/2026-04-15_28d_market_tsmom_longonly_probe_summary.json`
- `reports/artifacts/quant_digests/2026-04-15_28d_market_tsmom_longonly_probe_events.csv`

口径：`BTCUSDT perp 1h`，信号 `28d(672h)` 收益历史分位 `>=66.7%`，`t+2` 入场、持有 `5d(120h)`、long-only，非重叠持仓。

按 UTC 分时段（Asia=00-07, EU=08-15, US=16-23）统计净收益均值（bps）：

| 成本口径 | Asia | EU | US | 全体均值 | 事件数 |
|---|---:|---:|---:|---:|---:|
| net4bps | +146.84 | +259.06 | -64.37 | +100.39 | 79 |
| net6bps | +144.84 | +257.06 | -66.37 | +98.39 | 79 |
| net8bps | +142.84 | +255.06 | -68.37 | +96.39 | 79 |

判定：不满足 `Asia/EU/US` 同向为正，故 fresh intake 不保留到 `P1`。

## 最小 honesty / execution realism 子检查
- **无前视检查**：分位计算使用 running history（每个时点只用历史 `ret28` 样本，先算 percentile 再把当前值写入历史容器），未使用未来信息。
- **执行可实现性（最小）**：
  - 年化换手频率约 `24.03 trades/year`；
  - 持仓占比约 `32.89%`；
  - 入场小时 `quote_volume` 的 `p10` 约 `$227.1M`（`1%` 参与度容量代理约 `$2.27M` notional）。
- 结论：未见能推翻本轮 verdict 的 execution-fatal blocker；主要否决因子是分时段一致性不达标（US 持续负）。

## 本轮执行结论
- verdict: `background/P0`
- rank_assignment: `none`（未达到 `keep_P1`）
- survivor: `not eligible`
- status: `done`
