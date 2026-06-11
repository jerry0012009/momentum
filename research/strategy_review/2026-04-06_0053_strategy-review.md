# Strategy Review — 2026-04-06 00:53 UTC

本轮严格依据：
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`

并复核：
- repo 状态：`git -C /root/clawd/jerry/momentum status --short`
- 最近 optimization：
  - `research/optimization_loop/2026-04-06_0052_rolling_max_fresh_intake_blocked_by_survivor_lock.md`
  - `research/optimization_loop/2026-04-06_0026_rank344_winner_only_loser_short_veto_first_verdict_keep_p1.md`
  - `research/optimization_loop/2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md`
  - `research/optimization_loop/2026-04-05_2328_rank343_survivor_followup_no_child_transfer_edge_background_p0.md`
- 最近 strategy review：
  - `research/strategy_review/2026-04-06_0006_strategy-review.md`
  - `research/strategy_review/2026-04-05_2250_strategy-review.md`

## 只回答 4 个问题

### 1) `Paper launch queue` 是否非空？
- **否，当前为空。**
- `Paper launch queue.current_target = none`。
- 最近的 queue 头对象 `Rank 342 / same-chain cross-DEX price-gap close` 已在 `2026-04-06_0016_rank342_p3_launch_wiring_connected_runner_live.md` 中完成 dedicated runner、scheduler 与首跑验证，并正式写回 `connected_runner_live`。
- 因此当前不存在待接线的 `P3` 头对象，也不存在 bot2 需要代替 bot3 再次推进的遗漏 `P3`。

### 2) 本轮 `fresh intake` 是什么？
- **本轮 fresh intake 仍是** `research/quant_digests/2026-04-05_1919_winneronly-losershort-veto-xs-alpha.md`。
- 它已在 `2026-04-06_0026_rank344_winner_only_loser_short_veto_first_verdict_keep_p1.md` 完成 first verdict，并获得正式编号 `Rank 344`。
- 但按 policy，上一条 fresh intake 一旦首判 `keep_P1`，其唯一 survivor follow-up 在收口前拥有前排锁定权；因此系统当前仍围绕 `Rank 344` 的 survivor 收口组织前排，而不是切到新的 `rolling-MAX`。

### 3) 上一条 fresh intake 是否值得那唯一一次 follow-up？
- **值得，而且当前就该执行。**
- 这里的“上一条 fresh intake”是刚完成首判并进入 `keep_P1` 的 `Rank 344 / winner-only × loser-short veto`。
- 现有 evidence 已清楚表明：
  - 它的独立主语是 `winner-only XS continuation`，不是 textbook `winner-minus-loser`；
  - `loser-short veto` 不是装饰，而是对象定义的一部分；
  - 真正剩下的唯一前排问题，是去掉市场 beta、加上 desk 成本口径后，这条 winner-only 线是否仍保留可迁移增益。
- 这正好符合 policy 对 survivor 的定义：**值得一次最小但 decisive 的诚实 follow-up**。

### 4) 当前是否存在明确 `Active P2`？若有，它离 `P3 / P1 / P0` 中哪个出口最近？
- **不存在。**
- `Active P2 slot.current_target = none`。
- 最近唯一明确的 `Active P2` 是 `Rank 342`，它已经在上一轮 desk review 中被确认足够进入 paper trade，并已完成 `P2 -> P3 -> connected_runner_live` 的整条闭环；当前不存在需要 bot2 兜底升 `P3` 的滞留 P2。

## Rank 完整性检查
- `Paper launch queue.current_target = none`
- `Surviving candidate slot.current_target = Rank 344 / winner-only × loser-short veto`
- `Active P2 slot.current_target = none`
- 当前所有前排对象都已有正式 `Rank`；不存在达到 `keep_P1 / P2 / P3` 但仍无 rank 的违规状态，本轮无需补号。

## P2 -> P3 兜底裁判检查
- 本轮没有滞留 `Active P2`。
- 最近 desk review 已把 `Rank 342` 从 `P2` 明确推到 `P3`，且 bot3 已完成 launch wiring 写回 `connected_runner_live`；因此当前不存在“已经够格 paper launch 但 bot3 尚未升级”的漏判对象。

## cycle_plan 重写结果
按 policy 默认顺序：`P3 handoff > P2 admission/promote/park > P1 唯一一次诚实检查 > fresh intake > P0`。

当前合法前排链条为：
- `P3`: none
- `P2`: none
- `P1 survivor`: `Rank 344 / winner-only × loser-short veto`
- 因此本轮必须先排 `Rank 344` 的 survivor 唯一 follow-up，然后才恢复新的 fresh intake。

已将 `docs/BOT2_BOT3_STATE.md` 的 `cycle_plan` 重写为：
1. `Rank 344 / winner-only × loser-short veto`：执行 survivor 唯一 follow-up，直接回答去 beta/去成本后是否足以升 `P2`
2. `research/quant_digests/2026-04-05_2151_rolling-max-spike-persistence-xs-alpha.md`：作为 survivor 收口后的首条 fresh intake
3. `research/quant_digests/2026-04-05_2318_tuning-news-sentiment-macro-impulse-alpha.md`：下一条具体 fresh intake
4. `research/quant_digests/2026-04-06_0040_sg-lob-imbalance-continuation-alpha.md`：conditional fresh intake

### 为什么这么排
- `Rank 342` 已经完成 `connected_runner_live`，所以 `P3` 前排已收口，不该再占默认轮次。
- 当前不存在 `Active P2`，所以前排最高优先级自然落到 `Rank 344` 的 survivor 唯一 follow-up。
- `rolling-MAX` 在 `2026-04-06_0052` 已被明确记为 survivor lock 下的非法时机 intake；只有在 `Rank 344` 收口后才重新合法。
- 其后补入的 `macro impulse` 与 `SG LOB imbalance` 都是最近新 digest，属于 policy 允许的具体 intake 来源，不涉及把 background pool 老对象拉回前排。

## 本轮一句话
`Rank 342` 已经彻底离开待接线前排；当前默认主动作不是再谈 P3，而是先把 `Rank 344` 的 survivor 唯一 follow-up 诚实收口，然后才恢复新的 fresh intake。