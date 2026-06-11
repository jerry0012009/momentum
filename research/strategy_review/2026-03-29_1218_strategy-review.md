# Strategy Review (bot2)

Time: 2026-03-29 12:18 UTC

## 本轮一句话判断
`Paper launch queue` 仍为空；本轮前排已经切换为 `Rank 235` 的 `Active P2 admission` 与 `Rank 236` 的 `fresh intake` 首判。`Rank 235` 当前离 `P3` 最近，但最新 desk review 还不足以直接越级写成 `P3 / Paper launch queue`，所以本轮最诚实的动作是把它排成出口导向的两步 admission，而不是继续开放式研究。

## 1) 已读材料与边界核对
先读：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

再读：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short`
- 最近 `research/optimization_loop/`：
  - `2026-03-29_1215_rank235_survivor_followup_promote_p2.md`
  - `2026-03-29_1153_rank234_p2_exit_rescope_to_p1_small_cap_pocket.md`
  - `2026-03-29_1140_rank234_p2_cross_asset_leave_one_out_fail.md`
  - `2026-03-29_1033_rank236_rank86b_distinctness_turn_into_fresh_intake.md`
- 最近 `research/strategy_review/`：
  - `2026-03-29_1128_strategy-review.md`
  - `2026-03-29_0947_strategy-review.md`

硬约束遵守：
- 只更新了 `docs/BOT2_BOT3_STATE.md`
- 未改写 policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- `docs/TODO.md` 未参与本轮排班
- 当前前排对象都有正式 `Rank`，无需补 rank

## 2) 只回答 4 个问题
### Q1. `Paper launch queue` 是否非空？
**否，当前 queue 头为空。**

细节：
- `current_target: none`
- `connected_runner_live` 里已有 `Rank 200 / 201 / 213 / 229`
- 最近没有新的待接线对象被推入 queue 头

所以本轮没有合法的 `P3 launch wiring` 优先项，不能拿空槽确认占用轮次。

### Q2. 本轮 `fresh intake` 是什么？
**`Rank 236 / breakout-short-specific short-side admission score-veto`。**

原因：
- `2026-03-29_1033_rank236_rank86b_distinctness_turn_into_fresh_intake.md` 已把 queue-only 的 `Rank 86b` 正式转成新对象 `Rank 236`
- 它不是重开旧 `Rank 86`，而是把唯一剩下值得测的 claim 收窄成：
  - `breakout-short` 专用
  - `short-only`
  - `penetration / ATR` admission score-veto

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
**值得，而且那次唯一 follow-up 已经完成并把对象推进到 `P2`。**

上一条 fresh intake 是：
- `Rank 235 / richest-venue routing × hysteresis funding carry`

根据 `2026-03-29_1215_rank235_survivor_followup_promote_p2.md`：
- repo 的 `strategy_cross.py` 先用 `best_fr=max(venues)` 改写底层 funding cashflow
- notebook 已给出 `Binance-only net -10.0%` 对 `Cross-exchange net +27.8%` 的符号翻转
- 因而独立主增量首先来自 `richest-venue routing`，而不是单靠 hysteresis 降 churn

所以这次 follow-up 是高杠杆、而且已经诚实收口；对象不再停留在 survivor 槽位。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
**存在：`Active P2 = Rank 235 / richest-venue routing × hysteresis funding carry`；它当前离 `P3` 最近。**

原因：
- `Rank 234` 已在 `2026-03-29_1153` 被做成一次性 `P2 -> P1 re-scope`，不再是 active P2
- `Rank 235` 已经通过 survivor 轮回答了最关键问题：主增量来自 routing，而非仅是 exit-layer 降 churn
- 因此它不是更靠近 `P1/P0` 的早期模糊候选，而是已经进入 admission 的前排对象
- 但当前还缺出口所需的更窄证据：
  - `routing-only` 与 `routing+hysteresis` 的统一表
  - 跨资产 / 跨 venue regime 分布
  - quoted funding 到 realized carry 的 honesty / execution 审计

所以它**最近的出口是 `P3`**，但**还没达到 bot2 直接兜底升 `P3` 的门槛**。

## 3) rank 合规检查
- `Paper launch queue / connected_runner_live`：`Rank 200 / 201 / 213 / 229` 都有 rank
- `Fresh intake slot`：`Rank 236` 已有 rank
- `Surviving candidate slot`：当前 `none`
- `Active P2 slot`：`Rank 235` 已有 rank

结论：**本轮无需补新的整数 `Rank`。**

## 4) 为什么这轮没有把 `Rank 235` 直接改写进 `P3 / Paper launch queue`
policy 要求：如果 desk review 已清楚表明对象已经足够值得进入 paper trade / paper launch，而 bot3 还没升，bot2 必须直接升。

本轮我专门核对了这个条件，结论是：**还没到那一步。**

当前最新证据只足够说明：
- 主 alpha 确实来自 `richest-venue routing`
- `hysteresis/min_hold` 更像执行层净化器，而非 primary source
- 对象因此值得从 survivor 升到 `P2`

但还不够说明：
- `routing-only` 在多币、多 venue regime 下已经稳定到足以 paper launch
- quoted funding uplift 能较诚实地兑现成 realized carry
- 没有明显 execution / honesty 致命问题

因此本轮不能假装它已经满足 `P3` 门槛；最诚实的动作是把它排成**出口导向 admission 轮**，并要求下一轮直接回答 `promote_P3 / one-time P2->P1 re-scope / drop_to_background`。

## 5) 本轮 `cycle_plan` 重写
按 policy 默认顺序重排后，当前轮次写成：
1. `Rank 235`：`effectiveness / cross-asset`
2. `Rank 235`：`time / parameter / honesty`，直接做出口判断
3. `Rank 236`：fresh intake 首判
4. `simple-feature XS long-leg crypto ML alpha`：conditional fresh intake，只做“是否值得正式 intake”的对象边界判断

这样排的原因：
- 没有 `P3 queue` 头可做
- 有明确 `Active P2`，所以必须先收口 `Rank 235`
- 没有 survivor 槽位动作
- `Rank 236` 是当前 fresh intake，必须保留在 `P2` 收口之后
- 第 4 项只作为前排动作已诚实排入后的 conditional intake，不抢前排对象顺序

## 6) 对 runtime truth 的实际写回
已更新 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan`：
- 去掉已完成的 `Rank 234` / survivor 历史小点
- 把当前轮次切换到 `Rank 235` 两步 admission + `Rank 236` first verdict + 1 个 conditional fresh intake

其余槽位未改：
- `Paper launch queue`：仍为 queue 头为空
- `Fresh intake slot`：仍是 `Rank 236`
- `Surviving candidate slot`：仍为 `none`
- `Active P2 slot`：仍是 `Rank 235`

## 7) 一句话结论
这轮真正该盯的不是旧的 `Rank 234`，而是新晋 `Active P2` 的 `Rank 235`：它已经离 `P3` 最近，但还差最后一轮出口导向 admission；在这之前，不该偷懒把它硬写进 `P3`，也不该继续把它拖成开放式研究。