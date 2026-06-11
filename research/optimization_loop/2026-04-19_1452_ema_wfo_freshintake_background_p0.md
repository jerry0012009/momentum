# bot3 自动执行日志：EMA crossover × double-OOS admission fresh intake first verdict

- 时间：2026-04-19 14:52 UTC
- 执行小点：cycle_plan #3
- 对象：`research/quant_digests/2026-04-19_1135_ema-wfo-double-oos-trend-alpha.md`
- 策略名：`EMA crossover × double-OOS admission`
- 结论：`background/P0`

## 本轮只补的最小 blocker

按 cycle_plan 要求，只检查一个最小 blocker：`15m` 低换手 / cost-hurdle 版本是否有机会摆脱裸 taker EMA trend 的成本吞噬，留下可继续 admission 的 unseen-friendly pocket。

读取 digest 自带 artifact：`reports/artifacts/quant_digests/2026-04-19_ema_wfo_summary.csv`。

## 关键证据

- `15m fixed_12_48`：
  - BTC gross `+0.156bps/bar` 但 net `-0.246bps/bar`，turnover `4.83 unit/day`；
  - SOL gross `+0.057bps/bar` 但 net `-0.352bps/bar`，turnover `4.92 unit/day`；
  - ETH/BNB gross 已接近零或为负，net 更弱。
- `15m wfo_7_28` / `wfo_14_10` 没有解决核心问题：
  - 最接近的 `SOL 15m wfo_14_10` 只有 gross `+0.230bps/bar`、net `-0.047bps/bar`，turnover 仍约 `3.33 unit/day`；
  - BTC/ETH/BNB 的 WFO 版本均未形成正 net pocket。
- `5m` 版本虽然 BTC/SOL 固定参数有正 gross，但 turnover 约 `14.7 unit/day`，net 明显为负；WFO 版本也没有稳定转正。

## honesty / execution realism

这条线的好处是 admission discipline：训练窗选参、未见期单次执行，能作为方法论被其他策略复用。但作为独立 fresh intake 的 raw alpha，本轮 blocker 没过：

1. 低换手并没有真正出现，`15m` WFO 的换手仍大多在 `3.2~5.1 unit/day`；
2. 成本门槛后没有正 net，最强 `SOL 15m wfo_14_10` 也只是接近零而非可承接边际；
3. 正 gross 不具备跨资产稳定性，主要集中在 BTC/SOL 少数组合；
4. 若再要求训练窗内 `gross edge > 2 × expected cost`，现有 artifact 不支持留下可直接进入 P1 的单一 pocket。

## verdict

`EMA crossover × double-OOS admission` 的 first verdict：double-OOS / WFO 是有价值的 admission 方法论，但 `15m/5m` EMA crossover raw alpha 在低换手与 cost-hurdle 约束下仍没有摆脱成本吞噬；最强 `SOL 15m wfo_14_10` 也仅为 net 近零且不具备跨资产稳定性，因此本轮不分配 Rank，直接收口 `background/P0`。
