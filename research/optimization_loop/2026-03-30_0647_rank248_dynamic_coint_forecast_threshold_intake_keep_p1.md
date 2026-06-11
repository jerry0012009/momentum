# Rank 248 / dynamic-coint spread forecast × percentile trigger × PIW gate：fresh intake keep_P1

- 时间：2026-03-30 06:47 UTC
- 对象：`research/quant_digests/2026-03-30_0633_dynamic-coint-forecast-threshold-pairs-alpha.md`
- 轮次类型：bot3 auto optimization
- 结论：`keep_P1`
- Rank：`248`

## 这轮做了什么
按当前 `cycle_plan` 执行第一条 `fresh intake`，只回答这篇 2026 Frontiers pairs 论文转出来的对象，是否已经形成一个边界清楚、值得进入前排的独立 raw alpha 候选。

## 本轮判断
结论不是 `promote_P2`，也不是直接回 `background/P0`，而是 **`keep_P1`**。

原因有三点：
1. **它不是 generic pairs / plain z-score 的换壳。** 这条对象的最小独立主语已经清楚：`dynamic cointegration pair selection + forecasted spread score percentile trigger + prediction-interval-width uncertainty gate`。和库里已有的 `dynamic cointegration spread convergence`、`fixed threshold pairs`、`threshold map`、`cointegration sizing` 相比，它新增的不是又一个 spread 定义，而是 **forecast timing layer + uncertainty-width gating** 这两个可以单独证伪的层。
2. **完整策略骨架已经够清楚。** 当前 digest 已经把 pair universe（先从 majors pair 起步）、主时钟（`15m` 主信号，`5m` 执行细化）、forecast target（`next 1~4 bars standardized spread score`）、entry/exit（forecast percentile trigger / 回归中性带 / `4~8 bars` max hold）、PIW 角色（size/veto）、以及成本口径（单边 `2/4/6 bps`，先按 taker）写全；它不是只有论文 headline，没有 desk 化 spec 的模糊想法。
3. **但首轮证据还不够直接升 `P2`。** 现在拿到的主要还是论文结构证据与可转译 spec，尚未在同一 formation/trading split、同一 after-cost 口径下，正面对照 `forecast-score trigger` 是否真的优于 `plain z-score threshold`，也还没证明 `PIW gate` 是否留下独立净增益。也就是说，当前值得保留的是一个新的、结构完整的候选，不是已经过 admission 的可 paper-trade 对象。

## 会改变系统认知的话
`Rank 248 / dynamic-coint spread forecast × percentile trigger × PIW gate` 不是旧 pairs/z-score 家族的简单重命名，而是一个边界清楚的 `timing + uncertainty gating` 型 raw alpha skeleton；但在还没完成 `forecast-score vs plain z-score` 与 `PIW gate` 的同口径增益对照前，证据只够 `keep_P1`，不够直接升 `P2`。

## 唯一合法下一步（survivor）
若后续给它 survivor 唯一 follow-up，应该只做一件事：
- 在同一批 liquid majors pair、同一 rolling formation/trading split、同一 after-cost 假设下，正面对照：
  1. `plain current z-score threshold`
  2. `forecast-score percentile trigger`
  3. `forecast-score percentile trigger + PIW width veto/sizing`
- 目标不是继续讨论深度学习模型名，而是直接回答：**forecast timing 与 PIW uncertainty gate 是否带来独立净增益，还是只是把普通 spread MR 包装得更复杂。**

若这一步没有明确增益，这条线就应按 `keep_P1 后转 background` 收口，而不是继续在 `LSTM / ensemble / hyperparameter` 细节上拖长。
