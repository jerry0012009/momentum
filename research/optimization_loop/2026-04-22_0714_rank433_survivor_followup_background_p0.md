# Rank 433 survivor follow-up — 24h loser→winner majors8 RV fade

- 时间：2026-04-22 07:14 UTC
- 执行者：bot3
- cycle_plan 小点：2
- 对象：`research/quant_digests/2026-04-22_0622_xs24h-loserwinner-voltarget-shell.md`
- verdict：`background/P0`
- Rank：`Rank 433`

## 本轮只回答的问题

把 `Rank 433 / 24h loser→winner majors8 RV fade` 的唯一 survivor blocker 收敛成一句可执行的话：在前一轮已经确认 `15m parent / 4h hold`、真实 turnover 与最小 BTC trend gate 后仍保留 parent-level after-cost 正边际的前提下，这条线在最小 `maker-first child execution` proxy 下还能不能保住独立 edge，还是只剩 low-cost parent shell。

## 本轮最小 honesty / execution realism 检查

只补 1 个最便宜、最能改变结论的 child execution 检查，不扩写第二个 pending 小点：

- universe：`BTC/ETH/SOL/BNB/XRP/ADA/DOGE/AVAX`
- parent signal：沿用前一轮 `15m` 上的 `24h lookback / top-bottom 20% / 4h rebalance`
- child proxy：不再假设 signal bar close 即可进场；改成 **signal 后下一根 `5m` open 入场**，并在 **`4h + 5m` 的下一根 `5m` open** 退出，作为最小延迟成交 proxy
- sizing / turnover：仍按组合 long-short 等权，并对相邻 rebalance 的持仓变化量扣成本，而不是每次全平全开
- friction：沿用上一轮 maker-like full-reset `8.8bps`，按本轮真实 turnover 比例折算扣费
- trend gate：保留最小 BTC 强趋势缩仓 proxy；在强趋势时把 gross exposure 缩到 `25%`

## 结果

上述最小 child-execution proxy 直接改变结论：

- 样本数：`713` 次 rebalance
- 强趋势缩仓占比：约 `2.38%`
- child-entry 后平均 `gross`：约 `+5.65bps/rebalance`
- 扣掉按 turnover 折算的 maker-like 成本后，平均 `net`：约 **`-3.33bps/rebalance`**
- 累计 `net total return`：约 **`-23.90%`**
- `net win rate`：约 `48.11%`
- 月份切片：`2025-12 -14.19bps`、`2026-01 -7.31bps`、`2026-02 -7.16bps`、`2026-03 +3.54bps`、`2026-04 +1.56bps`

暴露并不是单一 symbol 幻觉——long 侧仍覆盖 `ADA/DOGE/SOL/BNB/XRP/AVAX/ETH/BTC`，short 侧仍覆盖 `BNB/AVAX/BTC/DOGE/SOL/ETH/ADA/XRP`——但 **child execution 一旦从 parent close 的理想成交压成 next-5m open 的最小现实延迟，原先可保留的 parent-level RV edge 就不再覆盖 maker-like 成本**。

## 结论

`Rank 433` 的 survivor 唯一 follow-up 已诚实收口：它没有证明 `majors8 24h loser→winner fade` 在最小 child execution realism 下仍保留独立、可复制的 after-cost edge；当前留下的只是一条 **对理想低成本 parent rebalance 很敏感的 relative-value shell**，还不足以进入 `P2 / pre-paper`。因此本轮按 survivor 预算耗尽直接转入 `background/P0`，不再占用前排。

## runtime 写回

- `Surviving candidate slot`：清空为 `none`
- `cycle_plan[2]`：写成 `done`
- `Background pool`：补记 `Rank 433` survivor follow-up 已诚实收口为 `background/P0`
