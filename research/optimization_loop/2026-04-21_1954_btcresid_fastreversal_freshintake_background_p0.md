# bot3 自动优化日志：BTC 残差化横截面 fast reversal fresh intake

- 时间：2026-04-21 19:54 UTC
- 执行小点：cycle_plan item 2
- target: `research/quant_digests/2026-04-21_1914_btcresid-xs-fastreversal-dailyrebalance-alpha.md`
- verdict: `background/P0`

## 本轮执行
1. 读取 fixed policy 与 runtime state，确认当前第一个合法 pending 小点是 fresh intake：`BTC-residualized cross-sectional fast reversal × daily rebalance`。
2. 读取 digest 与现成摘要 artifact：`reports/artifacts/quant_digests/2026-04-21_btcresid_fastrev_slowmom_probe_summary.csv`。
3. 只补一个最小 decisive blocker：用本地 `60d / 15m` Binance USDⓈ-M perp 缓存，对 BTC 残差化 fast-reversal 的 daily-rebalance basket 与 strongest-only router 做统一 `4bps one-way` 成本、月份/日期贡献检查。

## 关键证据
- digest 43d 摘要里，fast reversal sleeve 为薄正：`gross≈+0.0276bps/bar`、`net≈+0.0203bps/bar`、`net Sharpe≈1.52`、`cum_net≈+0.84%`。
- 但本轮 60d/15m 复核后，daily-rebalance basket 转为费后负：`cum_net≈-4.37%`、`mean_net≈-0.0775bps/bar`、`net Sharpe≈-3.43`。
- strongest-only router 也没有救回来：`cum_net≈-0.35%`、`mean_net≈-0.0061bps/bar`、`net Sharpe≈-0.07`。
- 月份切片不稳：basket `2026-02≈-4.57%`、`2026-03≈-0.71%`、`2026-04≈+0.93%`；正边际只出现在当前 4 月切片，不满足“非单月/非少数贡献支撑”的 first-verdict 门槛。
- symbol gross contribution 也不均衡：`ADA/BNB` 为主要正贡献，`ETH/SOL/DOGE/LINK` 拖累，说明这不是一个已经稳健跨资产迁移的独立 after-cost raw alpha。

## 结论
`BTC-residualized cross-sectional fast reversal × daily rebalance` 的 fresh intake first verdict 已诚实收口：digest 43d 摘要虽有 `net≈+0.0203bps/bar` 的薄正，但本轮用本地 60d/15m perp 缓存做统一 4bps one-way 复核后，daily-rebalance basket `cum_net≈-4.37% / mean_net≈-0.0775bps/bar / Sharpe≈-3.43`，strongest-only router 也 `cum_net≈-0.35% / mean_net≈-0.0061bps/bar`；且月份切片只有 `2026-04` 为正、`2026-02/03` 为负，因此它未通过“统一成本后仍为正且非单月/少数贡献支撑”的 decisive blocker，本轮直接收口 `background/P0`。

## runtime 回写
- `Fresh intake slot.latest_result` 更新为本 verdict，并把当前 fresh intake 前排切到下一条 `Tenkan/Kijun cross`。
- `Background pool.latest_parked` 与 `latest_parked_record` 已追加本次 `background/P0` 记录。
- `cycle_plan` item 2 写入 result 并标记 `done`。
