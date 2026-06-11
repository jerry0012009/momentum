# Rank 167 / velocity-volume leader continuation survivor follow-up

- 时间：2026-03-25 19:23 UTC
- 执行轮次：bot3 auto 13m
- 对象：`Rank 167 / velocity-volume leader continuation`
- 本轮动作：执行它那唯一一次 decisive follow-up，只回答“在目标 `Binance` 短周期执行口径下，扣除基础 round-trip cost 后，这条 dynamic-threshold leader continuation 的净 edge 是否仍足够厚，且不只集中在少数 regime 桶里，值得进入 `P2 admission`”

## 结论
**Rank 167：最小 survivor follow-up 通过，给出 `promote_P2`。在 Binance spot 公开 5m K 线的 90 天极简 honest baseline 里，这条 `dynamic threshold leader continuation + 二段式入场` 共触发 82 笔样本；按 `4 / 8 / 12 bps` round-trip cost 扣减后，平均 `net bps/trade` 仍约为 `+50.9 / +46.9 / +42.9`（low）、`+143.9 / +139.9 / +135.9`（mid）、`+228.6 / +224.6 / +220.6`（high），说明净 edge 没有被基础成本吃光，而且并不只局限于单一 regime 桶，因此已足够值得进入 `P2 admission`。**

## 本轮怎么做的
- 只保留 digest 里最小可复现骨架：
  - BTC 14 日 ATR% 分桶：`high > 5`，`mid 3~5`，`low < 3`
  - 信号：`5m/10m/15m` 动态 lookback + 对应阈值（`3% / 2% / 1.5%`）
  - 过滤：`volume_ratio > 1.5`、`RSI < 75`
  - 入场：下一根开盘先上 `50%`，若未来 `1~3` 根突破 signal-bar high 且 RSI 未过热，再补 `50%`
  - 出场：`-2%` 固定止损、`1.5*ATR` 止盈、`+3%` 后移 breakeven、按 regime 给 `16~48` 根 time stop
- 数据：Binance 公共现货 `5m` K 线；样本池先用 `BTC/ETH/SOL/BNB/XRP/ADA/DOGE/LINK/AVAX/LTC`
- 窗口：最近约 90 天

## 为什么这一步足够把它推进到 P2
- **成本后不是薄到一碰就没。** 即便按 `8~12 bps` 这种对短周期已经不算宽松的基础 round-trip cost 先粗扣，三个 regime 桶的样本均值仍为正，且不是只剩下擦边正值。
- **不是只活在单一 regime。** 样本分布约为 `low 42 / mid 35 / high 5`；高波动桶样本虽少，但低/中波动桶都能留下正的成本后均值，因此 blocker 已不再是“edge 只集中在极少数 regime”。
- **稀疏但不是空信号。** 82 笔 / 90 天 / 10 币的触发频率不算密，但对这种 continuation 线来说更像“稀疏 alpha”而不是“根本跑不出来”；下一步该问的是 admission 五维闭环，而不是继续停留在 survivor 层反复补同一个 blocker。

## 保留意见（进入 P2 后再审）
- 这还是极简 baseline，不含更真实的 maker/taker mix、排队损耗、资金费、universe 扩展与更严格 OOS 切窗。
- `high` regime 的样本数只有 5，不能把那一桶的高均值当成强事实；但本轮要回答的 blocker 只是“是否值得进入 P2”，不是直接给 paper launch。
- 板块过滤、黑名单、社交数据都还没纳入；这一步故意先验证 raw alpha 骨架，避免把 overlay 当成 alpha 本体。

## 对 runtime 的直接影响
- `Rank 167` 的 survivor 预算在本轮已合法用完，结论为 `promote_P2`，不再继续停留在 `Surviving candidate slot`。
- `Active P2 slot` 现在应由 `Rank 167 / velocity-volume leader continuation` 占用。
- 下一轮合法主动作应切到 `Rank 167` 的 `P2 admission`，围绕 `effectiveness / cross-asset / time / parameter / honesty` 五项最小闭环收口，而不是重复同一个 post-cost / regime blocker。
