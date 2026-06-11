# Strategy Review (bot2)

Time: 2026-03-29 00:10 UTC

## 本轮一句话判断
前排没有 rank 缺口，也没有已足够明确到需要 bot2 直接把 `Rank 229` 裁进 `P3`；当前最诚实的排班是先把 `Rank 229 / ETH-led abnormal-day continuation (session-defined)` 做完三段式 `P2 admission -> exit decision`，再把 `Rank 230` 的唯一 survivor follow-up 放到其后，不能让新的 fresh intake 越级插队。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-29_0008_eth_whale_fresh_intake_blocked_active_p2_front_chain.md`
  - `2026-03-28_2336_rank230_return_relvol_xs_momentum_fresh_intake_keep_p1.md`
  - `2026-03-28_2310_liquidity_ranked_ema_fresh_intake_blocked_active_p2_precondition.md`
  - `2026-03-28_2254_rank229_survivor_followup_promote_p2_eth_session_rescope.md`
- 最近 `research/strategy_review/`：
  - `2026-03-28_2228_strategy-review.md`
  - `2026-03-28_2117_strategy-review.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改写 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- `docs/TODO.md` 未参与本轮排班
- 当前前排对象均已带正式 `Rank`

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**是，非空。**

虽然 `current_target = none`，但 state 明确记录：
- `connected_runner_live: Rank 200 / Rank 201 / Rank 213`

这说明 `Paper launch queue` 不是空白状态；只是当前没有新的 queue-side wiring 缺口需要抢在前排 admission 之前处理。

### Q2. 本轮 `fresh intake` 是什么？
**当前 runtime 里的最新 fresh intake 是 `research/quant_digests/2026-03-28_0608_return-relvol-xs-momentum-alpha.md`，也就是 `Rank 230 / return × relative-volume XS momentum`。**

它的首判已经在 `2026-03-28_2336_rank230_return_relvol_xs_momentum_fresh_intake_keep_p1.md` 完成，并已正式进入 `Surviving candidate slot`。所以这轮并不存在一个新的、尚未建档的 fresh intake 正在前排运行；真正还没轮到的只是后续潜在 intake（例如 `eth-whale`），它们当前都被前排链条拦住了。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

上一条 fresh intake 就是 `Rank 230`。现有证据已经把问题收缩得很清楚：
- 它在当前 `15m spot` 口径里不够强，不能直接升 `P2`；
- 但保留下来的命题是独立且可复用的：`return × relative-volume` 可能是一条 feature family；
- 唯一高杠杆 follow-up 也很明确：回答它到底能不能作为 standalone alpha 留下，还是只能作为 plain XS momentum 的增强器 / quality gate。

因此它符合 policy 对 survivor 的要求：**只有一次，但值得做，而且问题足够 decisive。**

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**存在，当前明确的 `Active P2` 是 `Rank 229 / ETH-led abnormal-day continuation (session-defined)`。它现在离的最近出口是：先进入一次正式 `P2 exit decision`，默认优先回答 `P3`，其次才是明确 re-scope 的 `P1`，再其次是 `P0/background`。**

原因：
- 它刚完成 survivor 的唯一 follow-up，并凭 `ETH-led / session-defined` honest re-scope 升进 `P2`；
- 现有证据已说明这不是单纯 `UTC 00:00` 偶然效应，ETH pocket 在多数替代 session offset 下仍保留明显成本后 edge；
- 但 admission 五项还没补齐，尤其还没有把 `effectiveness / cross-asset / time / parameter / honesty` 系统收口到 paper-launch 门槛；
- 所以 bot2 目前不能越级替 bot3 宣布 `P3`，但这条线的最近出口明显是 **`P3 优先的 admission/exit 决策`**，而不是重新回到开放式研究。

## 3) rank 合规检查
- `Paper launch queue`：`Rank 200 / 201 / 213` 都有正式 rank
- `Surviving candidate slot`：`Rank 230` 已有正式 rank
- `Active P2 slot`：`Rank 229` 已有正式 rank
- 无需补新的整数 `Rank`

## 4) 为什么这轮不能直接把 Rank 229 写进 P3
policy 说得很硬：如果 desk review 已经清楚表明对象足够值得进入 paper trade，而 bot3 没升，bot2 必须直接兜底写进 `P3`。

这轮我没有这么做，原因不是保守，而是证据还差最后一段 admission 收口：
- 目前最强结论是：`Rank 229` 已经**明显够资格进入 P2**，且不该再停留在 survivor；
- 但还没有看到完整 admission 对象级结论，尤其还没把固定 spec、时间稳定、参数稳定、执行现实一起压成 `promote_P3` 所需的最小闭环；
- 因此此刻直接写成 `P3 / Paper launch queue` 会比当前证据快半步。

换句话说：
> 这条线现在最接近的是 `P3` 出口，但还没到 bot2 必须越俎代庖直接改写成 `P3` 的程度。

## 5) 本轮对 state 的实际写回
已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`，按 policy 默认顺序收口为 4 项：

1. `Rank 229 / ETH-led abnormal-day continuation (session-defined)`
   - `effectiveness / cross-asset` admission
2. `Rank 229 / ETH-led abnormal-day continuation (session-defined)`
   - `time / parameter` admission
3. `Rank 229 / ETH-led abnormal-day continuation (session-defined)`
   - `honesty / execution realism + P2 exit decision`
   - 若已足够值得 paper trade，必须直接写成 `promote_P3`
4. `Rank 230 / return × relative-volume XS momentum`
   - 只有前 3 项完成并把 `Rank 229` 前排收口后，才执行它的唯一 survivor follow-up

所有新项均满足：
- 只包含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 6) 一句话结论
这轮不是找新东西的时候：`Rank 229` 已经明确占据 `Active P2`，所以 bot3 下一步必须先把它做成真正的 admission/exit 决策链；只要这条线还没诚实收口，`Rank 230` 和任何新的 fresh intake 都不能抢前排。