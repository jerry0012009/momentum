# bot3 auto：cross-chain negative-spillover RV alpha fresh intake first verdict

- 时间：2026-04-20 11:53 UTC
- 执行小点：cycle_plan item 2
- 对象：`research/quant_digests/2026-04-19_1602_crosschain-negative-spillover-rv-alpha.md`
- verdict：`background/P0`

## 本轮只补的最小 blocker

按 cycle plan，只回答一件事：`cross-chain negative-spillover relative-value alpha` 在跨链冲击后做 laggard/follower 反应，若加入 `t+2` 延迟确认、双腿/跨 venue 成本与可交易窗口 realism，是否仍有可复制 after-cost pocket。

## 复核输入

使用 digest 已落地 artifact：

- `reports/artifacts/quant_digests/2026-04-19_crosschain_negative_spillover_15m_events.csv`
- `reports/artifacts/quant_digests/2026-04-19_crosschain_negative_spillover_15m_summary.csv`
- `reports/artifacts/quant_digests/2026-04-19_crosschain_negative_spillover_15m_by_leader.csv`
- `reports/artifacts/quant_digests/2026-04-19_crosschain_spillover_summary.csv`

原始 digest 的 strongest 口径：

- `15m` strongest leader shock，`n=871`。
- `long leader / short weakest rival` next `1h` gross ≈ `+10.88bps`，但这是双腿交易；按最小 `8bps/leg` 成本，成本口径至少约 `16bps`。
- `short weakest rival` next `2h` gross ≈ `+10.77bps`，看似可过单腿 `8bps`，但不是跨链 RV 双腿实现。
- `EW4 rivals short` next `2h` gross ≈ `+8.22bps`，几乎贴着单腿 `8bps` 成本线。
- `5m` child version 不支持 rival weakness：`rivals_short_alpha` 在 hold12/hold24 约 `-0.44bps / +0.23bps` gross。

## 最小 honesty 结果

我把现成 `15m` event artifact 压到统一成本与稳定性口径：

| 口径 | gross | cost assumption | after-cost mean | 结论 |
|---|---:|---:|---:|---|
| `long leader / short weakest rival`, 1h | `+10.88bps` | `16bps` 双腿 | `-5.12bps` | 双腿 RV 费后转负 |
| `long leader / short weakest rival`, 2h | `+6.02bps` | `16bps` 双腿 | `-9.98bps` | 双腿 RV 更弱 |
| `EW4 rivals short`, 2h | `+8.22bps` | `8bps` 单腿近似 | `+0.22bps` | 只剩成本线附近薄边际 |
| `short weakest rival`, 2h | `+10.77bps` | `8bps` 单腿近似 | `+2.77bps` | 仍为单腿 short，且稳定性不足 |

`short weakest rival` 的单腿正 net 不能直接升级为跨链 RV alpha，原因是稳定性没有闭合：

- 月份切片：`2026-01 +5.63bps`、`2026-02 +15.16bps`、`2026-03 -1.61bps`、`2026-04 -6.39bps`（均为 `8bps` 后）。最近两个月没有持续正边际。
- leader 切片：`ARBUSDT -5.60bps`、`AVAXUSDT -3.21bps`、`BNBUSDT +6.63bps`、`ETHUSDT +14.97bps`、`SOLUSDT +4.50bps`。正边际主要靠 `ETH/BNB` leader regime；`ARB/AVAX` 明显不成立。
- `EW4 rivals short` 虽避免 weakest 选择偏差，但 `8bps` 后仅 `+0.22bps`，且 `2026-04` 为 `-11.41bps`。
- 真正符合“relative-value / cross-chain”语义的双腿版本在 `16bps` 成本下已经转负；若再加入 `t+2` 延迟确认、跨 venue legging/slippage 与事件重叠去重，边际只会进一步恶化。

## verdict

`cross-chain negative-spillover relative-value alpha` 的论文叙事和 raw gross signal 有研究价值，但当前最小可复核证据没有保住可独立承接的 after-cost front-slot：双腿 RV 费后为负，单腿 weakest-rival short 虽有薄正但最近月份转负且 leader 切片集中，`5m` child execution 也不能补强。因此本轮 fresh intake first verdict 直接收口为 `background/P0`，不分配 Rank、不进入 survivor。

## runtime 写回

- Fresh intake slot：保持 `none`，latest_result 更新为本 verdict。
- Background pool：追加本对象为 latest parked。
- cycle_plan item 2：`status=done`，`result` 写成一句可改变系统认知的话。
