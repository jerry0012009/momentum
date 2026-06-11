# Rank 352 / BTC perp conditional drift fresh intake -> keep P1

- Time: 2026-04-06 11:13 UTC
- Target: `research/quant_digests/2026-04-06_0928_btc-perp-conditional-drift-alpha.md`
- Action: fresh intake first verdict
- Verdict: `keep_P1`
- Rank assigned: `Rank 352`

## Why this survives first intake

这条对象没有被压成“把常见条件动量重新命名”的空壳，原因有三点：

1. **主语足够清楚**：它不是 generic breakout/filter stack，而是单资产 `BTCUSDT perp` 上的 `vol-normalized expected-price slope`，即 `score = μ̂_H / σ̂_H` 驱动的 directional conditional drift。
2. **最小策略骨架已明确**：标的、频率（`5m/15m`）、持有窗口（`H=1/2/3` bars）、阈值进场、time/sign-flip exit、显式 taker/maker cost shell 都已写出，能直接落成 clean-room first test。
3. **它与现有前排对象不重合**：最近前排更偏 pairs / carry / cross-market lag / event continuation；这条是单资产 BTC perp 短周期方向层，既可独立验证，也可作为 continuation/event 策略的 direction prior。

## Why not P2 yet

它现在还不够直接进 `P2`，因为公开材料给的是论文摘要与元数据，不是已经跑出的 desk-grade after-cost transfer。当前还缺一轮便宜但 decisive 的 survivor follow-up，去回答：

- `5m/15m` 下 `score` 分桶对下一到三根收益是否有**单调性**；
- round-trip 成本（先按 taker `2~4bps`）后是否仍有净边；
- edge 是否只存在于极端高波动环境，从而只是 volatility-state 伪装。

## Result sentence for runtime

> `Rank 352 / BTC perp conditional drift` 已完成 fresh intake first verdict：对象把 `vol-normalized expected-price slope -> short-cycle directional drift` 的独立主语与最小可验证策略壳压清，和现有 pairs/carry/event 线不重合；虽尚未完成 after-cost transfer，仍足以保留为 `keep_P1` 并进入 survivor follow-up。

## Next honest follow-up

在 survivor 轮做一次最便宜的 clean-room 检查：

- 数据：`BTCUSDT perp`（必要时并排 `spot/mark/last`）
- Bar：`5m` 主实验，`15m` 稳健性复核
- 信号：`EWMA mean / EWMA vol` 先替代论文 full model zoo
- 输出：score 分桶 monotonicity、top-bottom spread、gross/net PnL、turnover、funding-adjusted PnL

如果这轮不能留下成本后单调性，就应在 survivor 轮直接收口回 `background/P0`，不拖进 `P2`。