# 2026-04-23 19:49 UTC · Rank 11 park reframe review

## Why this rank
- 本轮按 `Rank 1~37` 已 park 条目里择 1 条复盘。
- 近 7 天内大部分低号 parked rank 都已被复盘；`Rank 11` 属于较早一批、且最近没有出现足以改变对象边界的新证据，因此本轮做一次低频复核。
- `Rank 2 / Rank 17` 当前不是 parked 条目，不在本轮范围。

## Original park reason
- 原始对象：`Lo-style causal extrema pattern gate`。
- 2026-03-16 clean replication + Light Stability Pack 的硬结论是四项全 fail：
  - 时间稳定性 `fail`（`1/3` positive buckets）
  - 参数稳定性 `fail`（`0/5` 邻域为正）
  - 跨标的稳定性 `fail`（`0/3` 资产为正）
  - 成本/交易数稳定性 `fail`（`0/4` cost levels 为正）
- 6bps/side 下关键读数约为：`mean_total_return ≈ -4.33%`、`positive_asset_ratio = 0/3`、`mean_trades ≈ 58.3`。
- 因此它被 park 不是因为“样本太少还没看清”，而是因为旧 trigger 语言在收益、稳定性、成本三层都没有留下可交易余量。

## Hard park or soft park?
- 结论：**更像 hard park**。
- 原因不是“主题彻底没信息”，而是：若想把残余信息救出来，必须把旧的 causal-extrema pattern gate 改写成更窄的 event-defined reversal / path-state raw alpha；这已经不是在修旧 Rank 11，而是在换主语。

## Salvage signal
- 有弱“可救信号”，但**不属于旧 Rank 11 本体**。
- 4 月以来的旁证（如 sparse-jump trend/reversal router、部分结构/路径型 reversal 线索）继续说明：reversal / pattern 主题可能仍有信息量。
- 但这些信号成立的前提都是更具体的事件锚、状态切换或 raw-alpha 宿主，而不是旧 Rank 11 这种泛 causal-extrema gate。
- 换句话说：可救的是主题，不是旧对象。

## The single best cut
- 若只讨论“最值得改的唯一一刀”，那只能是：**把旧的 generic causal-extrema trigger 改写成 event-anchored reversal trigger**。
- 但这刀一落下，就已经越过 `Rank 11` 的对象边界，属于新 family，而不是诚实的 `Rank 11b`。
- 因此这条“一刀”本轮只作为否决理由记录，不形成派生假设。

## Derived hypothesis?
- **不值得形成新的 derived hypothesis。**
- 原因：
  1. 原 `park` verdict 的审计意义很清楚，没被推翻；
  2. 唯一可想象的改单轴会直接改掉对象身份；
  3. 近期没有新的 decisive evidence 证明旧 Rank 11 仍保有独立 queue-facing residual。

## This round verdict
- `keep_park`

## Short answer template
1. 原 rank 为什么 park？
   - 因为 clean replication 与四项稳定性检查一起失败，旧 causal-extrema gate 在收益、稳定性、跨标的、成本上都未保留可交易余量。
2. 它更像 hard park 还是 soft park？
   - 更像 hard park。
3. 有没有“可救信号”？
   - 有，但外流到了更窄的 event-driven reversal / path-state raw-alpha family，不属于旧 Rank 11 本体。
4. 最值得改的唯一一刀是什么？
   - 把 generic causal-extrema 触发改成 event-anchored reversal trigger；但这等于换主语，不应挂回 Rank 11。
5. 是否值得形成新的 derived hypothesis？
   - 不值得；本轮保持 `keep_park`。

## File / process notes
- 本轮只更新 `research/park_reframe/INDEX.md` 与 `docs/PARK_REFRAME_QUEUE.md` 的最小必要片段。
- 当前 git 工作区存在大量与本轮无关未跟踪文件，不适合做 selective commit，因此不提交。