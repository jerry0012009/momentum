# Rank 382 survivor follow-up（fill-adjusted capacity realism）→ promote_P2

- 时间：2026-04-11 15:56 UTC
- 对象：`Rank 382 / liquidity-volatility × illiquidity-level XS alpha`
- 轮次动作：cycle_plan #1（survivor 唯一 follow-up）
- 输入证据：
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/liquidity_volatility_illiqlevel_probe_summary_2026-04-11.csv`
  - `/root/clawd/jerry/momentum/reports/artifacts/literature/liquidity_volatility_illiqlevel_probe_universe_2026-04-11.txt`
- 新增 artifact：
  - `/root/clawd/jerry/momentum/reports/artifacts/optimization_loop/rank382_filladjusted_capacity_check_2026-04-11.csv`

## 检查方法（最小 honesty 子检查）
针对 `top25_30d_quotevol` 的 24h 窗口基准（gross `+12.44 bps / 1h`），补做 fill-adjusted capacity realism：

1. 从 Binance USDⓈ-M 24h ticker 拉取 top25 成分当前 `quoteVolume`，换算每 15m 成交额；
2. 取成分 `per_15m` 的 25 分位（保守流动性锚）作为可成交容量基线；
3. 对 long/short 各 5 名（共 10 名）做三档参与率压力：`0.10% / 0.25% / 0.50%` of bar ADV；
4. 采用对应 roundtrip 成本压力：`6 / 10 / 14 bps`（fee+impact 合并）重估净边际。

## 结果
- 保守流动性锚：`q25 per_15m ≈ 1.409M USDT`
- 三档结果：
  - `0.10%` 参与率：预计最大组合名义约 `14.1k USDT / 15m`，净边际约 `+6.44 bps / 1h`
  - `0.25%` 参与率：预计最大组合名义约 `35.2k USDT / 15m`，净边际约 `+2.44 bps / 1h`
  - `0.50%` 参与率：预计最大组合名义约 `70.4k USDT / 15m`，净边际约 `-1.56 bps / 1h`

## 结论（改变系统认知）
`Rank 382` 在 fill-adjusted capacity realism 下**仍可执行但容量受限**：当参与率不高于约 `0.25% bar ADV` 时净边际为正，超过 `0.50%` 参与率后转负；因此 survivor follow-up 收口为 `promote_P2`（后续 admission 应把容量上限写成硬约束）。

## 本轮状态写回
- Surviving candidate：`Rank 382` 用尽唯一 follow-up 并完成收口，释放 survivor 槽位。
- Active P2：切换为 `Rank 382`（待执行 P2 admission）。
- cycle_plan #1：`status -> done`。
