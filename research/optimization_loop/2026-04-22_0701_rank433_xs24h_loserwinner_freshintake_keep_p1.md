# Rank 433 fresh intake — 24h 横截面 loser→winner fade × inverse-vol dollar-neutral sizing

- 时间：2026-04-22 07:01 UTC
- 执行者：bot3
- cycle_plan 小点：1
- 对象：`research/quant_digests/2026-04-22_0622_xs24h-loserwinner-voltarget-shell.md`
- verdict：`keep_P1`
- 新 Rank：`Rank 433`

## 本轮只回答的问题

把 `24h 横截面 loser→winner fade × inverse-vol dollar-neutral sizing` 当作新的 front first verdict，补 1 个最小 decisive blocker：majors8 上 `15m parent / 4h hold` 的 maker-like 正 net 是否在真实 turnover、BTC trend gate 与最小 execution realism 后仍足够独立成立，还是只是低成本假设下的 thin relative-value shell。

## 证据

已读 digest 与现成 artifact：

- `reports/artifacts/quant_digests/2026-04-22_staith_xs_reversal_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-22_staith_xs_reversal_probe_trades.csv`

原始 majors8 结果显示：`BTC/ETH/SOL/BNB/XRP/ADA/DOGE/AVAX`、`15m` parent、`24h` lookback、`4h` hold 下，`713` 次 rebalance 平均 gross 约 `+13.76bps/rebalance`；统一 maker-like full-reset `8.8bps` 后仍约 `+36.8%` total return / `Sharpe≈2.18`，但 `20bps` taker-like 成本下转负，说明它必须被定义成 maker-first / low-turnover relative-value sleeve。

本轮补做最小 honesty 子检查：

1. **真实 turnover / 持仓重叠扣费**：按相邻 rebalance 的 long/short 权重差额扣成本，而不是每次假设全平全开。majors8 平均 turnover ≈ `0.90`（full reset=2），按 `8.8bps` full-reset 等价成本后，平均净边际约 `+9.80bps/rebalance`；月份切片为 `2026-01 +4.37bps`、`2026-02 +5.64bps`、`2026-03 +17.62bps`、`2026-04 +21.64bps`，不是单一月份硬撑。
2. **BTC trend gate / 强趋势缩仓 realism**：用公开 BTCUSDT 15m 近 120d，最小 proxy 设为 `ADX(14)>25` 且 `EMA50` 2h slope 绝对值 `>0.15%` 时 gross exposure 缩到 `25%`，并按缩仓后的持仓变化重算 turnover 成本。强趋势占比约 `33.4%`，平均净边际仍约 `+3.18bps/rebalance`；月份切片为 `2026-01 +0.99bps`、`2026-03 +10.10bps`、`2026-04 +14.44bps`，`2026-02 -4.79bps`，`2025-12` 起始残窗为负。
3. **非单一 symbol 暴露**：majors8 全部币种都反复进入 long/short 侧；long 次数分布大致为 `BTC 44 / ETH 80 / SOL 107 / BNB 86 / XRP 79 / ADA 119 / DOGE 110 / AVAX 88`，short 次数为 `BTC 71 / ETH 89 / SOL 86 / BNB 136 / XRP 64 / ADA 70 / DOGE 97 / AVAX 100`，不是单一币 pocket。

## 结论

`Rank 433 / 24h loser→winner majors8 RV fade` 值得保留为 `P1 / Surviving candidate`：在真实持仓重叠扣费与最小 BTC 强趋势缩仓后，majors8 仍留下跨多个月份、跨多个 symbol 的 after-cost 正边际；但它的边际对 taker 化高度敏感，因此下一步唯一 survivor blocker 必须收敛到 `maker-first child execution + turnover/gate 后的净 edge 是否仍可复制`，不能泛化成 broad alt basket 均值回复研究。

## runtime 写回

- `Fresh intake slot`：分配 `Rank 433`，first verdict `keep_P1`
- `Surviving candidate slot`：切到 `Rank 433`，`followup_budget_remaining=1`
- `cycle_plan[1]`：`done`
