# Strategy Review (bot2)

Time: 2026-03-30 08:59 UTC

## 本轮一句话判断
`Paper launch queue` 仍为空；本轮 `fresh intake` 是刚刚完成 first verdict 的 `Rank 249 / leader-basket → selected-follower spread catch-up / network follower routing`；它作为上一条 fresh intake **值得且必须先用掉** 那唯一一次 survivor follow-up；当前不存在 `Active P2`，因此本轮默认排班应先收口 `Rank 249`，再切回新的 intake（`pseudosession open leader continuation`、`trend continuation × pullback re-entry × correlation-budget shell`、`same-expiry box spread implied-rate 偏离`）。

## 1) 读取顺序与边界
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-30_0850_trend_pullback_correlation_shell_intake_blocked_by_rank249_survivor_lock.md`
  - `2026-03-30_0830_rank249_network_leaderbasket_follower_routing_intake_keep_p1.md`
  - `2026-03-30_0817_btc_directional_threshold_intake_blocked_duplicate_of_rank244.md`
  - `2026-03-30_0734_rank248_survivor_followup_background_p0.md`
  - `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md`
- 最近 `research/strategy_review/`：
  - `2026-03-30_0722_strategy-review.md`
- 为本轮排班额外核对的最近 digest / intake 线索：
  - `research/quant_digests/2026-03-30_0844_pseudosession-open-leader-continuation-alpha.md`
  - `research/quant_digests/2026-03-30_0808_network-leaderbasket-follower-routing-alpha.md`
  - `research/quant_digests/2026-03-29_2242_trend-pullback-correlation-shell-alpha.md`
  - `research/quant_digests/2026-03-29_2218_coinmargined-boxspread-rate-alpha.md`

硬约束遵守：
- 只更新 `docs/BOT2_BOT3_STATE.md`
- 未改 policy / brief / operating card / auto loop / cron prompt
- 未自动把 background pool 旧候选拉回前排
- `docs/TODO.md` 未作为本轮排班依据
- 当前前排对象不存在无 rank 的 `keep_P1/P2/P3`，因此本轮无需补 rank

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否。**

runtime 仍是：
- `current_target = none`
- `connected_runner_live = Rank 200 / Rank 201 / Rank 213 / Rank 229`

所以当前没有需要 bot2/bot3 抢占预算的 `P3 launch wiring` 头部对象。

### Q2. 本轮 `fresh intake` 是什么？
**当前 runtime 里的 `fresh intake` 是 `Rank 249 / leader-basket → selected-follower spread catch-up / network follower routing`。**

原因：
- `BOT2_BOT3_STATE.md` 的 `Fresh intake slot.current_target` 已写成 `Rank 249`
- `2026-03-30_0830_rank249_network_leaderbasket_follower_routing_intake_keep_p1.md` 已把它正式判成 `keep_P1`
- 因为它是最近一条 fresh intake，且已进入 `Surviving candidate slot`，所以在 survivor 收口前，它仍是当前前排链条的核心对象

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

而且这一次 follow-up **还没被执行掉**。

证据：
- `Rank 249` 首轮 verdict 已经清楚回答了“它是不是旧 cross-crypto lead-lag 的泛重述”——答案是否；当前新意被锁定为 `leader basket 先动 + pair-specific follower routing 的下一根 spread catch-up`
- 首轮最关键的新信息是：equal-weight follower basket 几乎没边，但 `LINK/ADA/XRP` 这类 selected-follower pockets 仍有 edge，这说明对象边界确实来自 `routing`，不是泛 alt basket catch-up
- 但它还没经过真正 admission；当前证据仍主要来自 spot `15m` pocket scan，尚未回答 `rolling routing + perp executable + after-cost` 下是否还有可执行 pocket

所以它完全符合 policy 对 survivor 的定义：只做一次最小 decisive follow-up，直接回答这条 routing 线在更诚实口径下是 `promote_P2` 还是 `背景收口`。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**不存在。**

runtime 明确写着：
- `Active P2 slot.current_target = none`

最近一次活跃 P2 仍是 `Rank 235`，但它已在 `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md` 被执行成一次性的 `P2 -> P1 re-scope`，不再属于当前 `Active P2`。

## 3) P2 -> P3 兜底裁判是否触发
**不触发。**

因为：
- `Paper launch queue = none`
- `Active P2 = none`
- 最近材料里没有任何当前前排对象已经明显达到 `paper trade / paper launch` 门槛却还被 bot3 卡在 `P2`

所以本轮不能伪造一个 `P3` 或重开旧 P2；最诚实的动作仍是：
1. 先收口 `Rank 249` 的 survivor
2. 再切回新的 `fresh intake`

## 4) rank 合规检查
前排槽位检查：
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = Rank 249`
- `Surviving candidate slot.current_target = Rank 249`
- `Active P2 slot.current_target = none`

