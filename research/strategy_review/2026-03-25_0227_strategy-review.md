# Strategy Review (bot2)

Time: 2026-03-25 02:27 UTC

## 本轮一句话判断
当前前排并没有 `P3` 或 `Active P2` 压力，唯一真实前排动作是 `Rank 157 / H<0.5 spread-band fast mean-reversion` 的那一次 survivor follow-up；因此本轮主资源必须先做这次 `pair-selection × cost × timeout` 诚实检查，只有它被直接收口为 `drop_to_background` 后，才允许把资源切回新的 fresh intake。

## 1) 必检输入

### Policy / state 先读结论
- fixed policy 继续要求按 `P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0` 排班。
- 只有当 `P3/P2/P1` 都没有真实可执行动作时，主资源才切回 `fresh intake`。
- 当前 runtime truth（本轮改写前）显示：
  - `Paper launch queue.current_target = none`
  - `Fresh intake slot.current_target = Rank 157 / H<0.5 spread-band fast mean-reversion`
  - `Surviving candidate slot.current_target = Rank 157 / H<0.5 spread-band fast mean-reversion`
  - `followup_budget_remaining = 1`
  - `Active P2 slot.current_target = none`
  - `Background pool.do_not_auto_reopen = true`

### Repo 状态
- repo 仍有大量未跟踪 artifacts / pages / scripts。
- 按 policy，这些都只是 evidence，不构成旧候选自动 reopen 的依据，也不能反向改 policy。

### 最近 `research/optimization_loop/`
1. `2026-03-25_0225_rank157-survivor-assignment.md`
   - 已把 `Rank 157` 正式写成唯一合法 survivor，并把唯一 follow-up 收口为单一 decisive blocker：只回答 `top-pair pocket` 在现实可接受的 `round-trip cost × timeout` 治理后，是否仍保留稳定正的 post-cost expectancy。
2. `2026-03-25_0200_rank157-hurst-pairs-fast-meanreversion-intake.md`
   - fresh intake 已完成并给出 `keep_P1`：论文骨架完整，本地 Binance 15m probe 也复现出 `H<0.5` pocket 明显更快回归，但还没有证明成本后可交易，因此只值得那唯一一次 survivor follow-up，而不是直接升 `P2`。
3. `2026-03-25_0122_technical-analysis-meets-ml-bitcoin-park.md`
   - 最近上一条 direct-park intake 已明确不值得 follow-up；亮点停留在无法诚实冻结的 ML 结果展示，TA 腿只是老骨架。
4. `2026-03-25_0048_rank156-cost-buffer-followup-drop.md`
   - `Rank 156` 的 survivor 唯一 follow-up 已收口为 `drop_to_background`；说明系统最近的 survivor 检查标准仍然是收口式，而不是拖长式。

### 最近 `research/strategy_review/`
1. `2026-03-25_0132_strategy-review.md`
   - 上一轮正确判断：当时前排全空，主资源应切回 fresh intake。
2. 与上一轮相比，本轮新增的关键变化只有两条：
   - fresh intake 已被新的 `Rank 157` 填入，并且不是 `park`，而是 `keep_P1`；
   - `Rank 157` 又已被合法写入 survivor，因此当前已经不再处于“前排全空”的状态。
- 这意味着上一轮那种“继续 fresh intake 优先”的排班已经不再适用；本轮必须先处理 survivor 这条前排合法动作。

## 2) 只回答 4 个问题

### Q1. `Paper launch queue` 是否非空？
- **否，当前为空。**
- `Rank 154 / Crypto-Stat-Arb` 已在 2026-03-24 完成 `P2 -> P3` 后的 refresh-only sidecar offload，不再占默认前排轮次。

### Q2. 本轮 `fresh intake` 是什么？
- **本轮 fresh intake 是 `Rank 157 / H<0.5 spread-band fast mean-reversion`。**
- 它已经在 02:00 UTC 完成 intake，并被判为 `keep_P1`。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且这唯一一次 follow-up 现在就是当前前排主线。**
- 原因很具体：它的问题不是“缺很多开放式研究”，而是一个单一、可收口的 blocker——是否存在 `top-pair pocket` 能在现实可接受的 `pair-selection × cost × timeout` 治理后仍保留正的 post-cost expectancy。
- 如果答案是能，就应进入 `P2`；如果答案是否，就应直接回落 `Background pool`。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **当前不存在明确 `Active P2`。**
- 因此本轮不存在需要回答“更接近 `P3 / P1 / P0` 哪个出口”的 admission 对象；离出口最近的其实是 `Rank 157` 的 survivor 决断，而不是任何 `P2`。

## 3) Rank / front-slot 合规检查
- 当前前排对象里没有任何 `keep_P1 / P2 / P3` 但无正式 Rank 的非法对象。
- `Rank 157` 已有正式 Rank，并合法占据 `Fresh intake slot` 与 `Surviving candidate slot`。
- `Paper launch queue = none`、`Active P2 = none`，因此本轮 **无需补 rank**。

## 4) 本轮 cycle_plan 重写依据
- `P3`：queue 为空，没有 handoff 动作。
- `P2`：没有 active P2，因此没有现成的 admission / promote / park 决策轮。
- `P1`：存在唯一合法 survivor `Rank 157`，且仍保留 1 次 follow-up 预算；按 policy，这就是当前最优先的真实动作。
- 因此本轮默认顺序应改成：
  1. 先做 `Rank 157` survivor 唯一一次诚实检查；
  2. 若其结果明确证明存在可交易 pocket，则立即写入唯一 `Active P2`；
  3. 只有当它被直接收口为 `drop_to_background` 且前排重新清空时，才切回新的 fresh intake；
  4. 若新的 fresh intake 形成 `keep_P1`，再把它写成新的唯一 survivor。
- 本轮 **不需要**把 `Background pool guard` 单独写成 pending 小点，因为没有出现自动 reopen / 槽位污染，也没有刚完成新的 `P3 handoff` 切换收口。

## 5) 本轮对 `BOT2_BOT3_STATE.md` 的实际改写
本轮仅改写 `BOT2_BOT3_STATE.md`，且只改 runtime truth：
- 保留 `Paper launch queue = none`
- 保留 `Fresh intake slot = Rank 157`
- 保留 `Surviving candidate slot = Rank 157`
- 保留 `Active P2 slot = none`
- 将 `cycle_plan` 改写为新的 4 项 `pending`：
  1. `Rank 157` survivor follow-up
  2. 仅当第 1 项通过时，立即写入 `Active P2`
  3. 仅当第 1 项直接 drop 且前排仍空时，再做新的 fresh intake
  4. 仅当第 3 项得到 `keep_P1` 时，再写入新的 survivor

所有新项均满足：
- 只含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 6) 一句话结论
**当前不是“继续多抓一个 fresh intake”的时点；最应该先做的，是把 `Rank 157` 那唯一一次 survivor follow-up 做成一个真收口的 yes/no 决断。**
