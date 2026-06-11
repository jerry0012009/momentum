# Rank 156 / Distance-first crypto pairs with trade-buffer governance surviving follow-up

- Time: 2026-03-25 00:48 UTC
- Slot: Surviving candidate
- Rank: 156
- Target: `Distance-first crypto pairs mean reversion with trade-buffer/cost governance`
- Origin record: `research/optimization_loop/2026-03-24_1659_rank156-distance-first-pairs-intake.md`
- Purpose: 用 survivor 唯一一次 follow-up，回答同一 public-data 口径下 `cost ladder × trade_buffer` 是否足以把成本后为负的结果拉回可生存 pocket。

## Why this was the legal next move
当前 runtime 明确把 Rank 156 留在 `Surviving candidate slot`，且它唯一允许的 follow-up 就是这次 `cost ladder × trade_buffer` 决断。虽然 `cycle_plan` 没有留下新的 pending 条目，但按 fixed policy，这一条 survivor follow-up 仍是当前前排唯一合法未收口动作；因此本轮按 policy 对 stale plan 做合法回退，只执行这一小点，不扩写其他排班。

## What was actually tested
为避免假装完整复刻，我没有捏造不存在的 8 币 5m 全量缓存，而是使用工作区现成的 **同一 public-data 家族、同一 8 币池、同一 distance-first 逻辑的 15m honest proxy** 来回答唯一 blocker：

- 数据：`reports/artifacts/scout_rank77_alt_btc_rs_breadth_15m/universe_cache/*__15m.csv`
- 币池：`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK`
- 时间：`2025-12-01` 到 `2026-03-16`
- 训练 / 执行：3 天 lookback、1 天 forward、每天重选 `k=3` 个 distance 最小 pairs
- 交易规则：`entry_z=2.0`、`exit_z=0.25`、`stop_z=4.0`、`max_hold=16`（对应 15m 的约 4h 持有上限）
- 二维治理网格：
  - cost ladder = `8 / 12 / 16 / 20 bps`
  - trade_buffer = `0 / 2% / 5% / 8%`
- artifact：
  - `reports/artifacts/quant_digests/rank156_cost_buffer_followup_20260325/summary_grid.csv`
  - `reports/artifacts/quant_digests/rank156_cost_buffer_followup_20260325/pairday_grid.csv`
  - `reports/artifacts/quant_digests/rank156_cost_buffer_followup_20260325/summary.json`

## What changed system knowledge
结果不是“buffer 甜点存在，所以值得继续拖”；而是更狠：**即使把频率降到 15m，并把成本降到 8bps round-trip、buffer 放宽到 8%，最佳 pocket 仍然是明显负值。**

网格摘要：

| cost (bps) | buffer | avg daily pnl (bps) | cum pnl (%) | trades |
|---|---:|---:|---:|---:|
| 8 | 0% | -137.82 | -140.57 | 2130 |
| 8 | 2% | -135.35 | -138.06 | 2110 |
| 8 | 5% | -132.42 | -135.07 | 2080 |
| 8 | 8% | -129.74 | -132.34 | 2060 |
| 12 | 5% | -213.99 | -218.27 | 2080 |
| 20 | 5% | -377.12 | -384.67 | 2080 |

关键观察：
1. `trade_buffer` 的确略微减少交易数（`2130 -> 2060`），但改善幅度只有约 `8 bps/day`；
2. 最佳组合 `8bps × 8% buffer` 仍是 `-129.74 bps/day`，完全没接近穿成本线；
3. 连 **gross** 日均收益也只有约 `+31.83 bps/day`，说明问题不是单纯 turnover 治理缺失，而是这套 public-data proxy 下 alpha 本身太薄，根本扛不住现实摩擦。

## Verdict
这次唯一 follow-up 已经把 survivor 问题收口：

`Rank 156 / Distance-first crypto pairs with trade-buffer governance` 在同一 public-data 家族下补完 `cost ladder × trade_buffer` 后，最佳 pocket 仍明显为负，说明成本后失效不是单靠 turnover/buffer 就能修回来的执行问题，而是当前 alpha 本身不过成本线；因此本轮结论应直接收口为 `drop_to_background`，不再继续保留前排 survivor 资源。

## Result sentence
`Rank 156 / Distance-first crypto pairs with trade-buffer governance` 的唯一 survivor follow-up 已完成：即使在更低成本与更高 trade_buffer 的 15m honest proxy 下，最佳 pocket 仍显著为负，因此当前证据更支持“alpha 本身不过成本线”而非“仅缺 turnover 治理”，本轮应直接 `drop_to_background`。
