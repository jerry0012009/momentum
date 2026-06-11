# Strategy Review (bot2)

Time: 2026-03-29 02:37 UTC

## 本轮一句话判断
`Rank 229` 已经被 bot3 正式升入 `P3 / Paper launch queue`，所以这轮不该再给它排开放式 admission；按 policy，当前最优先动作已经切换为 `P3 launch wiring`。在此之后，最诚实的 fresh intake 顺序是先恢复此前被前排拦住的 `eth-whale`，再看 `liquidity-ranked EMA`。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short --branch`
- 最近 `research/optimization_loop/`：
  - `2026-03-29_0221_rank230_survivor_followup_keep_p1_background.md`
  - `2026-03-29_0048_rank229_p2_time_parameter_promote_p3_queue.md`
  - `2026-03-29_0027_rank229_p2_admission_effectiveness_crossasset_exit_ready.md`
  - `2026-03-29_0008_eth_whale_fresh_intake_blocked_active_p2_front_chain.md`
  - `2026-03-28_2336_rank230_return_relvol_xs_momentum_fresh_intake_keep_p1.md`
- 最近 `research/strategy_review/`：
  - `2026-03-29_0010_strategy-review.md`
  - `2026-03-28_2228_strategy-review.md`
- 为决定新的 fresh intake 顺序，额外核对：
  - `research/quant_digests/2026-03-28_1033_eth-whale-balance-imbalance-alpha.md`
  - `research/quant_digests/2026-03-28_0704_liquidity-ranked-ema-trend-fullstack.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改写 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- `docs/TODO.md` 未参与本轮排班
- 当前前排对象均已带正式 `Rank`

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**是，非空。**

而且这次不是“只有 connected_runner_live 历史遗留所以广义上非空”，而是 runtime 明确写着：
- `current_target: Rank 229 / ETH-led abnormal-day continuation (session-defined)`

这表示 queue 里当前就有一个尚未完成最小接线的新对象，优先级必须压过任何新的 intake。

### Q2. 本轮 `fresh intake` 是什么？
**本轮应该恢复的 fresh intake 是 `research/quant_digests/2026-03-28_1033_eth-whale-balance-imbalance-alpha.md`。**

理由很直接：
- 它在 `2026-03-29_0008_eth_whale_fresh_intake_blocked_active_p2_front_chain.md` 里已经被明确写成“仅因前排 `Active P2 = Rank 229` 未收口而 blocked”；
- 现在 `Rank 229` 已从 `Active P2` 升到 `P3 / Paper launch queue`，survivor 也已经清空，所以这条 blocked intake 应按默认顺序恢复，而不是继续跳去别的发现。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，但已经用完，而且已经诚实收口，不再占前排。**

上一条 fresh intake 是 `Rank 230 / return × relative-volume XS momentum`。它的唯一 survivor follow-up 已在：
- `2026-03-29_0221_rank230_survivor_followup_keep_p1_background.md`

结论已经很清楚：
- standalone short-cycle alpha 过不了成本生存线；
- 可保留为 participation-aware feature family；
- 但不升 `P2`，按预算 `keep_P1 后转 background`。

所以答案不是“继续做 follow-up”，而是：**那唯一一次 follow-up 值得做，且已做完；现在不能再让 `Rank 230` 继续占用 survivor/front slot。**

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。当前 `Active P2 = none`。**

原因：
- `Rank 229` 已在 `2026-03-29_0048_rank229_p2_time_parameter_promote_p3_queue.md` 中完成 `promote_P3`；
- `Rank 230` 的 survivor 也已收口转 background；
- 因此前排已经从 `P2/P1` 收口阶段切换到 `P3 wiring + fresh intake recovery` 阶段。

## 3) rank 合规检查
- `Paper launch queue`：`Rank 229 / 200 / 201 / 213` 都有正式 rank
- `Fresh intake slot`：最近完成对象 `Rank 230` 已有正式 rank
- `Surviving candidate slot`：`none`
- `Active P2 slot`：`none`
- 无需补新的整数 `Rank`

## 4) 为什么这轮必须把重心切到 P3 wiring
policy 的顺序是：
1. `P3 / Paper launch queue` 最小接线与 handoff
2. `P2 / Active P2`
3. `P1 / Surviving candidate`
4. 新的 `fresh intake`

当前 runtime truth 正好对应：
- `P3`: 有，`Rank 229` 正在 queue 中等待最小接线
- `P2`: 无
- `P1`: 无（`Rank 230` 已收口）
- `fresh intake`: 有具体候选，但只能排在 queue-side wiring 之后

因此这轮如果还把 `Rank 229` 继续排成 admission，反而违反 policy；正确做法是：
- 先把 `Rank 229` 推到 `runner script + scheduler + first verified run + runtime writeback`
- 再恢复 `eth-whale` 这条此前被合法拦住的 fresh intake
- 若预算仍有余，再看 `liquidity-ranked EMA` 这条具体新 intake

## 5) 本轮对 state 的实际写回
已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan` 为 4 项：

1. `Rank 229 / ETH-led abnormal-day continuation (session-defined)`
   - `P3 launch wiring`：runner/spec 落库
2. `Rank 229 / ETH-led abnormal-day continuation (session-defined)`
   - `P3 launch wiring`：scheduler + first verified run + runtime writeback
3. `research/quant_digests/2026-03-28_1033_eth-whale-balance-imbalance-alpha.md`
   - 恢复此前被 front-chain 拦住的具体 fresh intake
4. `research/quant_digests/2026-03-28_0704_liquidity-ranked-ema-trend-fullstack.md`
   - 仅在前 3 项已诚实排入后，作为下一条具体 fresh intake

所有新项均满足：
- 只包含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 6) 一句话结论
这轮最重要的变化不是发现新 alpha，而是承认前排阶段已经切换：`Rank 229` 不再属于研究态 `P2`，而属于执行态 `P3 wiring`；只有把这件事诚实写进 state，后面的 `eth-whale` fresh intake 才能按顺序恢复。