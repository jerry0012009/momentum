# 2026-03-22 00:28 UTC｜bot6 park-reframe｜Rank 33

## 0) 本轮选择（为什么是 Rank 33）
- 约束：本轮只允许从 `Rank 1~37` 的已 `park` 条目里挑 1 条。
- 近 7 天内多数低号 rank 都已被复盘过；因此本轮优先挑一个**上次复盘较早**、且本身存在“局部可救信号但不足以翻案”的对象。
- 选定：`Rank 33 / NW + confirmed HL reclaim`（上次 bot6 复盘：`2026-03-20 11:59 UTC`，结论为 keep_park；本轮只做低频再审，保留原 park 审计意义）。

## 1) 原 Rank 为什么 park？（保留原 verdict 的审计意义）
原始证据来自：`research/optimization_loop/2026-03-17_1150_rank33-clean-replication-park.md`。

核心原因（简化成一句话）：
- **“更干净的结构过滤（NW 平滑 + confirmed HL/LH reclaim）确实降低了假 reclaim，但没有把收益结构一起救活；并且呈现典型 time-pocket：中段亮、前后两端不站住。”**

原 clean replication 的关键数值（6bps/side）：
- `raw_extrema_reclaim`：mean_total_return≈`-1.72%`，positive_asset_ratio=`1/3`，mean_trades≈`355`，false_reclaim_ratio≈`49.1%`
- `nw_hl_reclaim`：mean_total_return≈`-1.39%`，positive_asset_ratio=`1/3`，mean_trades≈`325`，false_reclaim_ratio≈`47.2%`
- `nw_hl_plus_highbreak`（主变体）：mean_total_return≈`-8.51%`，positive_asset_ratio=`1/3`，mean_trades≈`122`，false_reclaim_ratio≈`20.1%`，mean_no_trade_ratio≈`98.7%`
- time-pocket（主变体）：bucket_1≈`-9.24%`，bucket_2≈`+5.03%`，bucket_3≈`-3.95%`

因此原 rank 的 hard verdict 是：`park / evidence pool`。

## 2) 更像 hard park 还是 soft park？
- **偏 soft park**。
- 理由：它不是“所有面都硬 fail”。相反，`NW` 平滑把 `false_reclaim_ratio` 压低这一点是**可复用的方向性信号**；只是当它被当成“独立 entry alpha”时，收益与 time-pocket 稳定性不够支撑继续占用主资源。

## 3) 有没有“可救信号”？
有，但很窄：
- `false_reclaim_ratio` 从 ~`49%` 被压到 ~`47%`（nw_hl_reclaim），进一步加 `highbreak` 后可压到 ~`20%`。
- 这说明 Rank 33 的信息量更像：**“如何识别/过滤假 reclaim”**，而不是“给出可直接交易的 entry”。

## 4) 最值得改的唯一一刀是什么？（单一修改轴）
**单一修改轴（只改角色，不改原结构定义）：把 Rank 33 从 standalone entry 改写为 `shared false-reclaim veto gate`。**

更具体的可执行口径（不在本轮落到 TODO，只写成 reframe 方向）：
- 保留 Rank 33 的 `NW + confirmed HL/LH reclaim` 判定逻辑作为一个 *gate*；
- 但它不再自己触发开仓，而是**只对既有、已冻结的 base setup**（例如 breakout-short / Fib retest_hold / EMA-PSAR continuation）给出 `allow / veto / (可选) half-size` 的裁决：
  - 当 `Rank33_reclaim_ok=false`（或 reclaim 刚发生但质量差）时，**veto 新 entry**（避免把“假 reclaim”当 continuation）；
  - 当 `Rank33_reclaim_ok=true` 时，允许 base setup 按原规则出手。

trade on / trade off（供后续 bot2 判断是否入板）：
- trade on：把 Rank 33 里唯一相对干净的信号（降低假 reclaim）迁移到更该承担它的层级——**shared 过滤层**；避免继续把它误当成独立 alpha。
- trade off：trade density 会下降，且仍可能是“砍单美化”。因此若未来真要验证，第一刀必须是 **baseline vs veto-only** 的 strict A/B（不偷带新 exit / 新 universe / 新 regime）。

## 5) 是否值得形成新的 derived hypothesis？
- 本轮结论：`soft_reframe_candidate`（不直接 draft 成 `Rank 33b`）。
- 原因：
  1. 该思路与现有队列里多条“demote standalone -> shared veto/overlay”的范式一致，但 Rank 33 的独特点（假 reclaim 过滤）**还没证明对现有三条收口线有净增量**；
  2. 且它容易滑向“多轴修补”（引入新的 regime / expiry / MTF 结构）来硬救，本轮不做。

若未来 fresh intake 不足、且 bot2 需要挑 1 条 queue-only 线来补“shared failure filter”时，Rank 33 可作为候选之一；但现在不应再扩写成 derived 条目。

## 6) 允许的最终结论
- `soft_reframe_candidate`

## 7) 本轮文件改动
- 新增本轮日志：本文件
- 追加更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## 8) Commit
- 默认不提交：近期 workspace 常见有无关脏文件风险，本轮只做最小必要文档更新。