其中唯一前排对象 `Rank 249` 已有正式 rank，因此：
**本轮不存在“前排对象达到 keep_P1/P2/P3 但无正式 rank”的违规情况，无需补号。**

## 5) 为什么必须重写 `cycle_plan`
上一版 `cycle_plan` 已被最新结果实质性消费：
- `Rank 249` fresh intake 已完成并进入 survivor
- `trend continuation × pullback re-entry × correlation-budget shell` 在 `2026-03-30_0850_...blocked_by_rank249_survivor_lock.md` 中已被明示：因为 survivor lock，当前不能继续把它排成优先于 survivor 的动作
- 旧计划里带有 `blocked` 的占位，已经不符合“当前轮应只写具体值得做的任务”的要求

按 policy 的 authoritative priority ladder：
1. `P3 handoff`：无
2. `P2 admission/promote/park`：无
3. `P1 survivor`：有，而且就是 `Rank 249`
4. 只有把 survivor 诚实排在前面后，才能用剩余预算补新的 `fresh intake`

因此本轮必须把 `Rank 249` survivor follow-up 提到第 1 位，再依次排最近的新报告对象。

## 6) 本轮新的 `cycle_plan` 为什么这样排
### 第 1 项：`Rank 249 / leader-basket → selected-follower spread catch-up / network follower routing`
原因：
- 它是唯一合法 survivor
- policy 明确要求 survivor 的唯一 follow-up 在诚实收口前享有前排锁定权
- 当前 blocker 非常具体：`rolling routing + perp executable + after-cost` 下是否还留有 selected-follower pocket
- 这一步做完后，才能诚实决定是 `promote_P2` 还是 `background/P0`

### 第 2 项：`pseudosession open leader continuation`
原因：
- 这是最新的量化 digest（就在 `Rank 249` 之后）
- 与已有 clock / leader-lag 家族相比，它新增的核心边界是 `pseudo-session open` 这一特定时钟定义下的 leader continuation / follower participation，而不是泛 intraday continuation
- 在 survivor 后切回 intake 时，这条线比更早的旧候选更符合“最近新 repo/paper/alpha 报告优先”的规则

### 第 3 项：`trend continuation × pullback re-entry × correlation-budget shell`
原因：
- 仍属最近的新 repo 报告
- 它的独立性不在“趋势继续涨”本身，而在 `correlation-budget shell` 这层完整组合外壳是否构成单轮可证伪的新对象
- 它先前只是因为 survivor 锁定才被挡住，不是因为对象本身已失去审理价值

### 第 4 项：`same-expiry box spread implied-rate 偏离`
原因：
- 仍属最近新 alpha 报告，优先级高于 park_reframe 残余
- honesty blocker 很具体：coin-margined unit normalization + executable bid/ask
- 很适合做一次硬 first verdict：要么确认是值得前排的 options RV raw alpha，要么直接判成 mid 幻觉

## 7) 本轮写回的 runtime 变更
已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan` 为 4 个新的 pending 小点：
1. `Rank 249 / leader-basket → selected-follower spread catch-up / network follower routing`
2. `pseudosession open leader continuation`
3. `trend continuation × pullback re-entry × correlation-budget shell`
4. `same-expiry box spread implied-rate 偏离`

全部新项均满足：
- 每项只写 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`
- 没有再保留空泛或已知被 survivor lock 挡住的占位句子

## 8) repo 状态备注
`git status --short` 仍显示大量未跟踪产物与临时文件；本轮只把它当作环境证据读取，没有把“文件很多 / 日志很多”误当成排班理由。

## 9) 一句话结论
这轮没有 `P3`、没有 `Active P2`，但有一个必须先诚实收口的 survivor：`Rank 249`。因此 bot3 下一轮最该做的，不是继续翻旧 residual，也不是在 survivor 未收口前硬塞新的 `keep_P1`，而是先用掉 `Rank 249` 那唯一一次 decisive follow-up；只有做完这步，才轮到 `pseudosession open leader continuation`、`trend continuation × pullback × correlation-budget shell`、`same-expiry box spread implied-rate` 这些新的 intake。
