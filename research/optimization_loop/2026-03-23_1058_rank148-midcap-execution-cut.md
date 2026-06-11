# 2026-03-23 10:58 UTC · Rank 148 / intraday cross-sectional reversal（US 时段）mid-cap tradable universe + execution/capacity overlay

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 本轮路径：`Scout`
- 本轮范围：只做 **1 个主点 + 1 个紧邻子点**

## 0. 顶板判路
- `Paper / 待开启自动运行 = empty`
- 无新的 `Interrupt` 信号
- 按 `Next 3 bot3 runs` 执行 `Run 1 = Rank 148 follow-up`

## 1. 本轮主点
**主点：`Rank 148 / intraday cross-sectional reversal (US session)` 的 decisive next cut**

顶板要求已经写死：
> 下一刀不是再证明“它有概念”，而是直接回答它有没有继续往 `P2` 靠的空间：**切到中盘可交易宇宙，并补 1 个最小 execution / capacity overlay**。

所以本轮只做两件事：
1. 把大币 lower-bound 扩成 **中盘可交易宇宙**；
2. 给出最小执行层：**双边 fee + spread proxy + 容量代理**。

## 2. 实验口径
数据源：`Binance Spot /api/v3/klines`

样本：`2026-01-01 ~ 2026-03-23 10:23 UTC`

宇宙构造：
- 仅保留 `USDT` 现货可交易对；
- 剔除大币 `big20`、稳定币、杠杆币、明显非普通交易对；
- 按最近 `24h quote volume` 排序，并要求有完整样本覆盖；
- 取 `mid-cap top15 quote-volume ex big20`。

本轮宇宙：
- `TAOUSDT, BANANAS31USDT, ZECUSDT, PEPEUSDT, ASTERUSDT, WLFIUSDT, GUNUSDT, FETUSDT, SIGNUSDT, WLDUSDT, TURBOUSDT, DASHUSDT, ENAUSDT, KITEUSDT, GIGGLEUSDT`

策略骨架：
- `15m`
- morning：`13:30-14:00` 信号，`14:15-14:45` 持有
- close：`19:30-20:00` 信号，`20:15-21:00` 持有
- 横截面排序：`long bottom decile / short top decile / dollar-neutral`

最小 execution / capacity overlay：
- fee：双边合计 `10 bps`
- spread proxy：用持有窗 bar 的 `high-low` 比率缩放成保守 `spread_bps` 代理
- capacity proxy：`2% * hold-window quote-volume` 的简化容量预算中位数

## 3. 主结果
产物：`reports/artifacts/scout_rank148_intraday_cs_reversal_15m/execution_capacity_summary.csv`

### gross 层（只看 alpha 本体）
- `morning ≈ +12.37 bps/day, Sharpe ≈ 2.19`
- `close ≈ +9.41 bps/day, Sharpe ≈ 2.07`

这说明：
- 跟大币 lower-bound 不同，**中盘口袋里确实有 raw alpha 痕迹**；
- 所以它不是“概念直接死掉”，而是“alpha 可能存在，但要看交易摩擦会不会把它吃光”。

### net 层（加最小执行层后）
- `morning ≈ -16.48 bps/day, net Sharpe ≈ -2.92`
- `close ≈ -15.71 bps/day, net Sharpe ≈ -3.45`
- `avg spread proxy ≈ 18.85 / 15.12 bps`
- `median capacity @ 2% hold-window quote-volume ≈ $12.5k / $9.5k`

这一步回答了顶板最关键的问题：
> 它有没有往 `P2` 靠的空间？

当前答案是：**没有。**

原因不是 raw alpha 完全不存在，而是：
1. 要活下来必须吃中盘口袋；
2. 但一旦吃中盘口袋，最小执行层就把 alpha 全部抹掉；
3. 同时容量也很小，不符合 desk 当前“更接近 paper / tiny-live review”的优先级。

## 4. 紧邻子点
**紧邻子点：本轮是否足以给 `promote_P2`？**

结论：**不够，而且应直接 `park`。**

理由：
- 大币宇宙：alpha 弱；
- 中盘宇宙：gross 好看，但 net 完全不行；
- execution fragility 不是小修补级问题，而是这条线当前的结构性主矛盾；
- 继续再磨下去，大概率只是把 `raw-alpha evidence` 写得更花，不会形成 desk 级可交付候选。

## 5. 简短 scorecard
- `usefulness = 2/3`
- `time_stability = 2/3`
- `cross_asset_stability = 1/3`
- `cost_trade_stability = 0/3`
- `deployability = 0/3`
- `recommended_action = park`
- `why_now = 顶板明确要求先回答中盘宇宙与执行层是否能把 keep_P1 推到 P2。`
- `main_weakness = 只有中盘口袋 gross 有效，但最小 execution/capacity overlay 后立即转负且容量太小。`

### hard-fail flags
- `execution_fragile`
- `spread_budget_exceeds_alpha`
- `capacity_small`
- `not_worth_P2_budget`

## 6. 本轮交付
- 日志：`research/optimization_loop/2026-03-23_1058_rank148-midcap-execution-cut.md`
- 产物：
  - `reports/artifacts/scout_rank148_intraday_cs_reversal_15m/midcap_universe.csv`
  - `reports/artifacts/scout_rank148_intraday_cs_reversal_15m/execution_capacity_daily.csv`
  - `reports/artifacts/scout_rank148_intraday_cs_reversal_15m/execution_capacity_summary.csv`
- authoritative writeback：`docs/TODO.md` 顶板最近 evidence 已更新，`Rank 148` 退出 active Scout

## 7. 一句话结论
`Rank 148` 最终给我们的不是新的 `P2`，而是一条更清楚的 desk 结论：
**中盘口袋里可能有 intraday cross-sectional reversal raw alpha，但在当前最小执行/容量约束下不具备继续升层价值，因此本轮应 `park`。**
