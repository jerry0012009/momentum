# Strategy Review (bot2)

Time: 2026-03-25 05:32 UTC

## 本轮一句话判断
当前前排已被 `Rank 159` 的 survivor drop 正式清空：`Paper launch queue = none`、`Active P2 = none`、`Surviving candidate = none`；因此这轮没有任何可继续占主资源的 `P3/P2/P1` 动作，按 policy 应直接把主资源切回新的 fresh intake，不得把 background pool 旧候选自动拉回前排。

## 1) 必检输入

### Policy / state 先读结论
- fixed policy 仍要求按 `P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0` 排班。
- 只有当 `P3/P2/P1` 都没有真实可执行动作时，主资源才切回 `fresh intake`。
- 当前 runtime truth（本轮改写前）显示：
  - `Paper launch queue.current_target = none`
  - `Fresh intake slot.current_target = none`
  - `Surviving candidate slot.current_target = none`
  - `Active P2 slot.current_target = none`
  - `Background pool.do_not_auto_reopen = true`

### Repo 状态
- repo 仍有大量未跟踪 artifacts / pages / scripts。
- 按 policy，这些都只是 evidence，不构成旧候选自动 reopen 的依据，也不能反向改 policy。

### 最近 `research/optimization_loop/`
1. `2026-03-25_0529_rank159-survivor-followup-drop-background.md`
   - `Rank 159` 的唯一一次 survivor follow-up 已完成，并明确收口为 `drop_to_background`：低 trade-count follower 的排序方向仍在，但统一 `6 bps round-trip` 后三个 bucket 的最佳 `post-cost avg return / trade` 全为负。
2. `2026-03-25_0454_rank159-btc-alt-trade-count-lag-intake.md`
   - 上一条 fresh intake 是 `Rank 159 / BTC→ALT trade-count-sorted 1m lag follower`，其 fresh 首判是合法 `keep_P1`。
3. `2026-03-25_0353_rank158-survivor-followup-drop-background.md`
   - `Rank 158` 先前也已完成唯一一次 survivor follow-up，并明确 `drop_to_background`。
4. `2026-03-25_0302_rank158-pump-fade-intake.md`
   - `Rank 158` fresh intake 虽曾合法进入 `keep_P1`，但已在唯一 follow-up 后失败，不可继续占用前排。

### 最近 `research/strategy_review/`
1. `2026-03-25_0451_strategy-review.md`
   - 上一轮已正确把排班切回 `fresh intake`，前提是 `Rank 158` 已 drop 且前排清空。
2. 与上一轮相比，本轮新增的关键变化只有一条：
   - `Rank 159` 作为新的 survivor 也已完成唯一一次 follow-up，并明确 `drop_to_background`。
- 这意味着：上一轮给 fresh intake 的排班已经执行完，且没有产生新的 survivor / P2 / P3 压力；本轮应继续保持 `fresh-intake-first` 的默认顺序。

## 2) 只回答 4 个问题

### Q1. `Paper launch queue` 是否非空？
- **否，当前为空。**
- `Rank 154 / Crypto-Stat-Arb` 已在 2026-03-24 完成 `refresh-only sidecar` offload，不再占默认前排轮次。

### Q2. 本轮 `fresh intake` 是什么？
- **本轮尚无新的 fresh intake。**
- 上一条 fresh intake 是 `Rank 159 / BTC→ALT trade-count-sorted 1m lag follower`，但它已在 survivor follow-up 后正式 `drop_to_background`；因此本轮需要重新认领 1 个新的 raw alpha / paper / repo。

### Q3. 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且已经被执行完了；最终答案是否。**
- `Rank 159` 值得那一次 follow-up，因为 blocker 能被诚实地收口成单一问题：desk 可交易 perp universe 内、低 trade-count follower 的 lag edge 在保守 round-trip 成本后是否仍为正。
- 现在答案已经明确是否：排序方向仍在，但成本后最佳 pocket 全为负，因此它不值得第二次 follow-up，也不值得升 `P2`。

### Q4. 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **当前不存在明确 `Active P2`。**
- 因此本轮没有 admission 对象需要回答离 `P3 / P1 / P0` 哪个出口最近；离出口最近的对象已经是 `Rank 159`，而它的出口答案已明确写成 `P0 / Background pool`。

## 3) Rank / front-slot 合规检查
- 当前前排对象里没有任何 `keep_P1 / P2 / P3` 但无正式 Rank 的非法对象。
- `Paper launch queue = none`、`Active P2 = none`、`Surviving candidate = none`。
- 因此本轮无需补 rank。

## 4) 本轮 cycle_plan 重写依据
- `P3`：queue 为空，没有 handoff 动作。
- `P2`：没有 active P2，因此没有 admission / promote / park 决策轮。
- `P1`：没有 survivor；`Rank 159` 的 follow-up 预算已归零，不能再续写。
- 因此本轮默认顺序应改成：
  1. 直接做新的 fresh intake；
  2. 若该 intake 得到 `keep_P1`，立即把它写成新的唯一 survivor；
  3. 仅当新的 survivor 成立时，执行那唯一一次 decisive follow-up；
  4. 若该 survivor 又被直接收口为 `drop_to_background` 且前排仍空，再补 1 条 conditional fresh intake。
- 本轮不需要把 `Background pool guard` 单独写成 pending 小点，因为没有自动 reopen / 槽位污染，也没有新的 `P3 handoff` 切换需要审计。

## 5) 本轮对 `BOT2_BOT3_STATE.md` 的实际改写
本轮仅改写 `BOT2_BOT3_STATE.md`，且只改 runtime truth 里的 `cycle_plan`：
1. `Fresh intake slot`：认领 1 个新的 raw alpha / paper / repo，并直接回答 `park / keep_P1`
2. `Surviving candidate slot`：仅当第 1 项得到 `keep_P1` 时，把它写成新的唯一 survivor，并收口唯一 blocker
3. `Surviving candidate slot`：仅当第 2 项已形成 survivor 时，执行那唯一一次 decisive follow-up，并直接收口为 `promote_P2` 或 `drop_to_background`
4. `Fresh intake slot`：仅当第 3 项把新的 survivor 直接 drop 且前排仍空时，再补 1 条 conditional fresh intake

所有新项均满足：
- 只含 `target / action / success_criterion / result / status`
- `result = none`
- `status = pending`

## 6) 一句话结论
**这轮已经没有资格继续占主资源的 `P3/P2/P1` 对象；最诚实的排班是回到新的 fresh intake，而不是围着刚被明确打回 background 的 `Rank 159` 继续转。**
