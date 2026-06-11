# 2026-03-30 14:30 UTC strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 重排，只依据当前 runtime state、repo 状态、最近 `research/optimization_loop/`、最近 `research/strategy_review/` 与最新 digest 证据。

## 只回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 结论：**否。**
   - 证据：`BOT2_BOT3_STATE.md` 当前仍写明 `Paper launch queue.current_target: none`；已 live 的只有 `connected_runner_live`（Rank 200 / 201 / 213 / 229），没有待接线 queue 头。

2. **本轮 `fresh intake` 是什么？**
   - 结论：本轮 fresh intake 仍是 **`Rank 254 / BTC confirmed jump / liquid-alt follower contagion`**。
   - 证据：`Fresh intake slot.current_target` 当前即为 `Rank 254`，其首判已在 `research/optimization_loop/2026-03-30_1357_rank254_btc_jump_follower_contagion_intake_keep_p1.md` 完成，并已正式进入 survivor。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 结论：**值得，而且这是当前唯一必须优先收口的前排动作。**
   - 证据：`Surviving candidate slot` 当前就是 `Rank 254`，`followup_budget_remaining: 1`。最新首判已经把对象边界收窄到“`BTC confirmed jump -> ETH/LTC/XRP/BCH/ETC same-sign delayed follow-through` 的稀疏事件 pocket”，下一次且仅一次 follow-up 直接回答 public-data frozen replication、next-bar execution 与成本后 edge 是否还能站住；这正是 policy 允许且要求的 survivor 唯一诚实检查。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 结论：**不存在。**
   - 证据：`BOT2_BOT3_STATE.md` 当前 `Active P2 slot.current_target: none`。最近的 `Rank 235` 已在 `2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md` 完成 `one-time P2 -> P1 re-scope`，不再属于当前 active P2。

## rank / 前排合法性检查

- `Paper launch queue`: 无当前 queue 头
- `Surviving candidate`: `Rank 254`，已有正式 rank
- `Active P2`: `none`
- 结论：**本轮无需补 rank。**

## repo / recent evidence quick notes

- `git status --short --branch` 显示 repo 内存在大量未跟踪产物；本轮仅把它当环境噪音，不据此反推 policy 或改排班。
- 最近 optimization 证据链的关键信号：
  - `2026-03-30_1357_rank254_btc_jump_follower_contagion_intake_keep_p1.md`：`Rank 254` fresh intake 首判完成，进入 survivor
  - `2026-03-30_1406_bucket_neutral_mr_funding_gate_blocked_survivor_lock.md`：Hyperliquid bucket-MR 对象不是被判死，而是被 survivor lock 合法拦下
  - `2026-03-30_1428_multispread_conditional_closure_background_p0.md`：multiquote multispread 条线已诚实收口回 `background/P0`
- 最近新 digest 里，最值得占用接下来 intake 预算的新对象是：
  1. `research/quant_digests/2026-03-30_1426_deribit-expiry-twap-anchor-alpha.md`
  2. `research/quant_digests/2026-03-30_1242_bucket-neutral-mr-funding-divergence-gate.md`
  3. `research/quant_digests/2026-03-30_1348_onchain-vol-spike-btc-mr-alpha.md`

## cycle_plan 重写结论

按 policy 默认顺序扫描合法动作：
1. `P3 handoff`：无待接线 queue 头
2. `P2 admission/promote/park`：无 Active P2
3. `P1 唯一一次诚实检查`：有，而且只剩 `Rank 254` 这一条 survivor
4. 因此前排链条未完全收口前，第一优先级必须先排 `Rank 254` 的唯一 follow-up；其后才能用剩余预算补新的具体 intake

因此本轮把 `cycle_plan` 重写为：
1. `Rank 254 / BTC confirmed jump / liquid-alt follower contagion` survivor follow-up
2. `settlement-TWAP anchor gap / Deribit near-expiry options` fresh intake
3. `bucket-neutral 1h return mean reversion × funding misalignment gate` fresh intake
4. `onchain volume spike → BTC short-horizon mean reversion` fresh intake

## 为什么这样排

- 当前不存在任何合法 `P3` 或 `Active P2` 动作，因此前排唯一必须优先收口的是 `Rank 254` 的 survivor follow-up。
- `Rank 254` 已经拿到 `keep_P1`，按 policy 在诚实收口前享有 survivor 锁定权；不能再让新的 `keep_P1` 候选把它挤掉。
- `settlement-TWAP anchor gap / Deribit near-expiry options` 是当前最新、边界最清楚、且与现有 perp/funding 家族最正交的新 repo/digest：它主语不是 scanner，而是“到期前最后 30 分钟，option premium 向 settlement-TWAP anchor 回归”的事件型 options raw alpha。
- `bucket-neutral 1h MR × funding divergence gate` 上一轮只是被 survivor lock 挡住，并未被否定；当前 survivor 已在第 1 项诚实排入后，它理应回到下一条具体 intake。
- `onchain volume spike → BTC short-horizon mean reversion` 只作为补位 intake；它优先级低于 survivor 收口、也低于更独立的 Deribit / bucket-MR 新对象。

## P2 -> P3 兜底裁判是否触发

**不触发。**

因为：
- 当前 `Paper launch queue = none`
- 当前 `Active P2 = none`
- 最近 desk review 没有出现“对象已明显足够进入 paper trade / paper launch，但 bot3 尚未升级”的 active P2

因此本轮不新增 `P3 / Paper launch queue` 写回，也不伪造 handoff 路径。

## writeback

- 已更新：`docs/BOT2_BOT3_STATE.md`
- 未改写：policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 本轮没有对象达到 bot2 兜底直推 `P3` 的门槛，因此无新增 P3 handoff 写回
