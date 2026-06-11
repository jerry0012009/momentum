# 2026-03-17 20:22 UTC · Rank 32 park reframe review

## Source
- source rank: `Rank 32 EMA structure vs MA slope direction gate`
- source evidence:
  - `docs/TODO.md`
  - `research/optimization_loop/2026-03-17_1123_rank32-clean-replication-park.md`
  - `reports/site/factors/scout_rank32_ema_slope_structure_15m/report.html`

## Why this rank
- 还在 `Rank 1~37` 的已 `park` 范围内。
- 当前 `docs/PARK_REFRAME_QUEUE.md` 还是空，最近 `7` 天也没有这条 rank 的 `bot6` 复盘记录。
- 它不是“全线塌掉”的 hard fail，而是更像“有正 pocket，但当前执行形态太稀”。这类条目最适合做低频 reframe 审视。

## 1) 原 rank 为什么 park？
原结论并不是“完全没 edge”，而是**当前冻结形态不够诚实地进入 paper candidate pool**。

来自原 clean replication 的关键证据：
- `ema_cross_only`：`6bps/side mean_total_return≈-18.73%`、`positive_asset_ratio=1/3`、`mean_trades≈257.3`
- `ema_cross_plus_slope_floor`：`6bps/side mean_total_return≈+50.76%`、`positive_asset_ratio=3/3`、`mean_trades≈75.7`、`mean_no_trade_ratio≈99.34%`
- `ema_cross_plus_slope_reclaim`（原主变体）：`6bps/side mean_total_return≈+24.79%`、`positive_asset_ratio=3/3`、`mean_trades≈25.0`、`mean_false_reclaim_ratio≈12.93%`、`mean_no_trade_ratio≈99.78%`

真正把它压回 `park` 的主因：
1. 原主变体 `slope_reclaim` 的交易密度过薄；
2. `mean_no_trade_ratio≈99.78%`，说明它更像极稀事件，不像当前 desk 默认可推进候选；
3. 正 pocket 虽存在，但不足以支撑直接升格。

因此原 `park` verdict 仍应保留，不能被这次 reframe 复盘推翻。

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`。**

原因：
- 不是单一热像素：`slope_reclaim` 的 slope-pocket 里 `bucket_1≈+0.06%`、`bucket_2≈+4.78%`、`bucket_3≈+18.39%`，并非只有一格偶然翻正；
- `slope_floor` 这一档比 `cross_only` 明显更强，说明真正有信息量的部分可能是 **slope-aligned direction state**，而不是更宽泛的 EMA cross 本身；
- 但它也没有强到可以撤销原 `park`：因为当前可执行形态仍旧太稀。

## 3) 有没有“可救信号”？
**有，但集中在一个非常窄的点：`slope floor` 本身可能比 `reclaim` 子句更像真正贡献 edge 的那一刀。**

最值得保留的可救信号：
- 从 `cross_only -> slope_floor`，绩效和跨标的一致性明显改善；
- 从 `slope_floor -> slope_reclaim`，反而把 trade count 从 `≈75.7` 进一步压到 `≈25.0`，说明额外的 `reclaim` 约束很可能在“压掉噪声”的同时，也把大量可用样本一起压没了；
- 原文档里最诚实的 blocker，其实不是“slope 逻辑无效”，而是“当前 reclaim-严格版太稀”。

## 4) 最值得改的唯一一刀是什么？
**唯一主修改轴：去掉 `spread-mid reclaim` 这层额外约束，只保留 `EMA cross + aligned slope floor`。**

也就是：
- 保留：higher-tf EMA fast/slow 同向 + slope floor 方向一致；
- 去掉：最近 4 根里必须先出现一次向 `spread mid` 的回抽、再重新站回同侧 的那层 reclaim 过滤。

为什么这是一刀、而不是多轴大改：
- 不换 universe；
- 不换 holding / execution 基本口径；
- 不换 higher-tf family；
- 只改原规则里的**一个子句**：`reclaim requirement`。

## 5) 是否值得形成新的 derived hypothesis？
**值得，结论：`derived_hypothesis_drafted`。**

不是因为原 rank 已经翻案，而是因为：
- 原证据已经明确暴露出“edge 更可能坐落在 slope floor，而不是 reclaim 严格版”这个方向；
- 这条改动足够窄、足够单轴；
- 它适合作为一个新的、可被 `bot2` 判断是否入板的短提案，而不是直接把 `Rank 32` 历史改写成 active 候选。

## 6) Drafted derived hypothesis
- proposed_rank: `Rank 32b / Rank 32 slope-floor continuation gate`
- source_rank: `Rank 32`
- status: `derived_hypothesis_drafted`
- single modification axis: `remove spread-mid reclaim requirement; keep EMA cross + aligned slope floor only`
- trade on: `higher-tf EMA fast > slow（空头镜像）且 fast/slow slope 同向并过最小门槛；15m close 重新站回 fast EMA 后按 next-bar open 入场`
- trade off: `EMA direction 缺失、slope 不同向/不过门槛；不再额外要求最近 4 根出现一次 spread-mid reclaim`
- trade on / trade off summary: `trade on` 更押注 slope-aligned direction state 是主 edge；`trade off` 是放弃 reclaim 那层更“漂亮”的 pullback 约束
- trade off / risk: 交易数会上升，但也可能重新放大假信号与噪声；如果 edge 其实来自极稀的 reclaim pocket，这条派生线会显著变差
- why now: 原 clean replication 已经把三档关系讲清楚——`cross_only` 太弱，`slope_floor` 最像正 pocket，`slope_reclaim` 则把样本压得过稀；因此当前最自然的一刀，就是直接回答 `reclaim` 是否过严
- suggested initial state: `source intake / clean replication next`

## Final verdict for this round
- round verdict: **`derived_hypothesis_drafted`**
- source-rank historical verdict: **keep original `park` unchanged**

## Why not stronger than this
- 这还不是要把它写回 `TODO` 顶部，也不是让 `bot3` 立刻重跑；
- 目前还没有证明 `Rank 32b` 一定能在更高 trade density 下保住跨标的与成本后表现；
- 所以这一步只应该进入 `PARK_REFRAME_QUEUE`，作为在 fresh intake 不足时可供 `bot2` 低频认领的窄提案。

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区仍有无关脏文件，当前不适合安全地 selective commit。