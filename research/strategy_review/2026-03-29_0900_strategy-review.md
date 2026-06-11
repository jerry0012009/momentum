# Strategy Review (bot2)

Time: 2026-03-29 09:00 UTC

## 本轮一句话判断
当前没有待接线 `P3`、没有 `Active P2`；前排唯一必须先收口的对象是 `Rank 233 / volume-shock polarity-by-coin`。因此本轮必须先把它的唯一 survivor follow-up 排到首位；只有它诚实收口后，才允许切回新的 fresh intake。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 `research/optimization_loop/`：
  - `2026-03-29_0857_multiday_max_lottery_intake_blocked_survivor_slot_occupied.md`
  - `2026-03-29_0836_rank233_volume_shock_polarity_fresh_intake_keep_p1.md`
  - `2026-03-29_0828_rank232_survivor_quote_based_honesty_cut_keep_p1_background.md`
  - `2026-03-29_0343_rank229_p3_launch_wiring_connected_runner_live.md`
  - `2026-03-29_0048_rank229_p2_time_parameter_promote_p3_queue.md`
- 最近 `research/strategy_review/`：
  - `2026-03-29_0812_strategy-review.md`

为挑合法 conditional intake，再读：
- `research/park_reframe/INDEX.md`

硬约束遵守：
- 只更新了 `docs/BOT2_BOT3_STATE.md`
- 未改写 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- `docs/TODO.md` 未参与本轮排班
- 当前前排对象均已有正式 `Rank`，无需补新的整数 `Rank`

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**当前 queue 头为空。**

更具体地说：
- `current_target: none`
- 已接上线的 `connected_runner_live` 仍包含 `Rank 200 / 201 / 213 / 229`
- 这说明当前没有待 bot3 优先处理的 `P3 launch wiring` 对象

所以本轮不需要把资源放在 `P3 handoff`。

### Q2. 本轮 `fresh intake` 是什么？
**本轮真正应切回的 fresh intake 是 `research/quant_digests/2026-03-29_0742_multiday-max-lottery-xs-continuation-alpha.md`，但前提是先把 `Rank 233` 的 survivor follow-up 诚实收口。**

原因：
- 最近完成首判的 fresh intake 已经是 `Rank 233 / volume-shock polarity-by-coin`
- 它当前占据 survivor 槽位，且还剩唯一一次 decisive follow-up
- `2026-03-29_0857_multiday_max_lottery_intake_blocked_survivor_slot_occupied.md` 已证明：在 survivor 未收口前，新的 fresh intake 不能抢到前面

所以这轮“fresh intake 是谁”的正确答案，不是当前 front slot 里正在跑的对象，而是**survivor 收口之后的下一条具体 intake：`multiday MAX / lottery rich-vs-cheap continuation`**。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

上一条 fresh intake 是 `Rank 233 / volume-shock polarity-by-coin`。根据 `2026-03-29_0836_rank233_volume_shock_polarity_fresh_intake_keep_p1.md`：
- 它已经证明自己不是统一 continuation gate，而是值得独立保留的 coin-specific post-shock raw alpha family
- 但当前样本只到约 17 天，且未扣费，真正唯一高杠杆 blocker 很明确：
  - `180d frozen replication`
  - `next-bar open + no-overlap + 6bps/side`
  - `monthly polarity map` 必须胜过 `always continuation / always fade`

这正符合 policy 对 survivor 的定义：保留 **1 次** cheap-but-decisive follow-up，直接回答它能不能进 `P2`。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。当前 `Active P2 = none`。**

原因：
- `Rank 229` 已完成 `P2 -> P3 -> connected_runner_live`
- `Rank 232` 已完成唯一 survivor follow-up，并按 `keep_P1 后转 background` 收口
- `Rank 233` 仍处于 survivor，而不是 `P2 admission`
- 最近结果里没有新的 `promote_P2` writeback

所以本轮没有合法的 `P2 -> P3 / P1 / P0` 出口决策对象。

## 3) rank 合规检查
- `Paper launch queue / connected_runner_live`：`Rank 200 / 201 / 213 / 229` 都有 rank
- `Surviving candidate slot`：`Rank 233` 已有 rank
- `Active P2 slot`：`none`
- 结论：**本轮无需补新的整数 `Rank`**

## 4) 本轮排班逻辑
按 policy 默认顺序扫描：
1. `P3 handoff`：无 queue 头，跳过
2. `P2 admission/promote/park`：无 active P2，跳过
3. `P1 survivor 唯一一次诚实检查`：**有，且必须优先处理 `Rank 233`**
4. `fresh intake`：只能在 `Rank 233` 收口之后切回，第一条应是 `multiday MAX / lottery rich-vs-cheap continuation`
5. 若预算仍有余，再补合法的 conditional intake；优先来自 `park_reframe/INDEX.md` 的 `derived_hypothesis_drafted`

因此本轮合法且具体的顺序应是：
1. `Rank 233 / volume-shock polarity-by-coin` survivor 唯一 follow-up
2. `research/quant_digests/2026-03-29_0742_multiday-max-lottery-xs-continuation-alpha.md` fresh intake
3. `research/park_reframe/2026-03-29_0703_rank64-park-reframe.md` conditional fresh intake
4. `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md` conditional fresh intake

## 5) 本轮对 state 的实际写回
已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`：
1. `Rank 233 / volume-shock polarity-by-coin`
2. `research/quant_digests/2026-03-29_0742_multiday-max-lottery-xs-continuation-alpha.md`
3. `research/park_reframe/2026-03-29_0703_rank64-park-reframe.md`
4. `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`

所有新生成项都满足：
- 只包含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 6) 为什么没有直接改别的槽位
- `Paper launch queue` 当前没有待接线对象，不需要改
- `Fresh intake slot` 当前记录 `Rank 233` 的已完成首判，是正确 runtime truth，不应伪造切换
- `Surviving candidate slot` 当前锁定 `Rank 233`，也是正确 runtime truth
- `Active P2 slot` 仍然是 `none`

## 7) 一句话结论
这轮最该做的不是再找新花样，而是先把 `Rank 233` 那唯一一次 decisive follow-up 做完；只有它诚实收口后，bot3 才能切回 `multiday MAX`，再用剩余预算检查 `Rank 64b` 和 `Rank 86b` 这两条最新、最像新对象的 park-reframe 派生线。