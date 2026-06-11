# Rank 431 / cointegration maker-first + hard time-stop pairs — P2 admission 首轮 keep_P2

- 时间：2026-04-21 11:48 UTC
- 执行者：bot3
- 对应 cycle_plan 小点：1
- target: `Rank 431 / cointegration maker-first + hard time-stop pairs`

## 本轮只执行的动作
按 `Active P2` 首轮 admission 要求，围绕 `effectiveness / cross-asset / time / parameter` 做最小会改层级的汇总，并补 1 个最小 honesty 子检查：
- 用现成 artifact 的逐笔交易，做最小 `day-concentration` 压力检查，确认“至少两对可持续 pocket”是否仍成立。

## 使用证据
- `reports/artifacts/quant_digests/rank431_survivor_followup_proxy_summary_2026-04-21.csv`
- `reports/artifacts/quant_digests/rank431_survivor_followup_proxy_trades_2026-04-21.csv`

## admission 摘要
### effectiveness（成本后）
- `NEAR-ATOM`：`net_mean_8/12/16 ≈ +60.45/+56.45/+52.45bps`（23 笔）
- `AVAX-SUI`：`net_mean_8/12/16 ≈ +7.94/+3.94/-0.06bps`（24 笔）

### cross-asset
- 入选频次最高 pair 有 3 对（`AVAX-SUI`, `NEAR-ATOM`, `AVAX-ATOM`），但费后稳定正边际主要由 `NEAR-ATOM` 承担。

### time stability
- 对 `AVAX-SUI` 做最小日度集中检查后，`net8` 去掉 top3 贡献日后的剩余样本均值约 `-17.89bps`（17 笔），说明该对近期边际对少数好日子较敏感。
- `NEAR-ATOM` 去掉 top3 贡献日后剩余样本均值仍约 `+22.86bps`（17 笔），稳定性显著更好。

### parameter stability
- `AVAX-SUI` 在 `16bps` 已近零（`-0.06bps`）；`NEAR-ATOM` 在 `8/12/16bps` 仍同向为正。
- 目前“多参数梯度下双对同向稳定”并未闭合。

### honesty / execution realism（本轮唯一子检查）
- 沿用 survivor 阶段 maker-first + timeout-cross 摩擦口径，不新增第二类复杂 realism；只补 day-concentration 检查。
- 结果显示当前可持续性更接近“单 durable pair（NEAR-ATOM）+ 一条脆弱次优对”，尚不足以直接升 `P3`。

## 本轮结论
`keep_P2`（不是 `promote_P3`）。

## 唯一 decisive blocker（收敛）
`cross-pair durability` 尚未闭合：在最小日度集中压力下，第二对（`AVAX-SUI`）费后稳定性退化，当前更像单 durable pair 驱动，而不是“至少两对可持续 pocket”已被确认。

## 一句话结果（写回 state）
`Rank 431` 的 P2 admission 首轮已完成：在现有 rolling admission + maker-first realism 证据上补做最小 day-concentration 检查后，仅 `NEAR-ATOM` 保持跨成本梯度的稳定费后边际，`AVAX-SUI` 在去除少数高贡献日后转弱，因此本轮收口为 `keep_P2`，唯一剩余 blocker 收敛为 `cross-pair durability`。

## 尾部执行状态（非阻断）
- homepage publish：待本轮尾部命令执行。
- 邮件通知：待本轮尾部命令执行。
