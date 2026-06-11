# 2026-04-09 04:24 UTC · Rank 31 stale pending duplicate — blocked

- policy read: `docs/BOT2_BOT3_POLICY.md`
- runtime read: `docs/BOT2_BOT3_STATE.md`
- executed cycle item: `Rank 31 / false structural reclaim long continuation -> short failure-followthrough`
- scope rule: 只执行当前排在最前的 pending 小点；不重排后续 `cycle_plan`

## 本轮要回答的唯一问题
当前 `cycle_plan` 里把 `Rank 31` 的 `trade false structural reclaim as short failure-followthrough` 当作 fresh intake pending，这个对象是否仍然是一个**尚未被正式前排化、尚未收口**的合法新 intake？

## 读取到的关键 runtime 事实
1. `research/park_reframe/2026-03-22_0439_rank31-park-reframe.md`
   - 原 `Rank 31` 的唯一窄 residual 已被明确写成：`invert false reclaim into short failure-followthrough`。
2. `research/optimization_loop/2026-03-30_0439_rank246_false_reclaim_short_intake_keep_p1.md`
   - 这条 residual 当时已经被正式前排化，并分配了新的正式整数 `Rank 246 / false structural reclaim short failure-followthrough`；也就是说，它不再是“未分配 rank 的 parked residual”。
3. `research/optimization_loop/2026-03-30_0456_rank246_survivor_followup_background.md`
   - `Rank 246` 已完成唯一允许的 survivor follow-up，并在冻结同一 `BTC/ETH/SOL, 120d, 15m, 6bps/side` 口径下得到干净负结论：`6bps/side` 三资产全负、`positive_asset_ratio=0/3`，因此已正式回 `background/P0`。
4. `research/park_reframe/2026-04-06_0817_rank31-park-reframe.md`
   - 更晚的复盘再次确认：`Rank 31` 的原始 long structural reclaim 仍是 hard park；唯一 soft residual 已被既有 `Rank 31b` / `Rank 246` 消费，不值得再派生新的 `Rank 31c`。

## 本轮判断
当前这条 pending **不是合法的 fresh intake**，而是一个已经被历史 runtime truth 消费并收口过的过期重复项。

原因：
1. 它对应的唯一诚实 residual，早在 `2026-03-30 04:39 UTC` 就已经被正式分配为 `Rank 246`；
2. 该对象随后又在 `2026-03-30 04:56 UTC` 完成唯一 survivor 检查并回到 `background/P0`；
3. `2026-04-06 08:17 UTC` 的更晚 park reframe 进一步确认，没有新的 `Rank 31c` 可以诚实再派生；
4. 因此本轮若再把它当 fresh intake 执行，就会违反 policy 的 `Background pool do_not_auto_reopen` 与 `不得把已收口 residual 重新当前排 pending` 的约束。

## 正式结论
- 当前 `cycle_plan` 里的这条 `Rank 31` pending 应按 **`stale duplicate blocked`** 收口。
- 它不会生成新的 `keep_P1 / P2 / P3` verdict，也不会触发新的 rank 分配。
- runtime 应只更新当前小点本身：把该项写成 `blocked`，并把结果明确写成“`Rank 31` 的唯一诚实 residual 已被 `Rank 246` 前排化并收口回 background，因此不能再作为 fresh intake 重做 first verdict”。

## Runtime writeback
- `cycle_plan[2]`：`status -> blocked`
- `cycle_plan[2].result`：写成 `Rank 31` 的唯一诚实 residual 已在 2026-03-30 被正式前排化为 `Rank 246` 并在唯一 survivor follow-up 后回到 background；2026-04-06 更晚复盘也确认不存在新的 `Rank 31c`，因此本项按 stale duplicate blocked 处理。

## 本轮 reader-facing 变化
- 无新的正式 rank、无层级变化、无新页面交付。
- 本轮属于 runtime guard 收口：阻止一个已被消费并已回背景池的旧 residual 被误当成 fresh intake 重开。
