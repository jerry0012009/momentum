# Strategy Review (bot2)

Time: 2026-03-30 09:40 UTC

## 本轮一句话判断
`Paper launch queue` 当前为空；本轮 `fresh intake` 是刚完成首判并进入 survivor 的 `Rank 250 / pseudosession open leader continuation`；它值得且必须先用掉那唯一一次 survivor follow-up；当前没有 `Active P2`，因此本轮默认排班应先收口 `Rank 250`，再切回新的 `fresh intake`（先看最新的 `intraday hour-pair momentum / reversal`，再看 `trend continuation × pullback re-entry × correlation-budget shell` 与 `same-expiry box spread implied-rate 偏离`）。

## 1) 读取顺序与边界
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-30_0935_rank250_pseudosession_open_leader_continuation_intake_keep_p1.md`
  - `2026-03-30_0908_rank249_survivor_followup_background_p0.md`
  - `2026-03-30_0850_trend_pullback_correlation_shell_intake_blocked_by_rank249_survivor_lock.md`
  - `2026-03-30_0830_rank249_network_leaderbasket_follower_routing_intake_keep_p1.md`
- 最近 `research/strategy_review/`：
  - `2026-03-30_0859_strategy-review.md`
  - `2026-03-30_0722_strategy-review.md`
- 为本轮 intake 排班额外核对：
  - `research/quant_digests/2026-03-30_0929_intraday-hourpair-momentum-reversal-alpha.md`
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

因此当前没有需要 bot2/bot3 抢占预算的 `P3 launch wiring` 头部对象。

### Q2. 本轮 `fresh intake` 是什么？
**当前 runtime 里的 `fresh intake` 是 `Rank 250 / pseudosession open leader continuation`。**

原因：
- `BOT2_BOT3_STATE.md` 的 `Fresh intake slot.current_target` 已写成 `Rank 250`
- `2026-03-30_0935_rank250_pseudosession_open_leader_continuation_intake_keep_p1.md` 已把它正式判成 `keep_P1`
- 因为它是最近一条 fresh intake，且已进入 `Surviving candidate slot`，所以在 survivor 收口前，它仍是当前前排链条的核心对象

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得。**

而且这一次 follow-up **还没被执行掉**。

证据：
- `Rank 250` 首轮 verdict 已经清楚回答了“它是不是旧 clock/open continuation 的泛改写”——答案是否；当前新意被锁定为 `00/08/16 UTC pseudo-session` 开头 `30m` 里 `dominant leader 自身继续领跑`
- 首轮最关键的新信息是：broad 同向版本成本后为负，但 `leader>=50bps + spread_to_runner>=40bps` 的稀疏 pocket 在 Binance perp `15m` quick check 里仍留下 `12/24/30 bars` 约 `+2.34/+8.96/+16.16 bps/trade` 的 after-cost 空间
- 但它还没经过真正 admission；当前证据仍主要来自 quick check，尚未回答这条 leader continuation 在 rolling / OOS、perp / after-cost 口径下是否仍保有稳定 pocket

所以它完全符合 policy 对 survivor 的定义：只做一次最小 decisive follow-up，直接回答这条线在更诚实口径下是 `promote_P2` 还是 `background/P0`。

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
1. 先收口 `Rank 250` 的 survivor
2. 再切回新的 `fresh intake`

## 4) rank 合规检查
前排槽位检查：
- `Paper launch queue.current_target = none`
- `Fresh intake slot.current_target = Rank 250`
- `Surviving candidate slot.current_target = Rank 250`
- `Active P2 slot.current_target = none`

其中唯一前排对象 `Rank 250` 已有正式 rank，因此：
**本轮不存在“前排对象达到 keep_P1/P2/P3 但无正式 rank”的违规情况，无需补号。**

## 5) 为什么必须重写 `cycle_plan`
上一版 `cycle_plan` 已被最新结果实质性消费：
- `Rank 249` survivor 已完成并回到 `background/P0`
- `Rank 250` fresh intake 已完成并进入 survivor
- 旧计划中的 `pseudosession open leader continuation` 已不再是未决 fresh intake，而是当前 survivor

按 policy 的 authoritative priority ladder：
1. `P3 handoff`：无
2. `P2 admission/promote/park`：无
3. `P1 survivor`：有，而且就是 `Rank 250`
4. 只有把 survivor 诚实排在前面后，才能用剩余预算补新的 `fresh intake`

因此本轮必须把 `Rank 250` survivor follow-up 提到第 1 位，再依次排最近的新报告对象。

## 6) 本轮新的 `cycle_plan` 为什么这样排
### 第 1 项：`Rank 250 / pseudosession open leader continuation`
原因：
- 它是唯一合法 survivor
- policy 明确要求 survivor 的唯一 follow-up 在诚实收口前享有前排锁定权
- 当前 blocker 非常具体：`spread_to_runner` 阈值与 `12/24/30 bars` 持有窗在 rolling / OOS、perp / after-cost 口径下是否仍留下 stable pocket
- 这一步做完后，才能诚实决定是 `promote_P2` 还是 `background/P0`

### 第 2 项：`intraday hour-pair momentum / reversal within pseudo trading day`
原因：
- 这是当前最新的量化 digest（`2026-03-30_0929`）
- 与已有 clock/open 家族相比，它新增的核心边界不是泛时钟效应，而是 `same pseudo trading day` 里 `earlier hour -> later hour` 的 `continuation + reversal` 共存的 hour-pair pocket
- 这条线本身提供的是 raw alpha 主体，不是已有策略的边角 gate，因此值得在 survivor 之后占据下一个 fresh intake 槽位

### 第 3 项：`trend continuation × pullback re-entry × correlation-budget shell`
原因：
- 仍属最近的新 repo 报告
- 它的独立性不在“趋势继续涨”本身，而在 `correlation-budget shell` 这层完整组合外壳是否构成单轮可证伪的新对象
- 它上轮只是因 survivor lock 未能落地，不是因为对象本身已失去审理价值

### 第 4 项：`same-expiry box spread implied-rate 偏离`
原因：
- 仍属最近新 alpha 报告，优先级高于 park_reframe 残余
- honesty blocker 很具体：coin-margined unit normalization + executable bid/ask
- 很适合做一次硬 first verdict：要么确认是值得前排的 options RV raw alpha，要么直接判成 mid 幻觉

## 7) 本轮写回的 runtime 变更
已重写 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan` 为 4 个新的 pending 小点：
1. `Rank 250 / pseudosession open leader continuation`
2. `intraday hour-pair momentum / reversal within pseudo trading day`
3. `trend continuation × pullback re-entry × correlation-budget shell`
4. `same-expiry box spread implied-rate 偏离`

全部新项均满足：
- 每项只写 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`
- 没有保留空泛或已被最新结果消费掉的旧占位

## 8) repo 状态备注
`git status --short` 仍显示大量未跟踪产物与临时文件；本轮只把它当作环境证据读取，没有把“文件很多 / 日志很多”误当成排班理由。

## 9) 一句话结论
这轮没有 `P3`、没有 `Active P2`，但有一个必须先诚实收口的 survivor：`Rank 250`。因此 bot3 下一轮最该做的，不是继续翻旧 residual，也不是在 survivor 未收口前硬塞新的 `keep_P1`，而是先用掉 `Rank 250` 那唯一一次 decisive follow-up；只有做完这步，才轮到最新的 `intraday hour-pair momentum / reversal`、以及 `trend continuation × pullback × correlation-budget shell`、`same-expiry box spread implied-rate` 这些新的 intake。
