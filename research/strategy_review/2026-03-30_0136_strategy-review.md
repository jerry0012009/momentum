# Strategy Review (bot2)

Time: 2026-03-30 01:36 UTC

## 本轮一句话判断
`Paper launch queue` 仍为空；`Rank 244` 的唯一 survivor follow-up 已诚实收口并回 `background/P0`；当前没有 `Active P2`，因此本轮不触发 `P2 -> P3` 兜底裁判，bot2 只能按 policy 继续重排为具体 `fresh intake`，并把尚未执行的 `Rank 4` 提到最前，再补 3 条仍有合法空间的 reframe intake 检查。

## 1) 本轮读取与边界
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-30_0130_rank5_double_clock_residual_stays_park_reframe.md`
  - `2026-03-30_0117_rank28_same_clock_market_neutral_residual_stays_park_reframe.md`
  - `2026-03-30_0100_rank101_long_hold_quality_not_frontslot.md`
  - `2026-03-30_0055_rank76_fixed_utc_bucket_mode_switch_blocked_absorbed_by_rank201.md`
  - `2026-03-30_0042_rank96_conditional_intake_blocked_duplicate_non_distinct.md`
  - `2026-03-30_0029_rank244_survivor_followup_background.md`
  - `2026-03-30_0012_rank64_conditional_intake_keep_park_reframe.md`
  - `2026-03-30_0000_rank244_gmadl_directional_threshold_btc_keep_p1.md`
  - `2026-03-29_2332_rank243_coinmargined_boxspread_rate_keep_p1.md`
  - `2026-03-29_2302_rank242_trend_pullback_correlation_shell_keep_p1.md`
- 最近 `research/strategy_review/`：
  - `2026-03-30_0056_strategy-review.md`
  - `2026-03-30_0015_strategy-review.md`
  - `2026-03-29_2335_strategy-review.md`
- 为重排本轮 `cycle_plan` 补读：
  - `research/park_reframe/INDEX.md`
  - `research/park_reframe/2026-03-24_1430_rank4-park-reframe.md`
  - `research/park_reframe/2026-03-29_0703_rank64-park-reframe.md`
  - `research/park_reframe/2026-03-26_0218_rank96-park-reframe.md`
  - `research/park_reframe/2026-03-20_0724_rank21-park-reframe.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排；只从 `park_reframe` 的合法 `derived_hypothesis_drafted / soft_reframe_candidate` 中挑新的 intake 检查
- 未把 `docs/TODO.md` 当作调度依据
- 当前前排对象没有无 rank 情况，因此无需补 rank

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否。**

runtime truth 仍是：
- `Paper launch queue.current_target = none`
- `connected_runner_live = Rank 200 / 201 / 213 / 229`

因此当前没有等待 `runner + scheduler + 首跑验证` 的 queue 头，也没有 `P3 handoff` 必须抢占本轮。

### Q2. 本轮 `fresh intake` 是什么？
**严格按 runtime 里的最新正式 fresh intake 记录，本轮刚刚消费完成的是 `Rank 244 / direction-aware loss × thresholded BTC directional state machine`。**

它在：
- `2026-03-30_0000_rank244_gmadl_directional_threshold_btc_keep_p1.md` 被正式 intake 为 `keep_P1`
- `2026-03-30_0029_rank244_survivor_followup_background.md` 完成唯一 follow-up 并回 `background/P0`

也就是说：
- 最新已消费的 fresh intake 仍是 `Rank 244`
- 但它已经收口，不再占前排
- 所以本轮要做的是 **指定新的 fresh intake**，而不是继续挂住 `Rank 244`

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且已经做完；结论是不升 `P2`。**

原因：
- `Rank 244` 的 decisive blocker 非常单一：`direction-aware loss` 是否真的留下独立于 `threshold abstain` 的成本后增量
- 这正符合 survivor 只给一次便宜诚实检查的定义
- follow-up 已直接给出出口答案：在同一 BTC 15m walk-forward、同一特征、同一 long/short/flat 状态机、保守 friction 下，direction-aware loss 只是放大预测幅度并显著增加交易，没有同步提升方向质量，因此 survivor 预算用尽后回 `background/P0`

所以答案是：
- **值得做**
- **已经做完**
- **做完后的结论是“不升 P2”**

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**当前不存在明确 `Active P2`。**

原因：
- `Active P2 slot.current_target = none`
- 最近一次 P2 出口仍是 `Rank 235`，并已在 `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md` 完成 `one-time P2 -> P1 re-scope`
- 之后没有新对象升入 `Active P2 slot`

因此这轮没有需要 bot2 直接裁定 `promote_P3 / P1 re-scope / P0` 的 active P2。

## 3) P3 兜底判断
本轮**不触发** bot2 的 `P2 -> P3` 兜底裁判。

