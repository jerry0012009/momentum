# Strategy Review (bot2)

Time: 2026-03-25 06:52 UTC

## 本轮一句话判断
当前真正的前排动作不是 fresh intake，而是 `Rank 160 / rolling LASSO sparse next-minute raw alpha` 那唯一一次 survivor follow-up；`Paper launch queue` 为空、`Active P2` 为空，因此本轮主资源必须先把这次 `high-liquidity vs retail-beta × 保守 taker/spread 成本` 诚实检查做成 yes/no 收口，只有它被明确打回 background 后，才允许把主资源切回新的 fresh intake。

## 1) 必检输入

### Policy / state 先读结论
- fixed policy 继续要求按 `P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0` 排班。
- 只有当 `P3/P2/P1` 都没有真实可执行动作时，主资源才切回 `fresh intake`。
- 当前 runtime truth（本轮改写前）显示：
  - `Paper launch queue.current_target = none`
  - `Fresh intake slot.current_target = Rank 160 / rolling LASSO sparse next-minute raw alpha`
  - `Surviving candidate slot.current_target = Rank 160 / rolling LASSO sparse next-minute raw alpha`
  - `followup_budget_remaining = 1`
  - `Active P2 slot.current_target = none`
  - `Background pool.do_not_auto_reopen = true`

### Repo 状态
- repo 仍有大量未跟踪 artifacts / pages / scripts。
- 按 policy，这些都只是 evidence，不构成旧候选自动 reopen 的依据，也不能反向改 policy。

### 最近 `research/optimization_loop/`
1. `2026-03-25_0650_rank160-survivor-slot-assign.md`
   - `Rank 160` 已被合法写入唯一 survivor；其唯一一次 follow-up 已收口为：只回答这条 minute alpha 在 `high-liquidity vs retail-beta` 两个 bucket 中，按保守 taker/spread 成本后是否仍保留稳定正的 `post-cost avg bps/trigger`。
2. `2026-03-25_0558_rank160-sparse-lasso-intraday-intake.md`
   - `Rank 160` fresh intake 已完成并给出 `keep_P1`：公开论文与本地 proxy 都说明它不是空洞 ML 叙事，但 edge 明显依赖币种分层与 active 分钟筛选，因此还不能直接升 `P2`。
3. `2026-03-25_0529_rank159-survivor-followup-drop-background.md`
   - 上一个 survivor `Rank 159` 已按 policy 收口为 `drop_to_background`，没有被拖成长尾开放研究。
4. `2026-03-25_0532_strategy-review.md`
   - 上一轮正确把资源切回了 fresh intake；这一动作已经执行完成，并产出了新的 `Rank 160 / keep_P1 -> survivor`。

### 最近 `research/strategy_review/`
1. `2026-03-25_0532_strategy-review.md`
   - 上一轮判断是：前排已空，因此应把主资源切回新的 fresh intake。
2. 与上一轮相比，本轮新增的关键变化只有两条：
   - fresh intake 已被新的 `Rank 160` 填入，而且不是 `park`，而是 `keep_P1`；
   - `Rank 160` 又已被合法写入 survivor，因此当前已经不再处于“前排全空”的状态。
- 这意味着上一轮那种“继续 fresh intake 优先”的排班已经不再适用；本轮必须先处理 survivor 这条前排合法动作。

## 2) 只回答 4 个问题

### Q1. `Paper launch queue` 是否非空？
- **否，当前为空。**
- `Rank 154 / Crypto-Stat-Arb` 已在 2026-03-24 完成 `refresh-only sidecar` offload，不再占默认前排轮次。

### Q2. 本轮 `fresh intake` 是什么？
- **本轮 fresh intake 是 `Rank 160 / rolling LASSO sparse next-minute raw alpha`。**
- 它已在 05:58 UTC 完成 intake，并被判为 `keep_P1`。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且现在就是当前前排主线。**
- 原因很具体：`Rank 160` 的 blocker 不是缺更多开放式故事，而是一个单一、可收口的问题——在 `high-liquidity vs retail-beta` 两个 bucket 中，minute alpha 在保守 taker/spread 成本后是否还能留下稳定正的 `post-cost avg bps/trigger`。
- 如果答案是能，就应进入 `P2`；如果答案是否，就应直接回落 `Background pool`。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **当前不存在明确 `Active P2`。**
- 因此本轮不存在需要回答“更接近 `P3 / P1 / P0` 哪个出口”的 admission 对象；离出口最近的其实是 `Rank 160` 的 survivor 决断，而不是任何 `P2`。

## 3) Rank / front-slot 合规检查
- 当前前排对象里没有任何 `keep_P1 / P2 / P3` 但无正式 Rank 的非法对象。
- `Rank 160` 已有正式 Rank，并合法占据 `Fresh intake slot` 与 `Surviving candidate slot`。
- `Paper launch queue = none`、`Active P2 = none`，因此本轮无需补 rank。

## 4) 本轮 cycle_plan 重写依据
- `P3`：queue 为空，没有 handoff 动作。
- `P2`：没有 active P2，因此没有现成的 admission / promote / park 决策轮。
- `P1`：存在唯一合法 survivor `Rank 160`，且仍保留 1 次 follow-up 预算；按 policy，这就是当前最优先的真实动作。
- 因此本轮默认顺序应改成：
  1. 先做 `Rank 160` survivor 唯一一次诚实检查；
  2. 若其结果明确证明存在可交易 pocket，则立即写入唯一 `Active P2`；
  3. 只有当它被直接收口为 `drop_to_background` 且前排重新清空时，才切回新的 fresh intake；
  4. 若新的 fresh intake 形成 `keep_P1`，再把它写成新的唯一 survivor。
- 本轮不需要把 `Background pool guard` 单独写成 pending 小点，因为没有出现自动 reopen / 槽位污染，也没有刚完成新的 `P3 handoff` 切换收口。

## 5) 本轮对 `BOT2_BOT3_STATE.md` 的实际改写
本轮仅改写 `BOT2_BOT3_STATE.md`，且只改 runtime truth：
- 保留 `Paper launch queue = none`
- 保留 `Fresh intake slot = Rank 160`
- 保留 `Surviving candidate slot = Rank 160`
- 保留 `Active P2 slot = none`
- 将 `cycle_plan` 改写为新的 4 项 `pending`：
  1. `Rank 160` survivor follow-up
  2. 仅当第 1 项通过时，立即写入 `Active P2`
  3. 仅当第 1 项直接 drop 且前排仍空时，再做新的 fresh intake
  4. 仅当第 3 项得到 `keep_P1` 时，再写入新的 survivor

所有新项均满足：
- 只含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 6) 一句话结论
**当前不是继续并行扩 fresh intake 的时点；最该先做的，是把 `Rank 160` 那唯一一次 survivor follow-up 做成一个真收口的 yes/no 决断。**
