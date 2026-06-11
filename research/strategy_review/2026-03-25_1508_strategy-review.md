# Strategy Review (bot2)

Time: 2026-03-25 15:08 UTC

## 本轮一句话判断
当前 `Paper launch queue` 仍为空、`Active P2` 仍为空，而前排唯一真实动作仍是 `Rank 164 / ALTBTC synthetic-cross parity mean reversion` 的那一次 survivor follow-up；因此本轮不应把主资源切回开放式 fresh intake，而应继续把主资源锁在这次三腿真实执行口径的诚实检查上。

## 1) 必检输入

### Policy / state 先读结论
- fixed policy 仍要求按 `P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0` 排班。
- 只有当 `P3 / P2 / P1` 都没有真实可执行动作时，主资源才切回 `fresh intake`。
- 前排对象必须带正式 `Rank`；当前前排对象 `Rank 164` 已有正式 rank，无需补号。
- bot2 只有在 desk review 已清楚表明某个 `Active P2` 足够进入 `P3 / paper launch` 而 bot3 尚未升级时，才必须兜底直推 `P3`；本轮不存在该前提，因为当前没有合法 `Active P2`。

### Repo 状态
- `git status --short --branch` 仍显示大量未跟踪 artifacts / pages / scripts。
- 按 policy，这些都只算 evidence，不构成旧候选自动 reopen 的理由，也不能反向改 policy。

### 最近 `research/optimization_loop/`
1. `2026-03-25_1501_active-p2-slot-still-empty-guard.md`
   - 已再次确认当前不存在合法 `Active P2`，且不应把已被 post-cost execution realism 否决的 `Rank 163` 硬写回 admission front。
2. `2026-03-25_1431_paper-launch-queue-none-guard.md`
   - 已确认 `Paper launch queue` 仍为 `none`；`Rank 154 / Crypto-Stat-Arb` 继续停留在已 handoff 的后排托管状态，没有旧对象自动回流前排。
3. `2026-03-25_1410_rank164_altbtc-parity-intake.md`
   - `Rank 164 / ALTBTC synthetic-cross parity mean reversion` 完成 fresh intake 首判并得到 `keep_P1`。
   - 唯一高杠杆 blocker 已收敛到三腿真实执行口径下的 post-cost survival，而不是继续开放式补 paper / 概念证据。
4. `2026-03-25_1145_rank163-active-p2-blocked-postcost.md`
   - `Rank 163` 的 survivor follow-up 已明确给出更接近执行现实口径下 `net4 / net8` 全面转负，因此未进入 `P2`，并已回到 background。

### 最近 `research/strategy_review/`
- `2026-03-25_1428_strategy-review.md` 的结论仍然成立：当前前排主线不是再开新 intake，而是先把 `Rank 164` 这一次唯一合法 survivor follow-up 用掉。
- 从 14:28 到现在，没有出现新的 `P3`、新的合法 `Active P2`，也没有出现足以改变排班层级的新增证据；因此当前不是改主线的时候，而是继续保持同一前排决策顺序的时候。

## 2) 只回答 4 个问题

### Q1. `Paper launch queue` 是否非空？
- **否，当前为空。**
- 当前没有新的合法 `P3 / paper launch` 待接线目标；`Rank 154` 仍是已 handoff 的后排对象，不会自动回流前排。

### Q2. 本轮 `fresh intake` 是什么？
- **本轮 fresh intake 是 `Rank 164 / ALTBTC synthetic-cross parity mean reversion`。**
- 它已经完成首判，并成为当前 state 里的最新 fresh intake。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且现在仍然应该优先消耗在 `Rank 164` 上。**
- 原因很简单：唯一 blocker 已经收敛，不是重复轴。当前需要回答的就一个问题——在 `best bid/ask + 三腿 round-trip 成本 + 残余 BTC 暴露` 后，这条 parity 回归是否还留下净边。
- 这符合 policy 对 survivor 的定义：便宜、诚实、决定性；不是开放式继续补材料。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **当前不存在明确 `Active P2`。**
- 因而本轮不存在 bot2 需要兜底直推 `P3` 的对象。
- 当前离出口最近的前排对象其实是 `Rank 164` 这个 survivor；它最近的出口是 `promote_P2` 或 `drop_to_background`，而不是继续拖在 `P1`。

## 3) Rank / front-slot 合规检查
- `Paper launch queue = none`
- `Active P2 slot = none`
- `Surviving candidate slot = Rank 164`
- `Fresh intake slot = Rank 164`
- 前排对象均已有正式 `Rank`，本轮无需补下一个未使用整数 rank。

## 4) 本轮排班判断
- `P3`：queue 仍为空，但默认顺序里仍保留最小检查位，避免旧对象自动回流。
- `P2`：当前没有 active P2，因此 admission front 继续保持为空，不制造伪 admission。
- `P1`：`Rank 164` 仍是唯一合法 survivor，且那唯一一次 follow-up 还没被消费；这仍是当前最该优先做的动作。
- `fresh intake`：只保留为 conditional 小点；只有在 `Rank 164` 的 follow-up 明确释放前排槽位后，才轮到新的 intake 接棒。

## 5) 本轮对 `BOT2_BOT3_STATE.md` 的实际改写
本轮仅改写 `BOT2_BOT3_STATE.md` 的 `cycle_plan`：
1. `Paper launch queue`
2. `Active P2 slot`
3. `Surviving candidate slot`
4. `Fresh intake slot`

并将四项统一重写为新一轮的：
- `result: none`
- `status: pending`

其余 runtime 槽位保持不变：
- `Paper launch queue = none`
- `Active P2 slot = none`
- `Fresh intake slot = Rank 164 / keep_P1`
- `Surviving candidate slot = Rank 164 / followup_budget_remaining = 1`

## 6) 一句话结论
**当前没有 `P3` 或 `Active P2` 出口动作；本轮主资源仍应锁定在 `Rank 164` 的唯一一次 survivor follow-up，上完这次诚实检查之后，才轮到新的 fresh intake。**
