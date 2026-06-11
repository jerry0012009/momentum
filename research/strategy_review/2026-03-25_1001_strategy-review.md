# Strategy Review (bot2)

Time: 2026-03-25 10:01 UTC

## 本轮一句话判断
当前前排唯一真实动作不是继续 fresh intake，而是把 `Rank 162 / Kalman β-gap cross-sectional raw alpha` 的那唯一一次 survivor follow-up 做成 yes/no 收口；`Paper launch queue` 为空、`Active P2` 为空，因此本轮主资源必须先回答“极端 β-gap 事件触发后，成本后的 `avg bps/trigger` 能否转正”，只有它被明确打回 background 后，才允许把主资源切回新的 fresh intake。

## 1) 必检输入

### Policy / state 先读结论
- fixed policy 继续要求按 `P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0` 排班。
- 只有当 `P3/P2/P1` 都没有真实可执行动作时，主资源才切回 `fresh intake`。
- 当前 runtime truth（本轮改写后）显示：
  - `Paper launch queue.current_target = none`
  - `Fresh intake slot.current_target = Rank 162 / Kalman β-gap cross-sectional raw alpha`
  - `Surviving candidate slot.current_target = Rank 162 / Kalman β-gap cross-sectional raw alpha`
  - `followup_budget_remaining = 1`
  - `Active P2 slot.current_target = none`
  - `Background pool.do_not_auto_reopen = true`

### Repo 状态
- repo 仍有大量未跟踪 artifacts / pages / scripts。
- 按 policy，这些都只是 evidence，不构成旧候选自动 reopen 的依据，也不能反向改 policy。

### 最近 `research/optimization_loop/`
1. `2026-03-25_0957_rank162-survivor-assign.md`
   - `Rank 162` 已被合法写入唯一 survivor；其唯一 follow-up blocker 已收口为：只回答“极端 β-gap 事件触发后，Binance perp 执行下的 `post-cost avg bps/trigger` 是否还能转正”。
2. `2026-03-25_0930_rank162-kalman-beta-gap-intake.md`
   - `Rank 162` fresh intake 已完成并给出 `keep_P1`：横截面排序力确实存在，但 naive `5m/15m` 裸轮动先被换手和成本吃掉，因此不能直接升 `P2`。
3. `2026-03-25_0917_skylar-oversold-intake-park.md`
   - 上一条最新被直接 `park` 的 fresh intake《Skylar oversold volume reversal transfer check》已明确不值得 survivor follow-up：默认 Binance perp/15m transfer 四个持有窗全负，只剩极端 capitulation pocket 的小样本线索。
4. `2026-03-25_0740_rank161-survivor-followup-drop-background.md`
   - `Rank 161 / EPCM microstructure taker alpha` 的唯一 survivor follow-up 已完成，并明确 `drop_to_background`：三币最优毛收益仅 `0.85~0.98 bps/event`，在保守 `2~6 bps round-trip` 下全部转负。

### 最近 `research/strategy_review/`
1. `2026-03-25_0921_strategy-review.md`
   - 上一轮的默认排班仍是“若前排全空则回 fresh intake”；随后 bot3 已完成新 intake，并产出新的 `Rank 162 / keep_P1 -> survivor`。
2. `2026-03-25_0817_strategy-review.md`
   - 更早一轮正确把主资源切回 fresh intake，而不是围绕已 drop 的对象延长研究。
3. 与上一轮相比，本轮新增关键变化只有两条：
   - fresh intake 已被新的 `Rank 162` 填入，而且不是 `park`，而是 `keep_P1`；
   - `Rank 162` 又已被合法写入 survivor，因此当前已经不再处于“前排全空”的状态。

## 2) 只回答 4 个问题

### Q1. `Paper launch queue` 是否非空？
- **否，当前为空。**
- `Rank 154 / Crypto-Stat-Arb` 已在 2026-03-24 完成 `refresh-only sidecar` offload，不再占默认前排轮次。

### Q2. 本轮 `fresh intake` 是什么？
- **本轮 fresh intake 是 `Rank 162 / Kalman β-gap cross-sectional raw alpha`。**
- 它已在 09:30 UTC 完成 intake，并被判为 `keep_P1`。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且现在就是当前前排主线。**
- 原因很具体：`Rank 162` 的 blocker 不是缺更多开放式故事，而是一个单一、可收口的问题——当信号从“每 bar 裸轮动”收紧为“极端 β-gap 事件触发”后，保守成本口径下的 `post-cost avg bps/trigger` 是否还能留下正值 pocket。
- 如果答案是能，就应进入 `P2`；如果答案是否，就应直接回落 `Background pool`。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **当前不存在明确 `Active P2`。**
- 因此本轮不存在需要回答“更接近 `P3 / P1 / P0` 哪个出口”的 admission 对象；离出口最近的其实是 `Rank 162` 的 survivor 决断，而不是任何 `P2`。

## 3) Rank / front-slot 合规检查
- 当前前排对象里没有任何 `keep_P1 / P2 / P3` 但无正式 Rank 的非法对象。
- `Rank 162` 已有正式 Rank，并合法占据 `Fresh intake slot` 与 `Surviving candidate slot`。
- `Paper launch queue = none`、`Active P2 = none`，因此本轮无需补 rank。

## 4) 本轮 cycle_plan 重写依据
- `P3`：queue 为空，没有 handoff 动作。
- `P2`：没有 active P2，因此没有现成的 admission / promote / park 决策轮。
- `P1`：存在唯一合法 survivor `Rank 162`，且仍保留 1 次 follow-up 预算；按 policy，这就是当前最优先的真实动作。
- 因此本轮默认顺序应改成：
  1. 先做 `Rank 162` survivor 唯一一次诚实检查；
  2. 若其结果明确证明存在可交易 pocket，则立即写入唯一 `Active P2`；
  3. 只有当它被直接收口为 `drop_to_background` 且前排重新清空时，才切回新的 fresh intake；
  4. 若新的 fresh intake 形成 `keep_P1`，再把它写成新的唯一 survivor。
- 本轮不需要把 `Background pool guard` 单独写成 pending 小点，因为没有出现自动 reopen / 槽位污染，也没有新的 `P3 handoff` 切换收口。

## 5) 本轮对 `BOT2_BOT3_STATE.md` 的实际改写
本轮仅改写 `BOT2_BOT3_STATE.md`，且只改 runtime truth：
- 保留 `Paper launch queue = none`
- 保留 `Fresh intake slot = Rank 162`
- 保留 `Surviving candidate slot = Rank 162`
- 保留 `Active P2 slot = none`
- 将 `cycle_plan` 改写为新的 4 项 `pending`：
  1. `Rank 162` survivor follow-up
  2. 仅当第 1 项通过时，立即写入 `Active P2`
  3. 仅当第 1 项直接 drop 且前排仍空时，再做新的 fresh intake
  4. 仅当第 3 项得到 `keep_P1` 时，再写入新的 survivor

所有新项均满足：
- 只含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 6) 一句话结论
**当前不是继续并行扩 fresh intake 的时点；最该先做的，是把 `Rank 162` 那唯一一次 survivor follow-up 做成一个真收口的 yes/no 决断。**
