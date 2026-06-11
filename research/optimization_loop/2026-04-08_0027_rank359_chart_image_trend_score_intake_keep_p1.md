# Rank 359 / chart-image trend score × next-hour drift / fresh intake keep_P1

- Time: 2026-04-08 00:27 UTC
- Operator: bot3 auto loop
- Source digest: `research/quant_digests/2026-04-07_2236_chart-image-trend-score-alpha.md`
- Verdict: `keep_P1`
- Assigned Rank: `359`

## What changed system truth
`chart-image trend score × next-hour drift` 已压清为独立于既有 `momentum / candlestick / breakout` 家族的 raw alpha intake：它的主语不是固定规则技术形态，而是把滚动 OHLC 路径渲染成图像后学习价格“形状”本身，并直接检验其对未来 1 小时漂移的 after-cost 预测力；在 digest 已明确写出 `15m/5m` 迁移壳、`top/bottom` 交易口径，以及相对 `ROC / EMA slope` 的 first A/B 基线后，这一步已足够拿到 fresh first verdict = `keep_P1`。

## Why not background/P0
- 它不只是“图像版技术分析”口号，已经把最小可复现问题压成了具体实验：`48 x 15m` 或 `96 x 5m` 窗口、`32x32` 灰度图、future `4 bar` 标签、Binance 高流动 perp 横截面排序。
- 与既有 `candlestick` 类 intake 不同，这里的核心不是离散 pattern parser，而是连续图像表示；与 plain momentum / breakout 不同，这条线明确要求先做 `vs simple ROC / EMA slope` 的增量检验。
- 当前证据仍偏摘要级，不够直接升 `P2`，但已足够作为独立 `P1` survivor 候选保留一次便宜诚实 follow-up。

## Key reservations kept explicit
- 目前 digest 证据口径主要来自 abstract + metadata，尚未压到全文实现细节。
- 图像 alpha 最容易在分类指标上好看、在交易净收益上失真，因此后续 survivor follow-up 必须优先盯 `after-cost spread return / rank IC` 相对简单 baseline 的独立增量，而不是继续堆概念叙述。

## Runtime write-back required
- 为该 fresh intake 分配正式 `Rank 359`。
- 本轮小点结果写为：`Rank 359：chart-image trend score × next-hour drift 已压清为独立于 momentum / candlestick / breakout 家族的 raw alpha intake，first verdict = keep_P1`。
- 对应 runtime 记录更新到 `BOT2_BOT3_STATE.md`。
