# 2026-03-22 09:03 UTC · Rank 30 park reframe review

## Scope
- Source rank: `Rank 30 trendln paired-channel breach / corridor breakout gate`
- Original verdict stays: `park / evidence pool`
- This round only asks: **after the new breakout-bar conviction digest, does Rank 30 deserve one more narrower reframe beyond the already drafted `Rank 30b`?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_1029_rank30-clean-replication-park.md`
  - `research/park_reframe/2026-03-18_1513_rank30-park-reframe.md`
  - `research/quant_digests/2026-03-22_0858_breakout-bar-conviction-gate.md`

## Why revisit Rank 30 now
- `Rank 30` was already reviewed on `2026-03-18`, so by default it should not have been picked again inside 7 days.
- This revisit is only justified because there **is** new evidence: the `2026-03-22 08:58` digest adds a fresh, narrow breakout-bar-quality idea (`body% + edge-close conviction`).
- The question is **not** whether to overturn the original park, and not whether to replace `Rank 30b`; it is only whether this fresh evidence is strong enough to justify a new `Rank 30c`-style branch.

## 1) 原 rank 为什么 park？
`Rank 30` 被 park 的原因很集中：**paired-channel breach 本身不是完全没信息，但突破后的确认层过于脆弱，导致假突破率极高，成本后跨资产仍全负。**

原 clean replication 的核心证据：
- `raw_corridor_breach @ 6bps/side`：`mean_total_return≈-10.73%`、`positive_asset_ratio=0/3`、`mean_false_break_ratio≈86.11%`
- `breach_plus_reclaim_hold @ 6bps/side`：`mean_total_return≈-7.33%`、`positive_asset_ratio=0/3`、`mean_false_break_ratio≈82.39%`
- `mean_width_cv≈0.137`，说明主问题不在通道宽度稳定性，而在**确认层没把真假突破分开**。

翻成人话：
- `reclaim_hold` 比 raw breach 稍好，但远远不够；
- 这条线不是“没有方向事件”，而是“事件后续确认写得太粗”；
- 所以原 `park` verdict 仍必须保留。

## 2) 它更像 hard park 还是 soft park？
**仍然更像 `soft park`。**

理由：
- 原线至少出现过方向上正确但幅度不够的改善：`reclaim_hold` 相比 raw 少亏、假突破率略降；
- 这说明问题更像确认语义不足，而不是 corridor breach 主题彻底失效；
- 但当前证据仍然是 `0/3` 资产为正，所以它离真正 reopen 原 rank 还很远。

## 3) 有没有“可救信号”？
**有，但本轮新证据只算弱到中等的可救信号。**

本轮新增 digest 提醒了一件事：
- breakout 不该只看“越线了没有”，而应先看**突破那一根 bar 自己够不够像真突破**；
- `body_pct + edge-close` 这种 cheap conviction gate，确实比“裸越线”更诚实，也没有 strict BMS 那么稀疏。

但对 `Rank 30` 而言，这个可救信号有两个限制：
1. 它解决的是 **breakout 当根 bar 的质量**，而 `Rank 30` 原始 blocker 更核心的是 **突破后 1~3 根的 hold / reclaim 失败率仍过高**；
2. 这条新证据与已起草的 `Rank 30b`（event-anchored VWAP hold/reclaim）相比，更像更便宜但也更浅的一层前置过滤，而不是更值得单独立项的新主轴。

所以：有可救信号，但不足以再开一条新的派生 rank。

## 4) 最值得改的唯一一刀是什么？
**若只允许保留一个最值得改的轴，仍然是已经写过的那一刀：`breach-event anchored VWAP hold/reclaim`。**

本轮新增的 `body% + edge-close` 读法，更适合被理解为：
- `Rank 30b` 的可选廉价前置过滤提示；
- 或后续 clean replication 时作为附加比较臂；
- 而不是单独再派生一条 `Rank 30c`。

原因很简单：
- `Rank 30` 最深的失败点是 **post-breach acceptance / hold**；
- `AVWAP hold/reclaim` 仍然比单根 breakout-bar conviction 更贴这个核心 blocker；
- 如果现在再开 `Rank 30c=breakout-bar-quality gate`，会开始把同一条 rank 的确认层拆成平行近义分支，违反 bot6 的低频、单轴、简洁原则。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

更准确地说：
- 原 `park` 保留；
- 已存在的 `Rank 30b` 继续保留为该 rank 当前唯一最自然的窄 reframe；
- 本轮新增 breakout-bar conviction 证据，只够作为 `Rank 30b` 的补充思路，不足以再起草新的 `Rank 30c`。

## 6) 本轮结论（固定问答）
- 原 rank 为什么 park？
  - 因为 raw breach 与 `breach_plus_reclaim_hold` 成本后都仍跨资产全负，且假突破率极高；问题集中在确认层不诚实。
- 它更像 hard park 还是 soft park？
  - `soft park`。
- 有没有可救信号？
  - 有；本轮新 digest 说明 breakout-bar conviction 有信息，但更像浅层过滤，不是新的主 reframe。
- 最值得改的唯一一刀是什么？
  - 仍是 `breach-event anchored VWAP hold/reclaim`，不是再开一条 breakout-bar-quality 派生线。
- 是否值得形成新的 derived hypothesis？
  - **否。**

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`
- `note`: `2026-03-22 的 breakout-bar conviction 新证据只够作为 Rank 30b 的补充过滤提示，不足以再派生新的 Rank 30c；当前唯一更值得保留的窄 reframe 仍是已起草的 event-anchored VWAP hold/reclaim。`

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区存在大量无关脏文件与未跟踪文件，当前不适合安全地 selective commit。
