# Rank 357 — candlestick pattern shortlist × next-hour drift：fresh intake first verdict = keep_P1

- 时间：2026-04-07 22:03 UTC
- 对象：`research/quant_digests/2026-04-07_2117_candlestick-shorthorizon-pattern-alpha.md`
- 轮次角色：bot3 fresh intake first verdict
- 结论：`keep_P1`
- 正式 Rank：`357`

## 本轮判定
`pattern-shortlist × next-hour drift` 已足够构成**独立于既有 breakout / trend-shell / event overlay 家族**的新 raw-alpha intake，故本轮把该对象从 fresh intake 首判为 `keep_P1`，并赋予正式身份 `Rank 357`。

## 为什么不是旧 breakout / candlestick 壳的重写
1. 这篇 intake 的主语不是“可程序化 K 线结构”或“breakout confirmation”，而是**少数 pattern 本身就是下一小时 drift 的条件标签器**。
2. 文档已经把候选压到一个很窄的 `paper shortlist`：
   - `Bullish/Bearish Harami`
   - `Bullish/Bearish Hikkake`
   - `Three White Soldiers`
   - `Three Black Crows`
3. 最小执行壳也已经具体：
   - `15m 持有 4 bar ≈ 1h`
   - `5m 持有 12 bar ≈ 1h`
   - `下一根开盘入场`
   - 初版成本口径 `4 bps fee + 1 bp slippage` 每边
4. 它对应的是**单资产 raw directional drift**，而不是把 pattern 当作 breakout / retest / overlay 的附属过滤器。

## 为什么不是直接 background / P0
- 这不是泛泛“蜡烛图大全”摘要；它已经明确给出：
  - 有效名单
  - 预测窗口（next hour）
  - 迁移方式（15m/5m）
  - 最小 A/B（裸 pattern vs pattern + high-volume/high-vol gate）
- 因而它已满足 first verdict 的最低要求：**独立主语 + 最小实验口径 + 与旧家族的职责边界清楚**。

## 当前仍未完成的部分
- 还没做 clean-room replication；
- 高频压缩到 `5m` 后是否仍有 after-cost edge 未知；
- pattern 识别阈值（TA-Lib vs 自写规则）仍需 survivor follow-up 收口。

## runtime 影响
- `Fresh intake slot`：本轮首判完成，最新结论更新为 `Rank 357 ... keep_P1`
- `Surviving candidate slot`：由 `Rank 357` 占据，并获得仅一次最小 decisive follow-up 预算
- `Background pool`：不变

## 一句话 result
`Rank 357：pattern-shortlist × next-hour drift 已压清为独立单资产 raw alpha intake，fresh verdict = keep_P1，并进入 surviving candidate slot。`
