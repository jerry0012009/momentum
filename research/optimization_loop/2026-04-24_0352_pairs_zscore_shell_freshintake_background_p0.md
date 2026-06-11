# Engle-Granger admission × spread z-score fade pairs shell — fresh intake first verdict（background/P0）

- 时间：2026-04-24 03:52 UTC
- 对象：`research/quant_digests/2026-04-23_2359_github-pairs-zscore-shell-portability.md`
- 动作：fresh intake first verdict
- 结论：`background/P0`

## 本轮只回答一个最小 decisive blocker
这条 `Engle-Granger admission × spread z-score fade` pairs shell，是否留下了一个**相对已 live `Rank 424 / Rank 431` 仍具独立新增价值的 after-cost pairs pocket**，还是它的新增价值只剩 pairs shell / admission / 成本现实提示？

## 最小证据
1. digest 自带 recent Binance USDⓈ-M `15m/5m` portability probe，8 个 liquid majors 下的 repo 风格 z-score fade 结果在 `6bps` taker proxy 口径整体没过线：
   - `ADA-DOGE 15m`：`total return ≈ -5.0%`，`Sharpe ≈ -5.74`
   - `XRP-LINK 5m`：`total return ≈ -0.7%`，`Sharpe ≈ -3.22`
   - `ETH-SOL 15m`：`total return ≈ -9.6%`，`Sharpe ≈ -7.69`
   说明这次 repo 最清楚地留下的是「完整策略壳」，不是 recent taker after-cost edge。
2. 这条线的 alpha 主语与当前 runtime 已 live 的 pairs family 高度重合：
   - `Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade`
   - `Rank 431 / cointegration maker-first + hard time-stop pairs`
   前者已经把 `cointegration/pair admission + spread fade` 推到 live；后者已经把 `maker-first + time-stop` 这一层 execution realism 推到 live。当前新 repo 没拿出一个相对它们更强、或不同 pair 池下可独立排队的 after-cost pocket。
3. 当前 digest 自己给出的最诚实定位也是：`pairs shell for further refinement`。这说明它更像 pair-MR 家族可吸收的 `admission -> spread -> entry/exit/stop/cost` 完整模板，而不是新的 queue-facing raw alpha 主语。

## 为什么直接收口 background/P0
- **distinctness 不成立**：和 `Rank 424 / 431` 的 live pairs family 重合度过高，没有形成新的独立前排对象。
- **after-cost pocket 不成立**：recent public probe 在 taker 成本下整体偏弱/为负，没有拿出非单 pair、非单窗口 lucky-run 之外的净边际。
- **新增价值退化为策略壳提示**：它最值得保留的是可复用的 repo 结构与 pair-trading 最小闭环，而不是新的 front-slot alpha。

## 本轮结果句
`Engle-Granger admission × spread z-score fade` pairs shell 的 fresh intake first verdict 已诚实收口 `background/P0`：recent Binance `15m/5m` portability probe 没有证明非单 pair、非单窗口的 taker after-cost pocket，而且其 alpha 主语与已 live `Rank 424 / 431` 的 pairs family 高度重合，新增价值主要退化为 `pairs shell / pair admission / cost-realism` 提示，而不是新的前排 raw alpha。
