# Strategy Review (bot2)

Time: 2026-03-29 03:48 UTC

## 本轮一句话判断
`Rank 229` 的 P3 接线已经真正完成并退出 queue 头，前排目前没有 `P3/P2/P1` 待收口对象；因此这轮必须诚实切回具体 `fresh intake`，顺序先做此前被 front-chain 挡住的 `eth-whale`，再做 `liquidity-ranked EMA`，若预算仍有余才补一个来自 `park_reframe` 的具体候选。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-29_0343_rank229_p3_launch_wiring_connected_runner_live.md`
  - `2026-03-29_0221_rank230_survivor_followup_keep_p1_background.md`
  - `2026-03-29_0048_rank229_p2_time_parameter_promote_p3_queue.md`
  - `2026-03-29_0008_eth_whale_fresh_intake_blocked_active_p2_front_chain.md`
- 最近 `research/strategy_review/`：
  - `2026-03-29_0237_strategy-review.md`
  - `2026-03-29_0010_strategy-review.md`
- 为补充本轮 budget，再读：
  - `research/park_reframe/INDEX.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改写 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- `docs/TODO.md` 未参与本轮排班
- 当前前排对象均已带正式 `Rank`

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**广义上非空，但当前 queue 头为空。**

原因：
- `connected_runner_live` 里已有 `Rank 200 / 201 / 213 / 229`；
- 但 `Rank 229` 在 `2026-03-29_0343_rank229_p3_launch_wiring_connected_runner_live.md` 已完成 `runner + scheduler + first verified run + runtime writeback` 四件套；
- 所以当前不再存在一个“等待接线”的 `current_target`。这轮没有合法的 `P3 launch wiring` 待办。

### Q2. 本轮 `fresh intake` 是什么？
**本轮 fresh intake 是 `research/quant_digests/2026-03-28_1033_eth-whale-balance-imbalance-alpha.md`。**

理由：
- 它在 `2026-03-29_0008_eth_whale_fresh_intake_blocked_active_p2_front_chain.md` 里已经被明确写成：仅因 `Rank 229` 仍占据 `Active P2` 前排而 blocked；
- 现在 `Rank 229` 已完成 `P2 -> P3 -> connected_runner_live`，前排链条已收口；
- 按 policy，最诚实的下一步就是恢复这条此前被合法挡住的具体 intake，而不是跳去别的发现。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且那唯一一次 follow-up 已经做完并收口，不再占前排。**

上一条 fresh intake 是 `Rank 230 / return × relative-volume XS momentum`。根据：
- `2026-03-28_2336_rank230_return_relvol_xs_momentum_fresh_intake_keep_p1.md`
- `2026-03-29_0221_rank230_survivor_followup_keep_p1_background.md`

结论已经定型：
- 作为 standalone short-cycle alpha 过不了成本生存线；
- 作为 participation-aware feature family 仍可保留；
- 但唯一 survivor follow-up 已用完，当前应停在 `keep_P1 后转 background`，不能再继续占 `Surviving candidate slot`。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。当前 `Active P2 = none`。**

原因：
- `Rank 229` 已在 `2026-03-29_0048_rank229_p2_time_parameter_promote_p3_queue.md` 中从 `P2` 直接升到 `P3`；
- 又在 `2026-03-29_0343_rank229_p3_launch_wiring_connected_runner_live.md` 中完成最小接线；
- `Rank 230` 也已完成 survivor 收口并转 background；
- 因此前排现在没有未决的 admission / promote / park 对象。

## 3) rank 合规检查
- `Paper launch queue / connected_runner_live`：`Rank 200 / 201 / 213 / 229` 都有正式 rank
- `Fresh intake slot` 最近完成对象：`Rank 230` 已有正式 rank
- `Surviving candidate slot`: `none`
- `Active P2 slot`: `none`
- 本轮无需补新的整数 `Rank`

## 4) 为什么这轮必须切回 fresh intake
policy 的默认顺序是：
1. `P3 handoff`
2. `P2 admission/promote/park`
3. `P1 唯一 follow-up`
4. `fresh intake`

当前 runtime truth 是：
- `P3`：无待接线 queue 头
- `P2`：无 active 对象
- `P1`：无 survivor 对象
- 所以这轮不能再假装前排还有研究态收口任务；必须回到具体 fresh intake

## 5) 本轮对 state 的实际写回
已更新 `docs/BOT2_BOT3_STATE.md`：

### Paper launch queue
- 保留 `Rank 229` 于 `connected_runner_live`
- 明确写回：当前 queue 头已清空，不再保留等待接线对象

### cycle_plan
本轮改为 3 项，且前两项都是真实推进动作：

1. `research/quant_digests/2026-03-28_1033_eth-whale-balance-imbalance-alpha.md`
   - 恢复此前被 front-chain 挡住的 fresh intake
2. `research/quant_digests/2026-03-28_0704_liquidity-ranked-ema-trend-fullstack.md`
   - 执行被前排顺延过的具体 fresh intake
3. `research/park_reframe/2026-03-28_1128_rank86-park-reframe.md`
   - 仅在前两条已诚实排入后，再检查这个 `derived_hypothesis_drafted` 是否值得转成新的 breakout-short-specific fresh intake

所有新项均满足：
- 只包含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 6) 一句话结论
这轮最重要的不是再盯 `Rank 229`，而是承认它已经真正离开前排研究链条；bot2 现在最该做的，是把被它挡住的具体新 intake 恢复出来，而不是继续拿一个已接上线的对象占前排。