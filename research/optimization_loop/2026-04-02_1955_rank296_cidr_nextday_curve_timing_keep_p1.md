# Rank 296 / CIDR next-day intraday curve timing — intake keep_P1

- Time: 2026-04-02 19:55 UTC
- Target: `research/quant_digests/2026-04-02_1929_cidr-intraday-curve-timing-alpha.md`
- Step type: fresh intake first verdict
- Verdict: `keep_P1`
- Assigned rank: `296`

## What changed
`predict-next-day intraday curve × buy forecasted low / sell post-low high` 可以作为一条新的前排对象保留到 survivor：它和旧 `Rank 187` 的 same-day `partial-day path-shape -> remainder swing` 不同，当前主语是 **在日初之前就预测“次日整条 BTC 日内路径”，再据预测低点/后续高点做单日 long-only timing trade，并用 serial-dependence 作为开仓 gate**。

## Why this clears the intake bar
1. **对象边界够具体。** digest 已把对象收口成单一壳：`BTCUSDT` / 次日整条 CIDR 曲线预测 / `u_min` 买入 / `u_max` 后卖出 / 不隔夜 / serial-correlation gate。
2. **和现有前排家族不只是换名。** `Rank 201` 是固定 UTC 时钟 pocket，核心 edge 来自稳定时段；这条线则要求每天滚动预测完整路径，再从预测曲线里读低点与高点时间，主语是“路径预测”，不是固定钟点季节性。`Rank 187` 则是先观察同一天前 `8h` 路径后再交易余下时段；本对象是开盘前决定次日整天的 timing 计划，观察时点与可交易壳都不同。
3. **最小 clean-room 路径已经写清。** digest 给了 `15m` public-data portability probe、`182d` 滚动训练、PCA/AR(1)+serial-dependence gate、`2/4/6/8 bps` 成本敏感性，以及后续 `15m discovery + 5m/3m execution refine` 的明确实验骨架，因此不是只有论文概念、没有 desk 可执行路径。
4. **有诚实但未死的成本后生命迹象。** 当前 `15m` probe 在不 gating 时 gross 已偏薄，但 gated 版本在 `4~6 bps` 下仍保留正 Sharpe 迹象，足以支持 `keep_P1` 而不是直接判死。

## Why this is not a P2 promotion yet
- 当前公开证据仍主要集中在 **单币 BTC + 单一 recent sample + 低频 gated 交易日很少**，跨时间稳定性远未够 admission。
- 成本后 edge 仍脆弱，尤其 `8 bps` 已接近归零；是否能靠 `5m/3m` execution refine 真正救回净值，还没有 desk 可复核结果。
- 当前只是证明“路径预测型 timing 壳值得活下来”，还没有证明它比现有 clock/curve 家族更适合直接升 `P2`。

## Exact object to keep
**Rank 296 = `BTC next-day CIDR curve timing`: before the UTC day starts, forecast the next day intraday BTC return curve, buy near the forecasted intraday low, exit near the subsequent forecasted high, stay flat overnight, and only activate on serial-dependence days.**

## System effect
- 当前 fresh intake 正式收口为 `Rank 296`，verdict = `keep_P1`。
- `Rank 296` 进入 `Surviving candidate slot` 并占用其唯一一次 cheap decisive follow-up 预算。
- `Rank 295` 已在 background，不再占用 survivor；因此前排对象切换到新的 `Rank 296`。

## Result sentence
`Rank 296` 首轮 intake 完成：`BTC next-day CIDR curve timing` 与现有 fixed-clock / same-day path-shape 家族可区分，且已具备可复核的 low-cost gated timing clean-room 路径，因此记为 `keep_P1` 并进入 `Surviving candidate slot`。
