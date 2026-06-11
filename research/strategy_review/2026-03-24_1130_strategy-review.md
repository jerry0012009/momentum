# Strategy Review (bot2)

Time: 2026-03-24 11:30 UTC

## 本轮一句话判断
当前前排仍只有 `Rank 154 / Crypto-Stat-Arb` 这一条 `Active P2`；`Paper launch queue` 为空、`Surviving candidate` 为空且上一条 fresh intake 的唯一一次 follow-up 已兑现并升到 `P2`，所以本轮主资源继续放在 `P2 exit decision`，并且不得再沿 `time / honesty` 轴追加第三次开放式 `keep_P2`。

## 1) 必检输入

### Policy / state 先读结论
- policy 仍要求固定按 `P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0` 排班。
- 当前 runtime state 显示：
  - `Paper launch queue = none`
  - `Fresh intake slot` 最近一条仍是 `ryanczm/Crypto-Stat-Arb`，已正式分配 `Rank 154`
  - `Surviving candidate slot = none`，唯一一次 follow-up 已在 2026-03-24 09:50 UTC 用完并把对象升到 `P2`
  - `Active P2 slot = Rank 154 / Crypto-Stat-Arb`
  - `p2_consecutive_keep_p2 = 2`，且最新 evidence axis 为 `honesty / execution realism`

### Repo 状态
- repo 仍然很脏，但 desk review 只把它当作 evidence 背景，不据此反向改 policy。
- 本轮只更新 `docs/BOT2_BOT3_STATE.md`，不改 policy / brief / operating card / auto loop / cron prompt。

### 最近 `research/optimization_loop/`
按时间倒序读取到的关键结果：
1. `2026-03-24_1046_crypto-stat-arb-p2-honesty-execution.md`
   - `Rank 154` 在把权重与 funding 统一滞后 1 日后，`combined` 仍保持明显正边。
   - 但边际对 `trade_buffer≈5%` 的低换手实现较敏感，因此结论仍是 `keep_P2`。
2. `2026-03-24_1018_crypto-stat-arb-p2-time-stability.md`
   - 跨年与季度切片显示有真实负段，尤其 2022 不平滑。
   - 但并未把正边打穿，结论仍是 `keep_P2`。
3. `2026-03-24_0950_crypto-stat-arb-followup-promote-p2.md`
   - 上一条 fresh intake 的唯一一次 follow-up 已兑现，而且是有效 follow-up：直接把对象从 `P1` 升到 `P2`。
4. `2026-03-24_0922_crypto-stat-arb-fresh-intake.md`
   - 当前最新 fresh intake 就是 `ryanczm/Crypto-Stat-Arb`。
5. 更早的 `term-structure calendar-spread`、`nfi`、`chanpy-framework` 都已 park；无 reopen 授权，不能自动回前排。

### 最近 `research/strategy_review/`
1. `2026-03-24_1119_strategy-review.md`
   - 已把主资源继续放在 `Rank 154` 的 `P2 admission close-out`。
2. `2026-03-24_1117_strategy-review.md`
   - 同样保持前排只围绕 `Rank 154` 收口，没有违规把 background pool 拉回前排。

结论：当前排班连续性正常；09:22 fresh intake，09:50 唯一 follow-up 升 `P2`，10:18 与 10:46 连续补 time + honesty，因此现在唯一该收口的是 `P2 admission` 的出口判断，而不是回头拉旧候选，也不是直接把主资源切回 fresh intake。

## 2) 只回答 4 个问题

### Q1. `Paper launch queue` 是否非空？
- **否，仍为空。**
- 证据：`BOT2_BOT3_STATE.md` 中 `Paper launch queue.current_target = none`，且最新两条 P2 admission 结果都只是 `keep_P2`，没有任何对象升到 `P3`。

### Q2. 本轮 `fresh intake` 是什么？
- **`ryanczm/Crypto-Stat-Arb`，即现在的 `Rank 154`。**
- 证据：`Fresh intake slot.latest_result` 与 `source_record` 仍指向 `research/optimization_loop/2026-03-24_0922_crypto-stat-arb-fresh-intake.md`；它是最近一条真正进入当前运行槽位的 fresh intake。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且已经用掉，并且用得对。**
- 证据：`research/optimization_loop/2026-03-24_0950_crypto-stat-arb-followup-promote-p2.md` 明确显示这次 follow-up 不是无效补测，而是直接把对象从 `keep_P1` 推进到 `P2`。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **存在，就是 `Rank 154 / Crypto-Stat-Arb`。**
- **它当前离 `P3` 最近，但尚未过线。**
- 原因：
  - 最新两条 admission 结果都指向 `keep_P2`，没有出现明确的 re-scope / re-spec 方向，因此当前不满足 `P2 -> P1` 条件。
  - honesty 检查没有把它打穿到 `P0`；更诚实的结论仍是“保留在 admission 层”。
  - 剩余问题已经收缩到 exit decision：优先用 `effectiveness / cross-asset / parameter` 收口，再决定 `P3` 还是 `P0`。

## 3) rank 合规检查
- 本轮前排对象只有 `Rank 154 / Crypto-Stat-Arb`。
- `Paper launch queue` 为空；`Surviving candidate slot` 为空；`Active P2 slot` 已带正式 rank。
- **因此本轮不需要补发新的 Rank。**

## 4) 本轮 cycle_plan 重排（authoritative）
按 policy 默认顺序，当前真实可执行动作是：
1. **P2 exit decision**：围绕 admission 剩余缺口优先收口 `effectiveness / cross-asset / parameter`，并直接回答 `promote_P3 / drop_to_background / one-time P2->P1 re-scope`。
2. **P3 conditional handoff**：仅当 Run 1 直接升 `P3` 时才接线。
3. **fresh intake conditional reopen**：由于当前 `P2` 已出现 2 次连续 `keep_P2`，仍保留 1 个 conditional fresh intake 小点，但只在 Run 1 没有形成更高层级或明确 park 时切回。

因此本轮已将 `BOT2_BOT3_STATE.md` 的 `cycle_plan` 重写为：
1. `Active P2 slot（Rank 154 / Crypto-Stat-Arb）`：做最小 `P2 exit decision`，优先围绕 `effectiveness / cross-asset / parameter` 收口；不得重复 `time / honesty` 轴，也不得再产出第三次开放式 `keep_P2`。
2. `Paper launch queue（conditional handoff）`：若 Run 1 升 `P3`，立即整理最小 handoff。
3. `Fresh intake slot（conditional reopen）`：若 Run 1 未把 `Rank 154` 推到 `P3` 或明确 park，则下一轮默认优先切回新的 fresh raw alpha / repo。

## 5) 本轮实际改动
- 更新：`/root/clawd/jerry/momentum/docs/BOT2_BOT3_STATE.md`
  - 只重写当前轮 `cycle_plan`
  - 未改 policy / brief / operating card / auto loop / cron prompt
- 新增：`/root/clawd/jerry/momentum/research/strategy_review/2026-03-24_1130_strategy-review.md`

## 6) 一句话结论
**当前桌面主线还不是 fresh intake，而是 `Rank 154 / Crypto-Stat-Arb` 的 `P2 exit decision`；它目前最接近的出口仍是 `P3`，但下一刀必须换到 `effectiveness / cross-asset / parameter` 收口，不能再沿已有 `time / honesty` 轴拖成第三次开放式 `keep_P2`。**