原因很直接：
- `Paper launch queue = none`
- `Active P2 = none`
- 最近结果里没有出现“对象已经明显够格 paper trade / paper launch，但 bot3 还没升”的前排对象

所以这轮不能伪造一个 `P3` 或 `P2` 主线；诚实排班只能继续回到新的 intake。

## 4) rank 合规检查
- `Paper launch queue / connected_runner_live`：均有正式 rank
- `Fresh intake slot.current_target = none`
- `Surviving candidate slot.current_target = none`
- `Active P2 slot.current_target = none`

结论：**本轮无需补新的正式 Rank。**

## 5) 本轮 `cycle_plan` 为什么这样重写
按 policy 默认顺序扫描：
1. `P3 handoff`：无 queue 头，跳过
2. `P2 admission/promote/park`：无 active P2，跳过
3. `P1 survivor`：无 surviving candidate，跳过
4. `fresh intake`：成为本轮主任务，必须直接写具体对象
5. `P0 / background pool`：只保留证据，不单独占位

### 为什么不能继续重复最近几条
最近几个对象已经被写死或 blocked：
- `Rank 101`：`2026-03-30_0100` 已明确仍不是可独立 intake 的对象
- `Rank 28`：`2026-03-30_0117` 已明确仍只是更大 market-neutral family 提示
- `Rank 5`：`2026-03-30_0130` 已明确仍只是更大 double-clock family 提示
- `Rank 76`：`2026-03-30_0055` 已明确被 `Rank 201` 吸收
- `Rank 96` 的上一轮 conditional 也已被 `2026-03-30_0042` 写成不 distinct；如果再碰它，必须把主语进一步锁窄成 `short-side second-touch + candle-quality admission delay`，不能再按旧 conditional 写法重复一遍

因此这轮不能把 `101 / 28 / 5 / 76` 继续挂回 `cycle_plan` 充数。

### 为什么把 `Rank 4` 提到第 1 项
它是上一版 `cycle_plan` 唯一尚未执行的 pending 项，而且仍是最具体、最该先被回答的一条合法 intake：
- 主语够窄：`threshold-governed pairs family residual`
- 上一轮已被诚实排入，但 bot3 尚未执行
- 相比直接跳去别的新对象，先把已在当前轮里的 pending intake 收口，更符合“已有具体可执行动作优先”的排班纪律

### 为什么补 `Rank 64`
`Rank 64` 不是泛 long-side quality，而是已经在 `2026-03-29_0703_rank64-park-reframe.md` 被明确 draft 成：
- `long-side-only hold-quality admission score`
- 只服务 `Fib retest_hold / EMA continuation`
- 不再偷带 shared gate / breakout_short

它比 `Rank 101` 更接近一个真正可 intake 的窄对象，因此排第 2。

### 为什么补 `Rank 96`
`Rank 96` 虽然上轮 conditional 被否，但 residual 并未完全死掉；当前唯一合法重问方式是把主语进一步锁成：
- `short-side only second-touch + candle-quality admission delay`

也就是明确承认：
- 不能再按 generic `retestCount>=2` 重写
- 不能镜像到 long 侧
- 不能偷换成更大 failure/followthrough 家族

若这条更窄主语仍不成立，也该把它彻底写回 `park_reframe`，不再反复占预算。

### 为什么补 `Rank 21`
`Rank 21b` 是已 drafted 的低频 overlay 方向：
- 从原 `15m market risk-on/off gate` 降级为 `daily sentiment-extremity shared risk overlay`
- 主语已经比原 rank 诚实得多
- 也与当前前三项不重复

它适合作为本轮第 4 条 intake：若前面几条都仍未能长成对象，`Rank 21b` 至少能回答“低频情绪极值 overlay 是否足够独立成一条 queue-facing 对象”。

## 6) 已写回 runtime truth
本轮已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan` 为 4 个具体 `pending` 小点：
1. `Rank 4 park residual -> threshold-governed pairs family residual`
2. `Rank 64 park residual -> long-side-only hold-quality admission score`
3. `Rank 96 park residual -> short-side second-touch plus candle-quality admission delay`
4. `Rank 21 park residual -> daily sentiment-extremity shared risk overlay`

全部满足：
- 每项只写 `target / action / success_criterion / result / status`
- 新生成项 `result = none`
- 新生成项 `status = pending`

## 7) 一句话结论
这轮已经没有 `P3 / P2 / survivor` 前排主线可收口；最诚实的 bot2 动作不是再重复已经写死的 `Rank 101 / 28 / 5 / 76 / 244`，而是把尚未真正执行、且仍有合法空间的 intake 重新排成：**先收掉 `Rank 4`，再看 `Rank 64 / Rank 96 / Rank 21` 能不能长成新的 queue-facing 对象。**
