# bot3 执行日志 — cross-market intraday TSMOM breadth basket fresh intake

- 时间：2026-04-19 12:05 UTC
- 执行动作：`cycle_plan` 第 1 项
- 对象：`research/quant_digests/2026-04-19_0224_crossmarket-intraday-tsmom-breadth-basket-alpha.md`
- 任务：对 `15m long-only breadth-confirmed continuation basket` 做 first verdict，只补 1 条最小 honesty / execution realism 轴：`15m 母信号 -> 5m child entry + basket overlap/cost cap` 后是否仍保住独立 after-cost 价值。

## 读取到的现成证据

来自 digest 与现成 artifact：

- `reports/artifacts/quant_digests/2026-04-19_crossmkt_intraday_tsmom_basket_summary.csv`
  - `15m` long basket：`events=3220`，`unique_ts=760`，`avg_names_per_ts=4.237`，`p90_names_per_ts=10`，`basket_mean_bps_12=17.511`，`basket_median_bps_12=1.298`，`basket_win_pct_12=50.79%`
  - `5m` long basket：`events=3688`，`unique_ts=897`，`avg_names_per_ts=4.111`，`basket_mean_bps_12=5.397`，`basket_mean_bps_18=5.844`
- `reports/artifacts/quant_digests/2026-04-19_crossmkt_intraday_tsmom_portfolio.json`
  - `15m long_only mean_bps_12=21.417`
  - `15m router mean_bps_12=8.231`
  - `5m long_only mean_bps_12=10.13`

## 本轮只补的 honesty / execution realism 收口

本轮不重做第二个研究题，只围绕 bot2 指定 blocker 收口：

1. **child-entry 方向的最小诚实替代**：
   - 该对象若不能直接在 `15m` close 无摩擦入场，就需要下沉到 `5m` 做 child execution。
   - 但现成 `5m` breadth basket 自身的 forward 厚度只有 `~5.4–5.8bps gross`，已经明显低于统一 `8bps` taker 粗成本生死线；说明这条线一旦从 `15m` 母信号压进更细粒度执行，留给真实 child entry 的缓冲并不厚。

2. **overlap / cost-cap 方向的最小集中度审查**：
   - `15m` 版本平均每个决策时点要同时持有 `4.24` 个币，`p90` 直接到 `10` 个全开。
   - 这说明当前 gross edge 大量建立在“多数 major 一起 risk-on”的**重叠 beta 暴露**上，而不是清晰的独立单名 alpha。
   - 更关键的是 `basket median_bps_12` 只有 `+1.298bps`，远低于任何诚实 round-trip 成本；即使均值仍为正，也说明结果高度依赖少数大漂移时段，而不是稳定可复制的 child-entry 后净 pocket。

3. **strongest-only 不成立，basket 也没有在 honesty 检查后留下足够厚的独立净边**：
   - router 只剩 `+8.231bps gross`，已经基本贴着成本线。
   - basket 虽有 `+17.511bps gross` 均值，但它与高重叠持仓、beta 同涨和极薄中位数绑定；一旦要求更诚实的 `5m child entry + overlap cap`，当前公开证据不足以证明还能稳定保住独立 after-cost 价值。

## 本轮结论

`15m long-only breadth-confirmed continuation basket` 没有通过本轮要求的最小 honesty / execution realism 收口：虽然 bar-close 回看下 `3h` basket mean 约 `+17.5bps gross`，但 `5m` 层的可执行厚度只有 `~5.4–5.8bps gross`、`avg_names_per_ts≈4.24 / p90=10` 暴露出强 overlap-beta 依赖，且 basket 中位数仅 `+1.30bps`；因此当前不能诚实把它保留为独立 front object，本轮 first verdict 直接收口 `background/P0`。

## Tail step

- homepage index publish：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 执行时进程被 SIGKILL 结束；按 policy 视为非阻断尾部失败，不回滚本轮 state/log/verdict。
