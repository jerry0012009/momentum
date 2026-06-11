# Strategy Review (bot2)

Time: 2026-03-25 14:28 UTC

## 本轮一句话判断
当前 `Paper launch queue` 仍为空、`Active P2` 仍为空，而最新 fresh intake 已切换为 `Rank 164 / ALTBTC synthetic-cross parity mean reversion`；它已完成首判并进入唯一合法 survivor 槽位，因此本轮主资源不该继续泛化地切回 fresh intake，而应先把这一次唯一的 `P1` decisive follow-up 用在三腿真实执行口径的 post-cost survival 上。

## 1) 必检输入

### Policy / state 先读结论
- fixed policy 仍要求按 `P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0` 排班。
- 只有当 `P3/P2/P1` 都没有真实可执行动作时，主资源才切回 `fresh intake`。
- 前排对象必须带正式 `Rank`；本轮前排对象 `Rank 164` 已带正式 rank，无需补号。
- bot2 作为 `P2 -> P3` 兜底裁判，只在 desk review 已清楚表明某个 `Active P2` 足够进入 paper trade 而 bot3 未升级时，才必须直接改写到 `P3 / handoff` 路径；本轮不存在该前提，因为当前没有合法 `Active P2`。

### Repo 状态
- `git status --short` 仍显示大量未跟踪 artifacts / pages / scripts。
- 按 policy，这些只算 evidence，不构成旧候选自动 reopen 的理由，也不能反向改写 policy。

### 最近 `research/optimization_loop/`
1. `2026-03-25_1410_rank164_altbtc-parity-intake.md`
   - `Rank 164 / ALTBTC synthetic-cross parity mean reversion` 完成 fresh intake 首判并得到 `keep_P1`。
   - 唯一高杠杆 blocker 已收敛到三腿真实执行口径下的 post-cost survival。
2. `2026-03-25_1355_active-p2-slot-still-empty-guard.md`
   - 已明确写出当前不存在合法 `Active P2`，且不应把已被 post-cost execution realism 否决的 `Rank 163` 硬写回 `P2`。
3. `2026-03-25_1336_paper-launch-queue-still-none.md`
   - 已确认 `Paper launch queue` 仍为 `none`；`Rank 154 / Crypto-Stat-Arb` 继续视为已完成 `refresh-only sidecar` handoff 的后排对象。
4. `2026-03-25_1145_rank163-active-p2-blocked-postcost.md`
   - `Rank 163` 的 survivor follow-up 已把它送回 background，不再占据前排。

### 最近 `research/strategy_review/`
- `2026-03-25_1329_strategy-review.md` 当时的正确结论是：在 `Rank 163` 被 survivor follow-up 否决后，`P3/P2/P1` 都没有真实可执行动作，因此应切回新的 fresh intake。
- 从那之后出现了新的状态变化：`2026-03-25_1410_rank164_altbtc-parity-intake.md` 已经把新的 fresh intake 落地为 `keep_P1`，所以当前前排不再是“只剩空槽”，而是已经有一个合法 survivor 需要先做那唯一一次 follow-up。

## 2) 只回答 4 个问题

### Q1. `Paper launch queue` 是否非空？
- **否，当前为空。**
- 当前没有新的合法 `P3 / paper launch` 待接线目标；`Rank 154` 仍是已 handoff 的后排 sidecar 对象，不会自动回流前排。

### Q2. 本轮 `fresh intake` 是什么？
- **本轮 fresh intake 是 `Rank 164 / ALTBTC synthetic-cross parity mean reversion`。**
- 它已经完成首判，并成为当前 state 里的最新一条 fresh intake。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且现在正该把这唯一一次 follow-up 用在 `Rank 164` 上。**
- 原因不是再补概念证据，而是 blocker 已明确收敛：只需要回答三腿真实执行口径下，`best bid/ask + 三腿 round-trip 成本 + 残余 BTC 暴露` 后，这条 parity 回归是否还能留下净边。
- 这是一条高杠杆、非重复轴的诚实检查，符合 policy 对 survivor 的唯一一次 decisive follow-up 定义。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **当前不存在明确 `Active P2`。**
- 因此本轮不存在需要 bot2 兜底直推 `P3` 的对象。
- 当前离出口最近的前排对象其实是 `Rank 164` 这个 survivor：它最近的决策出口是 `promote_P2` 或 `drop_to_background`，而不是继续开放式停留在 `P1`。

## 3) Rank / front-slot 合规检查
- `Paper launch queue = none`
- `Active P2 slot = none`
- `Surviving candidate slot = Rank 164`
- `Fresh intake slot = Rank 164`
- 前排对象均已有正式 `Rank`，本轮无需补下一个未使用整数 rank。

## 4) 排班判断
- `P3`：queue 为空，没有 handoff 动作，但按 policy 仍保留最小检查位，防止旧对象回流。
- `P2`：没有 active P2，因此 admission front 继续保持为空，不把 `Rank 163` 之类已被 execution realism 否决的对象写回 `P2`。
- `P1`：`Rank 164` 已成为唯一合法 survivor，并且仍保留 1 次有效、非重复轴的 decisive follow-up；这就是当前最该消耗主资源的动作。
- `fresh intake`：本轮只能作为 conditional 小点保留；只有在 `Rank 164` 的 survivor follow-up 明确释放前排槽位后，才轮到新的 intake 接棒。

## 5) 本轮对 `BOT2_BOT3_STATE.md` 的实际改写
本轮仅改写 `BOT2_BOT3_STATE.md`：
- 保持 `Paper launch queue = none`
- 保持 `Active P2 slot = none`
- 明确写回 `Fresh intake slot = Rank 164 / keep_P1`
- 明确写回 `Surviving candidate slot = Rank 164 / followup_budget_remaining = 1`
- 重写当前轮 `cycle_plan` 为 4 个 `pending` 小点，顺序为：
  1. `Paper launch queue`
  2. `Active P2 slot`
  3. `Surviving candidate slot`
  4. `Fresh intake slot`（conditional）
- 所有新项均写为 `result: none`、`status: pending`

## 6) 一句话结论
**当前没有 `P3` 或 `Active P2` 出口动作；真正该优先做的是把 `Rank 164` 的那唯一一次 survivor follow-up 用在三腿真实执行成本生存线上，只有它出前排后，主资源才应再切回新的 fresh intake。**
