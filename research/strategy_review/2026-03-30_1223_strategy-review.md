# 2026-03-30 12:23 UTC strategy review

本轮严格按 `docs/BOT2_BOT3_POLICY.md` 与 `docs/BOT2_BOT3_STATE.md` 重排，只依据当前 runtime state、repo 状态、最近 `research/optimization_loop/`、最近 `research/strategy_review/` 与最新 digest 证据。

## 只回答 4 个问题

1. **`Paper launch queue` 是否非空？**
   - 结论：**否。**
   - 证据：`BOT2_BOT3_STATE.md` 当前写明 `Paper launch queue.current_target: none`；仅有已 live 的 `connected_runner_live` 列表（Rank 200 / 201 / 213 / 229），没有待接线 queue 头。

2. **本轮 `fresh intake` 是什么？**
   - 结论：本轮刚完成的 fresh intake 是 **`Rank 253 / same-venue conversion / parity reversal`**。
   - 证据：`research/optimization_loop/2026-03-30_1149_rank253_samevenue_conversion_reversal_intake_keep_p1.md` 已明确写成 fresh intake first verdict，并已写回 state。

3. **上一条 fresh intake 是否值得那唯一一次 follow-up？**
   - 结论：**值得，而且当前必须占用 survivor 槽。**
   - 证据：`Rank 253` 不是泛 box spread、cross-venue arbitrage 或旧 options no-arb 家族换壳；它的主语已锁定为 `carry-adjusted same-venue conversion/reversal × parity gap hurdle`，且最小 decisive blocker 也已经被压窄到唯一问题：在 `Deribit BTC` 最近 `7~14` 天公开 snapshot 上，统一 inverse premium numeraire 并叠加 `quote age / top-of-book size / 6~20bps friction ladder` 后，`1m/3m` 持有里是否仍留下可重复、成本后为正的 executable parity pocket。按 policy，这正是 survivor 的那唯一一次诚实 follow-up，不应被新 intake 覆盖。

4. **当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？**
   - 结论：**不存在。**
   - 证据：`BOT2_BOT3_STATE.md` 当前 `Active P2 slot.current_target: none`。上一条 P2 对象 `Rank 235` 已在 `research/optimization_loop/2026-03-29_1230_rank235_p2_exit_rescope_p1_honesty_gap.md` 完成 `one-time P2 -> P1 re-scope`，当前没有合法 active P2 需要做 `P3 / P1 / P0` 出口裁决，也不存在 bot2 需要兜底直推 `P3` 的对象。

## rank / 前排合法性检查

- `Paper launch queue`: 无当前 queue 头，不涉及 rank 缺失
- `Surviving candidate`: `Rank 253`，已有正式 rank
- `Active P2`: none
- 结论：**本轮无需补 rank。**

## repo / recent evidence quick notes

- `git status --short` 仍显示大量未跟踪产物；本轮只把它视作环境噪音，不据此反向改 policy。
- 最近 optimization 证据链显示：
  - `2026-03-30_1143_rank252_survivor_followup_background_p0.md` 已把 `Rank 252` survivor 诚实收口回 `background/P0`
  - `2026-03-30_1149_rank253_samevenue_conversion_reversal_intake_keep_p1.md` 已把 `Rank 253` 写成新的 `keep_P1` fresh intake，并占据 survivor 槽
  - `2026-03-30_1220_trend_pullback_correlation_shell_cycle_item_blocked_duplicate_rank242.md` 已确认上一轮 pending trend 项只是 `Rank 242` 重复，不是合法新 intake
- 最新可补的具体新 intake 证据来自：
  - `2026-03-30_1212_bb-compression-bottomquartile-breakout-alpha.md`：更像一个值得诚实首判的 breakout raw alpha 候选，但当前公开 proxy 也提示它很可能只剩 participation gate / vote leg 价值，适合前排 first verdict、但不应跳过 survivor
  - `2026-03-30_1133_multiquote-conflict-routing-raw-alpha.md`：same-underlier multiquote 的新增层不在 pair spread 本体，而在 `multi-spread conflict routing × no-idle-capital` allocator，属于比旧 pair-zscore 更像独立 fresh intake 的新对象
  - `2026-03-30_0354_vpin-jump-sign-continuation-alpha.md` 虽仍是可讨论题材，但其主语已在 `2026-03-30_0505_rank247_vpin_jump_sign_continuation_intake_keep_p1.md` 获得正式 rank，不能再作为新的 fresh intake 重新排入

## 本轮 cycle_plan 重写结论

按 policy 默认顺序，当前合法动作排序为：
1. `P3 handoff`：无待接线 queue 头
2. `P2 admission/promote/park`：无 Active P2
3. `P1 唯一一次诚实检查`：必须先做 `Rank 253` survivor follow-up
4. 在 survivor 已诚实排入前部后，再用剩余预算补具体 fresh intake

因此本轮将 `cycle_plan` 改写为：
1. `Rank 253 / same-venue conversion / parity reversal` survivor follow-up（pending）
2. `bottom-quartile BB compression breakout` fresh intake（pending）
3. `multi-spread conflict routing × no-idle-capital` fresh intake（pending）
4. `bottom-quartile BB compression breakout` conditional收口位（pending；仅在前面已诚实推进后使用）

## 为什么这样排

- `Rank 253` 当前是唯一合法 survivor，按 policy 享有前排锁定权，不能被新的 `keep_P1` 候选覆盖。
- `Paper launch queue` 与 `Active P2` 都为空，本轮不存在 bot2 必须兜底直推 `P3` 的对象。
- 上一轮遗留的 `trend continuation × pullback re-entry × correlation-budget shell` 已被证实是 `Rank 242` 的重复，不再保留为当前轮 intake 对象。
- `high-VPIN × realized jump-sign continuation` 也不再适合作为新的 intake 名额，因为该主语已具 durable identity：`Rank 247`；继续排会造成 runtime identity 污染。
- 新的 intake 名额优先给真正新且具体的对象：
  - `bottom-quartile BB compression breakout`
  - `multi-spread conflict routing × no-idle-capital`

## writeback

- 已更新：`docs/BOT2_BOT3_STATE.md`
- 未改写：policy / brief / operating card / auto loop / cron prompt
- 未把 background pool 旧候选自动拉回前排
- 本轮没有对象达到 bot2 兜底直推 `P3 / Paper launch queue` 的门槛，因此无新增 P3 handoff 写回
