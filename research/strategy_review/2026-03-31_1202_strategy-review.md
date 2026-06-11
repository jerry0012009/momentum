# 2026-03-31 12:02 UTC strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 重排；只读取 runtime state、repo 状态、最近 `research/optimization_loop/` 与最近 `research/strategy_review/`，不反向改 policy，不把 background pool 旧候选拉回前排。

## 只回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 结论：**否。**
   - 证据：`BOT2_BOT3_STATE.md` 仍写明 `Paper launch queue.current_target: none`；当前只有 `Rank 200 / 201 / 213 / 229` 在 `connected_runner_live`，没有新的待接线 queue 头。

2. **本轮 `fresh intake` 是什么？**
   - 结论：本轮最近一条已正式写回 runtime 的 fresh intake 仍是 **`Rank 267 / crypto factor momentum × size/vol rotation`**。
   - 证据：`research/optimization_loop/2026-03-31_0915_rank267_crypto_factor_momentum_sizevol_rotation_intake_keep_p1.md` 完成首判，随后 `2026-03-31_0946_rank267_survivor_followup_promote_p2.md` 用掉 survivor follow-up 并把它升入 `Active P2`；因此当前 fresh intake 仍应回答 Rank 267，而不是把尚未正式 intake 的新 digest 硬写成当前 intake。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 结论：**值得，而且已经用完且兑现成 `promote_P2`。**
   - 证据：`Rank 267` 的唯一 survivor follow-up 已执行完成；在 Binance perp 当前高流动 universe、4h 横截面换仓与单边 10bps 成本下，`short-horizon momentum` 与 `size` sleeves 已给出明确成本后净边，`low-vol` 未见 fatal flaw，而基于 sleeve 自身近窗 PnL 的 `winner rotation` 进一步把最佳组合提升到约 `+174.82 bps/period`，因此它不是“follow-up 后继续停留 P1”，而是已经诚实收口成 `promote_P2`。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 结论：**存在。当前明确 `Active P2` 是 `Rank 267`，它离的最近出口是 `P1 / one-time re-scope`，不是 `P3`。**
   - 证据：
     - `2026-03-31_1044_rank267_p2_cross_asset_blocker_alt_pocket.md` 已证明：`leave-one-out` 仍为正，但 `BTC / ETH / SOL` majors 单独拆开几乎不赚钱，当前净边主要由 `ex-majors alt basket` 支撑。
     - `2026-03-31_1134_rank267_p2_time_stability_passed_but_cross_asset_blocker_remains.md` 又证明：时间维度过关，不是只靠最近窗口幻觉。
     - 因而它不是直接该掉到 `P0` 的坏对象；但在 desk review 层面，也还没到“足够值得直接 paper launch”的程度。当前最诚实的最近出口，是把 `P2` 收口成一次性明确判断：若 `parameter + honesty` 没暴露致命缺口，则优先考虑按 **`ex-majors alt basket` 明确 re-scope** 回 `P1`，而不是带着未解决的 majors blocker 直接硬推 `P3`。

## rank / 前排合法性检查

- `Paper launch queue`: `none`
- `Fresh intake slot`: `Rank 267`，已有正式 rank
- `Surviving candidate slot`: `none`
- `Active P2 slot`: `Rank 267`，已有正式 rank
- 结论：**本轮无需补 rank。**

## repo / recent evidence quick notes

- `git status --short --branch` 显示 repo 有大量未跟踪产物；本轮只把它视为最近研究活动背景，不据此改 policy，也不据此把旧对象拉回前排。
- 最近 optimization 最关键的三条证据：
  - `2026-03-31_0946_rank267_survivor_followup_promote_p2.md`
  - `2026-03-31_1044_rank267_p2_cross_asset_blocker_alt_pocket.md`
  - `2026-03-31_1134_rank267_p2_time_stability_passed_but_cross_asset_blocker_remains.md`
- 最近 strategy review 最新文件是 `2026-03-31_0955_strategy-review.md`；当时仍把 `Rank 267` 理解为更靠近 `P3`。现在新增的 cross-asset blocker 证据已改变出口排序，本轮必须把 state 改写到“出口决策轮”，不能继续沿用开放式 `keep_P2`。

## 为什么本轮不触发 bot2 的 `P2 -> P3` 兜底直推

policy 说得很清楚：如果 desk review 已经清楚表明对象足够值得进入 paper trade / paper launch，而 bot3 没升，bot2 必须直接写入 `P3 / handoff`。本轮我专门对 `Rank 267` 检查了这一条，结论是：**还不够。**

- 支持它继续留在前排、而不是掉回背景的证据已经足够：
  - survivor replication 成立；
  - `time stability` 也成立；
  - 不是单一币幻觉。
- 但阻止它被直接兜底升 `P3` 的证据同样明确：
  - `majors` 自身不成立；
  - 当前净边主要由 `ex-majors alt basket` 支撑；
  - 这意味着当前对象还没有通过“更干净、更可承载资产子集也站得住”的门槛。

因此，bot2 本轮不能把它继续拖成第三次开放式 `keep_P2`，也不能假装 blocker 不存在直接硬升 `P3`。最诚实的做法是：**先把 `parameter + honesty` 补成最后一个 admission 小点，然后立刻做单轮出口决策。**

## cycle_plan 重排结论

按 policy 默认顺序扫描合法动作：
1. `P3 handoff`：无待接线 queue 头
2. `P2 admission/promote/park`：有，而且唯一合法对象就是 `Rank 267`
3. `P1 survivor`：无
4. `fresh intake`：只能作为条件式补位，排在 `Rank 267` 出口收口之后

因此本轮把 `cycle_plan` 重写为：
1. `Rank 267`：做合并版 `parameter + honesty` admission
2. `Rank 267`：立即进入 **P2 出口决策轮**，只许在 `promote_P3 / one-time P2->P1 re-scope / drop_to_background` 中三选一
3. `anchor-low reversal gate`：作为条件式 fresh intake
4. `dynamic boundary RL pairs`：作为第二个条件式 fresh intake

## writeback

- 已更新：`docs/BOT2_BOT3_STATE.md`
- 更新内容：
  - 保持前排槽位不变；
  - 把旧的开放式 `keep_P2` 尾项重写为 **最终 admission + 出口决策轮**；
  - 按 policy 为“2 次连续 keep_P2 后的下一轮”保留条件式 fresh intake 补位。
- 未改写：policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 本轮未触发 `P2 -> P3` 兜底直推，因为现有 desk review 证据尚不足以诚实宣称 `Rank 267` 已经达到 paper launch 门槛
