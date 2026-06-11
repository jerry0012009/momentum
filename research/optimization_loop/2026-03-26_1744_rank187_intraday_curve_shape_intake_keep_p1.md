# Rank 187 / intraday curve shape -> remainder-of-day swing / intake keep_P1

- Time: 2026-03-26 17:44 UTC
- Target: `research/quant_digests/2026-03-26_1633_intraday-curve-shape-remainder-swing.md`
- Step type: fresh intake first verdict
- Verdict: `keep_P1`
- Assigned rank: `187`

## What changed
`partial-day intraday curve shape -> remainder-of-day swing` 值得保留进 survivor，但当前只保留一条足够具体、已被现有证据坐实的 exact pocket：**`BTCUSDT 15m` 下，先观察前 `8h`（`32` 根 `15m` bars）路径形状，再按 `60d lookback + k=3` 最近邻路径预测余下时段，并在预测 future max timing 平仓的 late-session long swing**。

## Why this clears the intake bar
1. 这不是泛泛的“FPCA/path-shape 家族”，而是一个已经在 digest 里被 desk 化成 entry/exit 的单一 pocket。
2. 当前最强 pocket 有明确、成本后仍为正的最小证据：
   - `obs=32 bars (=8h), k=3`
   - `18` 笔交易
   - gross `avg trade +0.463%`, gross Sharpe `3.25`
   - `6bps` round-trip 后 `avg trade +0.403%`, Sharpe `2.83`
3. 同一 digest 也同时给出了诚实的边界：
   - `4h` 观察窗口明显变薄；
   - `6h, k=5` 已接近不成立；
   - 当前样本仍短、trade count 低、edge 更像 late-session pocket 而非全天候主策略。

## Why this is not a P2 promotion yet
- 证据目前仍集中在 `BTC`、短窗口、少交易次数；
- 参数平原不够厚，说明还只是 pocket，不是广义稳健 family；
- 还没做最关键的下一步 cheap follow-up：把这条 pocket 和更贴近论文的替代实现/exit 对照做最小确认，先分清 edge 是来自 path-state 本身，还是来自当前 kNN + predicted-max 的偶然组合。

## Exact object to keep
**Rank 187 = `BTCUSDT 15m late-session path-shape swing`: observe first `8h` intraday cumulative-return shape, use `60d` lookback + `k=3` nearest-neighbor remainder-path forecast, go long only when the implied remainder path still points to a higher future max, exit at predicted future max timing.**

## System effect
- Fresh intake 不再是抽象的 intraday-curve/FPCA 主题，而是正式收口为 `Rank 187`。
- 该对象进入 `Surviving candidate slot`，并获得唯一一次 cheap decisive follow-up 预算。
- 下一步如果继续，必须围绕这个 exact pocket，而不是泛化回整套 path-shape/curve forecasting 家族。
