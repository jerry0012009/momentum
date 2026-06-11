# bot3 auto：long-crowding Williams %R liquidation fade fresh intake first verdict

- 时间：2026-04-22 15:43 UTC
- 执行小点：cycle_plan #1
- 对象：`research/quant_digests/2026-04-22_1350_longcrowding-williamsr-liqfade-alpha.md`
- 动作：fresh intake first verdict；只补一个最小 decisive blocker：跨资产/跨月份可迁移性 + 成本后厚度。

## 结论

`overbought Williams %R × long-crowding liquidation fade` 本轮直接收口 `background/P0`，不保留 survivor。

原因：原 digest 最强 ETH short-only pocket 在全样本 `6bps` 下看似为正，但最小 honesty 切片显示它没有通过跨资产/跨月份可迁移性门槛：`long_share>62%` 时 `BTC/SOL/XRP` 在 `6bps` 后分别约 `-7.16/-2.72/-3.77bps/trade`，ETH 虽全样本约 `+5.66bps/trade`，但 `2026-03` 约 `+16.31bps/trade`、`2026-04` 转为约 `-7.45bps/trade`；更高 `>70%` 阈值几乎只剩 2026-03 的 ETH 样本（2026-04 仅 1 笔且约 `-100.57bps`）。因此这条线当前更像 ETH/月份局部 crowding-reversal pocket，而不是可独立排队的新 short-cycle raw alpha。

## 最小复核依据

已读取 digest 与现有 artifact：

- `reports/artifacts/quant_digests/liquidity_hawk_probe_20260422/threshold_sweep_summary.csv`
- `reports/artifacts/quant_digests/liquidity_hawk_probe_20260422/ETHUSDT_trades.csv`
- 同目录 `BTCUSDT/SOLUSDT/XRPUSDT_trades.csv`

关键数值（均沿用 artifact 的 `6bps` round-trip net）：

| 条件 | BTC | ETH | SOL | XRP |
|---|---:|---:|---:|---:|
| `long_share>62%` all | -7.16 | +5.66 | -2.72 | -3.77 |
| `long_share>62%` 2026-03 | -14.59 | +16.31 | +16.41 | -0.39 |
| `long_share>62%` 2026-04 | +3.62 | -7.45 | -10.21 | -4.95 |
| `long_share>70%` all | -20.47 | +10.52 | -5.00 | -3.77 |

## runtime 写回

- Fresh intake slot：该对象 first verdict 写成 `background/P0`。
- Background pool：追加本对象 parked 结论与本日志路径。
- cycle_plan #1：`result` 写入本轮改变系统认知的一句话，`status=done`。
