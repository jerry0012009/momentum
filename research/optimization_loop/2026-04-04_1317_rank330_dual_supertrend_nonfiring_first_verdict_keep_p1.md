# Rank 330 — dual SuperTrend non-firing alpha first verdict: keep P1, not P2

- Time: 2026-04-04 13:17 UTC
- Target: `research/quant_digests/2026-04-04_1050_dual-supertrend-nonfiring-alpha.md`
- Action type: fresh intake first verdict
- Verdict: `keep_P1`
- Assigned rank: `Rank 330`

## What changed system truth

`dual SuperTrend flip × EMA50 × volume gate` 这条对象虽然当前 repo 实现几乎不触发、不能拿 README 高 Sharpe 当结论，但 base alpha、entry/exit/sizing/cost 壳都已经明确，而且失败点被 source-audit 收敛到单一可执行 blocker：`canonical SuperTrend spec / firing density` 还没对齐；因此它应作为 `P1 survivor` 保留一次便宜诚实 follow-up，而不是直接当成已证伪的 `P0` 丢回背景池。

## Why this is not P2 yet

它离 `P2 admission` 还差关键一步：

1. repo 简介 / README / 代码三套口径不一致；
2. `ADX`、`1h bias`、`min_edge` 等 claim 没有落到实际 entry；
3. recent 90d 的 `BTC/ETH/SOL/BNB 15m` portable probe 是 `0 trades`；
4. 当前最需要回答的不是收益，而是 repo SuperTrend 实现是否偏离 canonical 版本、导致 flip/firing density 近乎冻结。

这说明它现在更像“待修正的趋势 raw alpha 壳”，还不是可直接 admission 的 desk experiment。

## Why this still survives as P1

它没有被直接打成 `P0`，因为：

1. **alpha 定义清楚**：快慢双 SuperTrend 同向、EMA50 同侧、放量确认后追 `15m` 趋势延续；
2. **策略部件完整**：entry / exit / sizing / cost 都已成型；
3. **失败方式具体**：不是泛泛地“效果不好”，而是 source-audit 能明确落到 `canonical spec / flip density` 这个单一前置问题；
4. **后续便宜检查明确**：只需要做一次 canonical 对账，就能决定是升 `P2` 还是收口回背景池。

## Single legal survivor follow-up

下一步唯一合法 follow-up 应该是：

- 在 `BTCUSDT 15m recent 90d` 上，把 repo 当前 SuperTrend 实现与 canonical 版本逐 bar 对账；
- 直接回答 `flip timestamps / direction segments / firing density` 是否恢复到正常趋势策略应有的水平；
- 若 canonical 化后仍基本不触发，则诚实收口回 `background/P0`；若恢复出可验证 signal density，再讨论是否进入 `P2`。

## Result sentence

`Rank 330`：fresh intake first verdict 完成，这条 `dual SuperTrend flip × EMA50 × volume gate` 虽然当前实现几乎不触发，但 raw alpha 定义和完整策略骨架都已明确，且 blocker 已收敛到单一的 `canonical SuperTrend / firing density` 对账问题，因此进入 `keep_P1` survivor，暂不升 `P2`。
